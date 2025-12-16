from __future__ import annotations

import csv
import re
from pathlib import Path
import yaml

ITEMS_CSV = Path("docs/ppt_extracted/items.csv")
OUT_DIR = Path("linguistic_rules/lexicon")

# What we will treat as lexicon entries per category:
# - nouns: allow "der Hund" etc.
# - verbs: allow infinitives only (single token, lowercase-ish)
# - time_numbers: allow single tokens and common time phrases (2 tokens ok)
# - adverbs: allow single token
# - adjectives: allow single token
ALLOW_TOKENS = {
    "noun": 4,
    "verb": 2,
    "adjective": 2,
    "adverb": 2,
    "time_numbers": 4,
}

PUNCT = set("?!:;")

def looks_like_lexicon(text: str, category: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False

    # keep commas out; they usually indicate sentences/examples
    if "," in t:
        return False

    # reject obvious sentence punctuation (but allow dot in times like 12.30)
    if any(ch in t for ch in PUNCT):
        return False

    tokens = t.split()
    if len(tokens) > ALLOW_TOKENS.get(category, 2):
        return False

    # verbs lexicon: prefer infinitives only (gehen, lernen, arbeiten)
    if category == "verb":
        if len(tokens) != 1:
            return False
        # reject capitalized (likely noun or sentence start)
        if t[:1].isupper():
            return False

    # adjectives/adverbs: prefer one token
    if category in {"adjective", "adverb"}:
        if len(tokens) != 1:
            return False

    # time_numbers: allow tokens like "morgen", "heute Abend", "12:30"
    if category == "time_numbers":
        # allow times and numbers
        if re.fullmatch(r"\d{1,2}:\d{2}", t):
            return True
        if re.fullmatch(r"\d+", t):
            return True

    return True


def load_rows():
    with ITEMS_CSV.open("r", encoding="utf-8") as f:
        yield from csv.DictReader(f)


def main():
    if not ITEMS_CSV.exists():
        raise SystemExit("Missing docs/ppt_extracted/items.csv")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    buckets = {
        "noun": {},
        "verb": {},
        "adjective": {},
        "adverb": {},
        "time_numbers": {},
    }

    for r in load_rows():
        cat = (r.get("category") or "").strip()
        if cat not in buckets:
            continue

        text = (r.get("norm_text") or "").strip()
        if not looks_like_lexicon(text, cat):
            continue

        key = text
        buckets[cat].setdefault(key, {"text": text, "sources": []})
        buckets[cat][key]["sources"].append({
            "ppt": r.get("ppt_file"),
            "slide": int(r.get("slide_number") or 0),
        })

    # write raw v0.1-style lexicon YAMLs so your migrate script can re-run cleanly
    outfiles = {
        "noun": "nouns.yaml",
        "verb": "verbs.yaml",
        "adjective": "adjectives.yaml",
        "adverb": "adverbs.yaml",
        "time_numbers": "numbers_time.yaml",
    }

    for cat, fname in outfiles.items():
        payload = {
            "schema_version": "0.1",
            "source": "items_csv_rebuild",
            "category": cat,
            "items": sorted(buckets[cat].values(), key=lambda x: x["text"].lower()),
        }
        p = OUT_DIR / fname
        with p.open("w", encoding="utf-8") as f:
            yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
        print(f"Wrote {p} ({len(payload['items'])} items)")

if __name__ == "__main__":
    main()
