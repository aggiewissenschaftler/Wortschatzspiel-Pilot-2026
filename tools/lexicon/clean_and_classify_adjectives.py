#!/usr/bin/env python3
"""
Clean + normalize adjectives in linguistic_rules/lexicon/adjectives.yaml.

What it does:
- De-dupes by lemma (normalized German form)
- Removes obvious meta/junk entries
- Validates "adjective-ish" tokens (letters/umlauts/ß, optional hyphen)
- Rewrites schema entries with consistent IDs: A1-ADJ-0001, ...
- Keeps your schema header fields consistent with verbs.yaml

Output:
  linguistic_rules/lexicon/adjectives_cleaned.yaml
"""

from __future__ import annotations

import re
import unicodedata as ud
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


# ----------------------------
# Config
# ----------------------------
INPUT_PATH = Path("linguistic_rules/lexicon/adjectives.yaml")
OUTPUT_PATH = Path("linguistic_rules/lexicon/adjectives_cleaned.yaml")

SCHEMA_NAME = "lexical_schema_v1"
LANGUAGE = "de"
CEFR_LEVEL = "A1"
SOURCE_DEFAULT = "cefr_a1_core"

# Allow German letters + optional hyphens (e.g., "hell-blau")
WORD_RE = re.compile(r"^[a-zäöüß]+(?:-[a-zäöüß]+)*$")

# Stuff that is *not* vocabulary (often shows up from slides/notes)
META_TOKENS = {
    "adjektiv", "adjective", "adjectives",
    "noun", "nouns", "verb", "verbs", "infinitive", "conjugated",
    "pronoun", "preposition", "artikel", "article", "articles",
    "plural", "singular", "grammar", "regel", "rules",
    "word", "words", "order", "satz", "sentence",
}

# Fix common typos / variants
CORRECTIONS: Dict[str, str] = {
    # examples — add as you encounter them
    "gros": "groß",
    "gross": "groß",
    "uber": "über",
}

# Optional: if you have known English glosses, keep them here.
# Otherwise leave blank; the script will report what's missing.
TRANSLATIONS: Dict[str, str] = {
    # "groß": "big, tall",
    # "klein": "small",
}


def nfc_lower(s: str) -> str:
    return ud.normalize("NFC", (s or "")).strip().lower()


def is_valid_adjective(lemma: str) -> bool:
    """Basic sanity checks for German adjective tokens."""
    if not lemma:
        return False
    if lemma in META_TOKENS:
        return False
    if len(lemma) < 2:
        return False
    if not WORD_RE.match(lemma):
        return False
    return True


def generate_item_id(index: int) -> str:
    return f"A1-ADJ-{index:04d}"


def clean_and_rewrite_adjectives(input_path: Path, output_path: Path) -> None:
    data = yaml.safe_load(input_path.read_text(encoding="utf-8")) or {}

    cleaned_items: List[dict] = []
    removed_items: List[Tuple[str, str]] = []
    corrected_items: List[Tuple[str, str]] = []
    missing_translations: List[str] = []

    seen = set()
    idx = 1

    for item in data.get("items", []):
        # Accept either 'lemma' or 'de' as source; normalize into lemma/de
        raw = item.get("lemma") or item.get("de") or ""
        lemma = nfc_lower(raw)

        if not lemma:
            continue

        if lemma in CORRECTIONS:
            old = lemma
            lemma = nfc_lower(CORRECTIONS[lemma])
            corrected_items.append((old, lemma))

        if lemma in seen:
            removed_items.append((lemma, "duplicate"))
            continue

        if not is_valid_adjective(lemma):
            removed_items.append((lemma, "invalid adjective / meta token"))
            continue

        seen.add(lemma)

        english = TRANSLATIONS.get(lemma, item.get("en", "") or "")
        if not english:
            missing_translations.append(lemma)

        new_item = {
            "item_id": generate_item_id(idx),
            "type": "adjective",
            "de": lemma,
            "en": english,
            "lemma": lemma,
            "seen_in_course": bool(item.get("seen_in_course", False)),
            "notes": item.get("notes", "") or "",
            "source": item.get("source", SOURCE_DEFAULT) or SOURCE_DEFAULT,
        }
        cleaned_items.append(new_item)
        idx += 1

    output_data = {
        "schema": SCHEMA_NAME,
        "language": LANGUAGE,
        "cefr_level": CEFR_LEVEL,
        "source": data.get("source", SOURCE_DEFAULT) or SOURCE_DEFAULT,
        "last_updated": str(date.today()),
        "items": cleaned_items,
    }

    output_path.write_text(
        yaml.dump(output_data, allow_unicode=True, sort_keys=False),
        encoding="utf-8"
    )

    # Report
    print("\n" + "=" * 60)
    print("ADJECTIVE LEXICON CLEANUP REPORT")
    print("=" * 60)
    print(f"Input file:   {input_path}")
    print(f"Output file:  {output_path}")
    print("-" * 60)
    print(f"Input items:   {len(data.get('items', []))}")
    print(f"Output items:  {len(cleaned_items)}")
    print(f"Removed:       {len(removed_items)}")
    print(f"Corrected:     {len(corrected_items)}")

    print(f"\nMISSING TRANSLATIONS: {len(missing_translations)}")
    if missing_translations:
        for w in missing_translations[:25]:
            print(f"  - {w}")
        if len(missing_translations) > 25:
            print("  ... (more)")

    if removed_items:
        print("\nREMOVED ENTRIES (first 30):")
        for lemma, reason in removed_items[:30]:
            print(f"  - {lemma} ({reason})")
        if len(removed_items) > 30:
            print("  ... (more)")

    if corrected_items:
        print("\nCORRECTIONS:")
        for old, new in corrected_items:
            print(f"  - {old} → {new}")

    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)


def main():
    if not INPUT_PATH.exists():
        raise SystemExit(f"ERROR: Input file not found: {INPUT_PATH}")

    clean_and_rewrite_adjectives(INPUT_PATH, OUTPUT_PATH)

    print("\nNext steps:")
    print(f"  1) Review: {OUTPUT_PATH}")
    print(f"  2) If good, replace original:")
    print(f"     mv {OUTPUT_PATH} {INPUT_PATH}")
    print(f"  3) Run your index/validation pipeline as needed")
    print(f"  4) Commit changes")


if __name__ == "__main__":
    main()
