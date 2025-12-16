from __future__ import annotations

from pathlib import Path
import re
import sys
import yaml


INDEX_PATH = Path("linguistic_rules/lexicon/index.yaml")
TABLES_PATH = Path("linguistic_rules/morphology/conjugation_tables.yaml")


def norm(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s.lower()


def load_yaml(p: Path):
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(p: Path, data):
    with p.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def build_verb_lookup(index_data: dict) -> dict[str, str]:
    """
    Map normalized surface text -> lex_id for verbs only.
    """
    lookup: dict[str, str] = {}
    for item in index_data.get("items", []):
        if item.get("category") != "verb":
            continue
        text = item.get("text", "")
        lex_id = item.get("lex_id", "")
        if text and lex_id:
            lookup[norm(text)] = lex_id
    return lookup


def main() -> int:
    if not INDEX_PATH.exists():
        print(f"Missing {INDEX_PATH}. Run: python tools/add_lex_ids_and_build_index.py", file=sys.stderr)
        return 2
    if not TABLES_PATH.exists():
        print(f"Missing {TABLES_PATH}.", file=sys.stderr)
        return 2

    index_data = load_yaml(INDEX_PATH)
    verb_lookup = build_verb_lookup(index_data)

    tables_data = load_yaml(TABLES_PATH)
    tables = tables_data.get("tables", [])

    updated = 0
    missing = []

    for t in tables:
        lemma = t.get("lemma_guess", "")
        if not lemma:
            missing.append(("__no_lemma__", t.get("table_id", "")))
            continue

        # already linked
        if t.get("lemma_lex_id"):
            continue

        lid = verb_lookup.get(norm(lemma))
        if lid:
            t["lemma_lex_id"] = lid
            updated += 1
        else:
            missing.append((lemma, t.get("table_id", "")))

    save_yaml(TABLES_PATH, tables_data)

    print(f"Updated tables with lemma_lex_id: {updated}")
    if missing:
        print("\nMissing lemma matches (needs manual fix or lexicon addition):")
        for lemma, tid in missing[:60]:
            print(f"  - lemma='{lemma}'  table_id='{tid}'")
        if len(missing) > 60:
            print(f"  ...and {len(missing)-60} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
