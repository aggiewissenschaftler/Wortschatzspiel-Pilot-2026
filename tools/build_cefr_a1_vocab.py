#!/usr/bin/env python3
"""
Build CEFR A1 vocabulary YAML by merging:
  (A) an external CEFR A1 list (CSV/TSV) as source-of-truth
  (B) your extracted course wordbank_dedup.csv as validation/coverage

Outputs:
  - linguistic_rules/vocab/cefr_a1.yaml
  - docs/ppt_extracted/cefr_a1_merged.csv  (debug/inspection)

Assumptions:
  - wordbank_dedup.csv has columns: ppt_file, slide_number, token, norm, category, lemma, source_text
  - conjugation tables exist at: linguistic_rules/morphology/conjugation_tables.yaml (optional)
  - spaCy model de_core_news_lg can be used optionally to fill missing lemmas/categories

CEFR A1 input format (CSV/TSV):
  Must contain at least ONE of these columns:
    - lemma (preferred) or word or token or text
  Optional columns:
    - category (noun/verb/adjective/etc.)
    - gender (Masc/Fem/Neut)
    - notes

Usage example:
  python tools/build_cefr_a1_vocab.py \
    --cefr docs/cefr/goethe_a1_vocab.csv \
    --wordbank docs/ppt_extracted/wordbank_dedup.csv \
    --out-yaml linguistic_rules/vocab/cefr_a1.yaml \
    --out-csv docs/ppt_extracted/cefr_a1_merged.csv \
    --use-spacy

"""

from __future__ import annotations

import argparse
import csv
import logging
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

try:
    import yaml
except ImportError as e:
    raise SystemExit("Missing dependency 'pyyaml'. Install with: pip install pyyaml") from e


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("build_cefr_a1_vocab")


# -----------------------------------------------------------------------------
# Repo-default paths
# -----------------------------------------------------------------------------
DEFAULT_CONJ_TABLES = Path("linguistic_rules/morphology/conjugation_tables.yaml")


