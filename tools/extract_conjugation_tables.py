from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple, Iterable

import yaml

# Canonical order for output.
# NOTE: we split sie into sie_sg and sie_pl to avoid collisions.
PRONOUN_ORDER = ["ich", "du", "Sie", "er", "sie_sg", "es", "wir", "ihr", "sie_pl"]
PRONOUN_SET = {"ich", "du", "Sie", "er", "sie", "es", "wir", "ihr"}  # raw pronouns we detect

# Match: "ich spreche", "du sprichst", "Sie sprechen", "er ist", "sie sprechen"
RE_PRONOUN_PAIR = re.compile(r"^(ich|du|er|sie|es|wir|ihr|Sie)\s+(.+?)\s*$")

IRREGULAR_MARKERS = {
    "bin", "bist", "ist", "sind", "seid",
    "habe", "hast", "hat", "haben",
    "werde", "wirst", "wird", "werden"
}


def read_items_csv(path: Path) -> List[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def normalize_pronoun(p: str) -> str:
    return "Sie" if p == "Sie" else p.lower()


def looks_like_pronoun_line(text: str) -> bool:
    return bool(RE_PRONOUN_PAIR.match((text or "").strip()))


def group_by_ppt_slide(rows: List[dict]) -> Dict[Tuple[str, str], List[str]]:
    grouped: Dict[Tuple[str, str], List[str]] = {}
    for r in rows:
        ppt = r.get("ppt_file", "")
        slide = r.get("slide_number", "")
        t = (r.get("norm_text") or "").strip()
        if not ppt or not slide or not t:
            continue
        grouped.setdefault((ppt, slide), []).append(t)
    return grouped


def extract_tables_from_group(lines: List[str]) -> List[Dict[str, str]]:
    """
    Within a slide, find clusters of pronoun+form lines.
    If a cluster has >= 4 unique pronouns, treat it as a conjugation table.

    Important: "sie" may appear twice in a table (she vs they). We will store
    those as sie_sg and sie_pl based on simple heuristics.
    """
    tables: List[Dict[str, str]] = []
    current: Dict[str, str] = {}

    def flush():
        nonlocal current
        if len(current) >= 4:
            tables.append(current)
        current = {}

    for line in lines:
        m = RE_PRONOUN_PAIR.match(line.strip())
        if not m:
            flush()
            continue

        p_raw, form = m.group(1), m.group(2).strip()
        p = normalize_pronoun(p_raw)

        if p != "sie":
            current[p] = form
            continue

        # ---- Handle "sie" ambiguity (sg vs pl) ----
        # If "sie" shows up twice, we must keep both.
        # Heuristic:
        # - If form matches "er" (often ends with -t), treat as sie_sg
        # - Otherwise treat as sie_pl
        er_form = (current.get("er") or "").strip().lower()
        form_low = form.lower()

        if "sie_sg" not in current and (er_form and form_low == er_form or form_low.endswith("t")):
            current["sie_sg"] = form
        elif "sie_pl" not in current:
            current["sie_pl"] = form
        else:
            # If both exist, keep the latest as sie_pl (safe default)
            current["sie_pl"] = form

    flush()

    # Deduplicate exact tables
    uniq: List[Dict[str, str]] = []
    seen = set()
    for t in tables:
        key = tuple(sorted(t.items()))
        if key not in seen:
            seen.add(key)
            uniq.append(t)
    return uniq


def ordered_forms(table: Dict[str, str]) -> Dict[str, str]:
    """
    Return forms in a consistent order. Keeps any extra keys at the end.
    """
    out: Dict[str, str] = {}
    for p in PRONOUN_ORDER:
        if p in table:
            out[p] = table[p]
    # Append any unexpected keys (rare)
    for k in table.keys():
        if k not in out:
            out[k] = table[k]
    return out


from typing import Dict

def guess_lemma(table: Dict[str, str]) -> str:
    """
    Lemma guess (A1-focused, practical):
    1) Normalize ultra-common irregulars: sein, haben, werden
    2) Prefer 'wir' form if single token (often infinitive-like)
    3) Else prefer 'Sie' form if single token (also often infinitive-like)
    4) Else prefer 'ich'
    5) Else any available form
    """
    # normalize super-common irregulars
    forms = {(v or "").strip().lower() for v in table.values() if isinstance(v, str) and v.strip()}
    if {"bin", "bist", "ist", "sind", "seid"} & forms:
        return "sein"
    if {"habe", "hast", "hat", "haben"} & forms:
        return "haben"
    if {"werde", "wirst", "wird", "werden"} & forms:
        return "werden"

    wir = (table.get("wir") or "").strip()
    if wir and " " not in wir:
        return wir

    sie_form = (table.get("Sie") or "").strip()
    if sie_form and " " not in sie_form:
        return sie_form

    ich = (table.get("ich") or "").strip()
    if ich:
        return ich

    # last resort: first non-empty string
    for v in table.values():
        if isinstance(v, str) and v.strip():
            return v.strip()

    return ""


def detect_pattern(table: Dict[str, str]) -> str:
    """
    Label: regular / stem_change / irregular / unknown

    - If table contains markers for sein/haben/werden -> irregular
    - Else if du/er stem differs from wir (compare first 4 chars) -> stem_change
    - Else regular
    """
    forms = {v.lower() for v in table.values() if v}
    if forms & IRREGULAR_MARKERS:
        return "irregular"

    wir = (table.get("wir") or "").lower()
    du = (table.get("du") or "").lower()
    er = (table.get("er") or "").lower()

    if not wir:
        return "unknown"

    wir4 = wir[:4]
    if du and du[:4] != wir4:
        return "stem_change"
    if er and er[:4] != wir4:
        return "stem_change"

    # Umlaut trigger (schlafen -> schläfst, laufen -> läufst, etc.)
    if any(ch in (du + er) for ch in "äöü") and not any(ch in wir for ch in "äöü"):
        return "stem_change"

    return "regular"


def main():
    items_csv = Path("docs/ppt_extracted/items.csv")
    if not items_csv.exists():
        raise SystemExit("Missing docs/ppt_extracted/items.csv — run extraction first.")

    rows = read_items_csv(items_csv)
    grouped = group_by_ppt_slide(rows)

    out_tables: List[dict] = []

    for (ppt, slide), lines in grouped.items():
        pronoun_lines = [ln for ln in lines if looks_like_pronoun_line(ln)]
        if len(pronoun_lines) < 4:
            continue

        tables = extract_tables_from_group(pronoun_lines)
        for t in tables:
            lemma_guess = guess_lemma(t)
            pattern = detect_pattern(t)

            out_tables.append({
                "table_id": f"{ppt}__slide{slide}",
                "lemma_guess": lemma_guess,
                "pattern_guess": pattern,
                "forms": ordered_forms(t),
                "source": {"ppt": ppt, "slide": int(slide)},
            })

    payload = {
        "schema_version": "0.1",
        "rule_type": "morphology",
        "category": "conjugation_tables",
        "language": "de",
        "cefr_level": "A1",
        "tables": out_tables,
    }

    out_path = Path("linguistic_rules/morphology/conjugation_tables.yaml")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)

    print(f"Wrote: {out_path} ({len(out_tables)} tables)")


if __name__ == "__main__":
    main()