from __future__ import annotations

import re
from pathlib import Path
import yaml

LEXICON_DIR = Path("linguistic_rules/lexicon")

# Map filename -> category + prefix
FILE_MAP = {
    "verbs.yaml": ("verb", "V"),
    "nouns.yaml": ("noun", "N"),
    "adjectives.yaml": ("adjective", "ADJ"),
    "adverbs.yaml": ("adverb", "ADV"),
    "time_numbers.yaml": ("time_numbers", "T"),
    "numbers_time.yaml": ("time_numbers", "T"),  # if an older name exists
}

ARTICLES = {"der", "die", "das"}


def safe_load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def safe_dump_yaml(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


def parse_gender_and_lemma(text: str) -> tuple[str | None, str | None]:
    """
    For noun entries like 'der Hund' -> ('der', 'Hund')
    Otherwise returns (None, None)
    """
    t = (text or "").strip()
    parts = t.split()
    if len(parts) >= 2 and parts[0] in ARTICLES:
        gender = parts[0]
        lemma = " ".join(parts[1:])  # keep multiword noun lemmas intact
        return gender, lemma
    return None, None


def normalize_sources(item: dict) -> list[dict]:
    """
    Ensure sources is always a list of {ppt, slide}
    """
    sources = item.get("sources", [])
    if not isinstance(sources, list):
        return []
    out = []
    for s in sources:
        if isinstance(s, dict) and "ppt" in s and "slide" in s:
            out.append({"ppt": s["ppt"], "slide": s["slide"]})
    return out


def migrate_one_file(path: Path) -> None:
    name = path.name
    if name not in FILE_MAP:
        return

    category, prefix = FILE_MAP[name]
    old = safe_load_yaml(path)

    # Expect old format:
    # schema_version: '0.1'
    # source: pptx_extraction
    # category: verb
    # items: - text: ...
    items = old.get("items", [])
    if not isinstance(items, list):
        items = []

    # Deterministic ordering so lex_id stays stable across reruns:
    # sort by text, then by first source ppt/slide if present
    def sort_key(it: dict):
        txt = (it.get("text") or "").strip()
        srcs = normalize_sources(it)
        if srcs:
            first = srcs[0]
            return (txt.lower(), str(first.get("ppt")), int(first.get("slide", 0)))
        return (txt.lower(), "", 0)

    items_sorted = sorted(items, key=sort_key)

    new_items = []
    counter = 1
    for it in items_sorted:
        text = (it.get("text") or "").strip()
        if not text:
            continue

        lex_id = f"LEX-{prefix}-A1-{counter:04d}"
        counter += 1

        entry = {
            "lex_id": lex_id,
            "text": text,
            "pos": category,
            "lemma": None,
            "notes": None,
            "sources": normalize_sources(it),
        }

        # Noun enrichment if applicable
        if category == "noun":
            gender, lemma = parse_gender_and_lemma(text)
            entry["gender"] = gender
            entry["lemma"] = lemma if lemma else None
            entry["plural"] = None  # keep null unless you explicitly add later

        # Verb lemma default: if it’s one token, assume it’s already infinitive
        if category == "verb":
            entry["lemma"] = text if (" " not in text) else None

        # Adjective/adverb/time_numbers lemma: use raw text as lemma if single token
        if category in {"adjective", "adverb", "time_numbers"}:
            entry["lemma"] = text if (" " not in text) else None

        new_items.append(entry)

    payload = {
        "schema_version": "0.2",
        "rule_type": "lexicon",
        "language": "de",
        "cefr_level": "A1",
        "category": category,
        "source": old.get("source", "pptx_extraction"),
        "items": new_items,
    }

    # Backup original once
    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    safe_dump_yaml(path, payload)
    print(f"Migrated: {path}  (items: {len(new_items)})  backup: {backup.name}")


def main():
    if not LEXICON_DIR.exists():
        raise SystemExit("Missing linguistic_rules/lexicon directory.")

    for p in sorted(LEXICON_DIR.glob("*.yaml")):
        migrate_one_file(p)

    print("Done. Review with: git diff")


if __name__ == "__main__":
    main()