# -----------------------------------------------------------------------------
# Normalization & heuristics
# -----------------------------------------------------------------------------
TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿÄÖÜäöüß]+(?:[-'][A-Za-zÀ-ÖØ-öø-ÿÄÖÜäöüß]+)?", re.UNICODE)

ARTICLES = {"der", "die", "das", "ein", "eine", "einer", "einen", "einem", "eines"}
NEGATION_DETERMINERS = {"kein", "keine", "keiner", "keinen", "keinem", "keines"}
QUESTION_WORDS = {"wer", "was", "wo", "wann", "warum", "wie", "woher", "wohin", "wen", "wem", "wessen"}
COMMON_PREPS = {"in", "an", "auf", "unter", "über", "vor", "hinter", "neben", "zwischen", "bei", "mit", "nach", "zu", "von", "aus", "für", "ohne", "gegen", "um"}
COMMON_CONJ = {"und", "oder", "aber", "denn", "sondern", "weil", "dass", "wenn", "als", "ob", "während"}
COMMON_PARTICLES = {"nicht", "doch", "ja", "mal", "auch", "schon", "nur", "eben", "halt", "sehr", "ganz"}

# Minimal category mapping standard (keep it stable)
CANON_CATS = {
    "article", "noun", "verb", "verb_form", "adjective", "adverb",
    "pronoun", "preposition", "conjunction", "particle", "interjection",
    "numeral", "proper noun", "noun_phrase", "other"
}


def norm_key(s: str) -> str:
    return (s or "").strip().lower()


def looks_like_noun(surface: str) -> bool:
    # your wordbank is usually lowercase, but keep this for when inputs are mixed-case
    return bool(surface) and surface[:1].isupper()


def guess_category_basic(token: str) -> str:
    tk = norm_key(token)
    if tk in ARTICLES or tk in NEGATION_DETERMINERS:
        return "article"
    if tk in QUESTION_WORDS:
        return "pronoun"
    if tk in COMMON_PREPS:
        return "preposition"
    if tk in COMMON_CONJ:
        return "conjunction"
    if tk in COMMON_PARTICLES:
        return "particle"
    return "other"


# -----------------------------------------------------------------------------
# Data models
# -----------------------------------------------------------------------------
@dataclass
class VocabItem:
    lemma: str
    category: str
    gender: str = ""
    notes: str = ""
    cefr: str = "A1"
    seen_in_course: bool = False
    course_examples: str = ""  # short debug string (not full text)
    source: str = "cefr_a1"

    def key(self) -> Tuple[str, str, str]:
        # stable merge identity
        return (norm_key(self.lemma), norm_key(self.category), norm_key(self.gender))


# -----------------------------------------------------------------------------
# Loaders
# -----------------------------------------------------------------------------
def detect_delimiter(path: Path) -> str:
    # simple sniff: if tabs are common, treat as TSV
    sample = path.read_text(encoding="utf-8", errors="replace")[:4000]
    if sample.count("\t") > sample.count(","):
        return "\t"
    return ","


def load_cefr_list(cefr_path: Path) -> List[VocabItem]:
    if not cefr_path.exists():
        raise FileNotFoundError(f"CEFR list not found: {cefr_path}")

    # NEW: allow YAML CEFR lists (source-of-truth) as well as CSV
    if cefr_path.suffix.lower() in [".yaml", ".yml"]:
        data = yaml.safe_load(cefr_path.read_text(encoding="utf-8")) or {}
        raw_items = data.get("items", [])
        items: List[VocabItem] = []

        for it in raw_items:
            if not isinstance(it, dict):
                continue
            raw_lemma = (it.get("lemma") or it.get("text") or it.get("word") or "").strip()
            if not raw_lemma:
                continue

            raw_cat = (it.get("category") or it.get("pos") or it.get("type") or "").strip()
            raw_gender = (it.get("gender") or it.get("genus") or "").strip()
            raw_notes = (it.get("notes") or it.get("note") or "").strip()

            cat = norm_key(raw_cat)
            if not cat:
                cat = guess_category_basic(raw_lemma)

            cat_map = {
                "det": "article",
                "artikel": "article",
                "n": "noun",
                "noun": "noun",
                "subst": "noun",
                "verb": "verb",
                "v": "verb",
                "adj": "adjective",
                "adjektiv": "adjective",
                "adv": "adverb",
                "pron": "pronoun",
                "prep": "preposition",
                "konj": "conjunction",
                "part": "particle",
                "num": "numeral",
            }
            cat = cat_map.get(cat, cat)
            if cat not in CANON_CATS:
                cat = "other"

            items.append(VocabItem(
                lemma=raw_lemma,
                category=cat,
                gender=raw_gender,
                notes=raw_notes,
                cefr="A1",
                seen_in_course=False,
                source="cefr_a1",
            ))

        if not items:
            raise ValueError(f"CEFR YAML produced 0 items. Check file format: {cefr_path}")

        log.info("Loaded CEFR items (YAML): %d", len(items))
        return items




    delim = detect_delimiter(cefr_path)
    items: List[VocabItem] = []

    with cefr_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        if not reader.fieldnames:
            raise ValueError(f"CEFR file has no headers: {cefr_path}")

        # acceptable lemma columns
        lemma_cols = ["lemma", "word", "token", "text"]
        cat_cols = ["category", "pos", "type"]
        gender_cols = ["gender", "genus"]
        notes_cols = ["notes", "note", "comment", "comments"]

        for row in reader:
            raw_lemma = ""
            for c in lemma_cols:
                if c in row and (row[c] or "").strip():
                    raw_lemma = row[c].strip()
                    break

            if not raw_lemma:
                continue

            raw_cat = ""
            for c in cat_cols:
                if c in row and (row[c] or "").strip():
                    raw_cat = row[c].strip()
                    break

            raw_gender = ""
            for c in gender_cols:
                if c in row and (row[c] or "").strip():
                    raw_gender = row[c].strip()
                    break

            raw_notes = ""
            for c in notes_cols:
                if c in row and (row[c] or "").strip():
                    raw_notes = row[c].strip()
                    break

            cat = norm_key(raw_cat)
            if not cat:
                # fall back to heuristic
                cat = guess_category_basic(raw_lemma)

            # normalize category labels lightly
            cat_map = {
                "det": "article",
                "artikel": "article",
                "n": "noun",
                "noun": "noun",
                "subst": "noun",
                "verb": "verb",
                "v": "verb",
                "adj": "adjective",
                "adjektiv": "adjective",
                "adv": "adverb",
                "pron": "pronoun",
                "prep": "preposition",
                "konj": "conjunction",
                "part": "particle",
                "num": "numeral",
            }
            cat = cat_map.get(cat, cat)
            if cat not in CANON_CATS:
                # keep it but avoid chaos
                cat = "other"

            items.append(VocabItem(
                lemma=raw_lemma.strip(),
                category=cat,
                gender=raw_gender.strip(),
                notes=raw_notes.strip(),
                cefr="A1",
                seen_in_course=False,
                source="cefr_a1",
            ))

    if not items:
        raise ValueError(f"CEFR list produced 0 items. Check file format: {cefr_path}")

    log.info("Loaded CEFR items: %d", len(items))
    return items


def load_wordbank(wordbank_path: Path) -> List[Dict[str, str]]:
    if not wordbank_path.exists():
        raise FileNotFoundError(f"wordbank_dedup.csv not found: {wordbank_path}")

    rows: List[Dict[str, str]] = []
    with wordbank_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Wordbank file has no headers: {wordbank_path}")
        for row in reader:
            rows.append({k: (v or "") for k, v in row.items()})

    if not rows:
        raise ValueError(f"Wordbank produced 0 rows: {wordbank_path}")

    log.info("Loaded wordbank rows: %d", len(rows))
    return rows


def load_conjugation_form_map(conj_tables_path: Path) -> Dict[str, str]:
    """
    Build inflected_form(lower) -> lemma(lower) map
    Expected YAML structure: list of tables with lemma + rows, or any mapping that includes form/text.
    """
    if not conj_tables_path.exists():
        log.warning("Conjugation tables not found: %s (skipping)", conj_tables_path)
        return {}

    data = yaml.safe_load(conj_tables_path.read_text(encoding="utf-8")) or {}
    form2lemma: Dict[str, str] = {}

    # Try a few likely shapes
    # Shape A: {"tables":[{"lemma":"sein","rows":[{"form":"bin"}, ...]}]}
    tables = data.get("tables") if isinstance(data, dict) else None
    if isinstance(tables, list):
        for t in tables:
            lemma = norm_key((t or {}).get("lemma", ""))
            rows = (t or {}).get("rows", [])
            if not lemma or not isinstance(rows, list):
                continue
            for r in rows:
                form = (r or {}).get("form") or (r or {}).get("text") or ""
                form = norm_key(form)
                if form:
                    form2lemma[form] = lemma

    # Shape B: list of tables directly
    if not form2lemma and isinstance(data, list):
        for t in data:
            lemma = norm_key((t or {}).get("lemma", ""))
            rows = (t or {}).get("rows", [])
            if not lemma or not isinstance(rows, list):
                continue
            for r in rows:
                form = norm_key((r or {}).get("form") or (r or {}).get("text") or "")
                if form:
                    form2lemma[form] = lemma

    log.info("Loaded conjugation form→lemma entries: %d", len(form2lemma))
    return form2lemma


# -----------------------------------------------------------------------------
# Lemma/category enrichment
# -----------------------------------------------------------------------------
def maybe_load_spacy(use_spacy: bool, model: str) -> Optional[object]:
    if not use_spacy:
        return None
    try:
        import spacy  # local import on purpose
        nlp = spacy.load(model)
        log.info("Loaded spaCy model: %s", model)
        return nlp
    except Exception as e:
        log.warning("spaCy unavailable (%s). Continuing without spaCy.", e)
        return None


def enrich_wordbank_rows(
    rows: List[Dict[str, str]],
    form2lemma: Dict[str, str],
    nlp: Optional[object],
) -> List[Dict[str, str]]:
    """
    Ensures each row has a best-available lemma and sane category.
    Priority for lemma:
      1) existing lemma if non-empty
      2) conjugation tables (form2lemma) for verb_form-like tokens
      3) spaCy lemma if available
      4) fallback: norm itself
    """
    out: List[Dict[str, str]] = []

    for r in rows:
        token = r.get("token", "")
        norm = r.get("norm", "") or norm_key(token)
        cat = norm_key(r.get("category", "")) or "other"
        lemma = r.get("lemma", "").strip()

        # normalize categories a bit
        if cat == "det":
            cat = "article"
        if cat not in CANON_CATS:
            cat = "other"

        # lemma: best-available logic
        if not lemma:
            # conjugation override first
            if norm_key(norm) in form2lemma:
                lemma = form2lemma[norm_key(norm)]
                if cat == "other":
                    cat = "verb_form"
            elif nlp is not None:
                doc = nlp(token)
                if doc and len(doc) > 0:
                    lemma = (doc[0].lemma_ or "").strip()
                    if not cat or cat == "other":
                        pos = doc[0].pos_
                        # minimal POS→category
                        pos_map = {
                            "DET": "article",
                            "NOUN": "noun",
                            "PROPN": "proper noun",
                            "VERB": "verb",
                            "AUX": "verb",
                            "ADJ": "adjective",
                            "ADV": "adverb",
                            "PRON": "pronoun",
                            "ADP": "preposition",
                            "CCONJ": "conjunction",
                            "SCONJ": "conjunction",
                            "PART": "particle",
                            "NUM": "numeral",
                            "INTJ": "interjection",
                        }
                        cat = pos_map.get(pos, cat)
            if not lemma:
                lemma = norm_key(norm)

        r2 = dict(r)
        r2["norm"] = norm_key(norm)
        r2["category"] = cat
        r2["lemma"] = lemma
        out.append(r2)

    return out


# -----------------------------------------------------------------------------
# Merge logic
# -----------------------------------------------------------------------------
def merge_cefr_with_course(
    cefr_items: List[VocabItem],
    course_rows: List[Dict[str, str]],
) -> Dict[Tuple[str, str, str], VocabItem]:
    """
    CEFR items are source-of-truth. Course rows add flags + examples.
    We map course tokens to CEFR by matching lemma (primary) or norm (fallback).
    """
    merged: Dict[Tuple[str, str, str], VocabItem] = {}

    # seed with CEFR
    for it in cefr_items:
        merged[it.key()] = it

    # build quick lookup for CEFR by lemma only (category-agnostic fallback)
    cefr_by_lemma: Dict[str, List[VocabItem]] = {}
    for it in cefr_items:
        cefr_by_lemma.setdefault(norm_key(it.lemma), []).append(it)

    for r in course_rows:
        norm = norm_key(r.get("norm", ""))
        lemma = norm_key(r.get("lemma", "")) or norm
        cat = norm_key(r.get("category", "")) or "other"
        example = (r.get("source_text") or r.get("token") or "")[:120].replace("\n", " ").strip()

        # try: match CEFR by lemma
        candidates = cefr_by_lemma.get(lemma, [])
        chosen: Optional[VocabItem] = None

        # prefer candidate whose category matches
        for c in candidates:
            if norm_key(c.category) == cat:
                chosen = c
                break
        # else pick the first candidate if lemma matches at all
        if not chosen and candidates:
            chosen = candidates[0]

        # if no CEFR match, optionally create a "local extension" entry
        if not chosen:
            # you can turn this off by filtering later; keeping it is useful
            chosen = VocabItem(
                lemma=lemma,
                category=cat if cat in CANON_CATS else "other",
                gender="",
                notes="",
                cefr="A1",
                seen_in_course=True,
                course_examples=example,
                source="local_extension",
            )
            merged[chosen.key()] = chosen
        else:
            # mark existing CEFR entry as seen
            k = chosen.key()
            merged[k].seen_in_course = True
            if not merged[k].course_examples and example:
                merged[k].course_examples = example

    log.info("Merged vocabulary entries: %d", len(merged))
    return merged


# -----------------------------------------------------------------------------
# Writers
# -----------------------------------------------------------------------------
def write_yaml_vocab(out_yaml: Path, merged: Dict[Tuple[str, str, str], VocabItem]) -> None:
    out_yaml.parent.mkdir(parents=True, exist_ok=True)

    # stable sorting
    items = sorted(merged.values(), key=lambda x: (norm_key(x.category), norm_key(x.lemma), norm_key(x.gender)))

    payload = {
        "schema": "vocab_schema_v1",
        "cefr_level": "A1",
        "items": [
            {
                "lemma": it.lemma,
                "category": it.category,
                "gender": it.gender or "",
                "notes": it.notes or "",
                "seen_in_course": bool(it.seen_in_course),
                "course_examples": it.course_examples or "",
                "source": it.source,
            }
            for it in items
        ],
    }

    out_yaml.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
    log.info("Wrote YAML: %s", out_yaml)


def write_debug_csv(out_csv: Path, merged: Dict[Tuple[str, str, str], VocabItem]) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    items = sorted(merged.values(), key=lambda x: (norm_key(x.category), norm_key(x.lemma), norm_key(x.gender)))

    fieldnames = ["lemma", "category", "gender", "cefr", "seen_in_course", "source", "notes", "course_examples"]

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for it in items:
            row = {
                "lemma": it.lemma,
                "category": it.category,
                "gender": it.gender,
                "cefr": it.cefr,
                "seen_in_course": "true" if it.seen_in_course else "false",
                "source": it.source,
                "notes": it.notes,
                "course_examples": it.course_examples,
            }
            w.writerow(row)

    log.info("Wrote debug CSV: %s", out_csv)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Build CEFR A1 vocab YAML by merging CEFR list + course wordbank.")
    ap.add_argument("--cefr", required=True, help="Path to CEFR A1 list (CSV/TSV). Must contain lemma/word/token/text column.")
    ap.add_argument("--wordbank", default="docs/ppt_extracted/wordbank_dedup.csv", help="Path to wordbank_dedup.csv")
    ap.add_argument("--conj", default=str(DEFAULT_CONJ_TABLES), help="Path to conjugation_tables.yaml (optional)")
    ap.add_argument("--out-yaml", default="linguistic_rules/vocab/cefr_a1.yaml", help="Output YAML path")
    ap.add_argument("--out-csv", default="docs/ppt_extracted/cefr_a1_merged.csv", help="Output debug CSV path")
    ap.add_argument("--use-spacy", action="store_true", help="Use spaCy to fill missing lemmas/categories when needed")
    ap.add_argument("--spacy-model", default="de_core_news_lg", help="spaCy model name (default: de_core_news_lg)")
    ap.add_argument("--fail-on-empty", action="store_true", help="Fail hard if merged output is empty")
    args = ap.parse_args()

    cefr_path = Path(args.cefr)
    wordbank_path = Path(args.wordbank)
    conj_path = Path(args.conj)
    out_yaml = Path(args.out_yaml)
    out_csv = Path(args.out_csv)

    cefr_items = load_cefr_list(cefr_path)
    wordbank_rows = load_wordbank(wordbank_path)

    form2lemma = load_conjugation_form_map(conj_path)
    nlp = maybe_load_spacy(args.use_spacy, args.spacy_model)

    wordbank_rows = enrich_wordbank_rows(wordbank_rows, form2lemma=form2lemma, nlp=nlp)
    merged = merge_cefr_with_course(cefr_items, wordbank_rows)

    if args.fail_on_empty and not merged:
        raise SystemExit("Merged output is empty. Aborting because --fail-on-empty was set.")

    write_yaml_vocab(out_yaml, merged)
    write_debug_csv(out_csv, merged)

    print("\nDONE")
    print(f"  CEFR in    : {cefr_path}")
    print(f"  Wordbank in: {wordbank_path}")
    print(f"  YAML out   : {out_yaml}")
    print(f"  CSV out    : {out_csv}")
    print(f"  Entries    : {len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
