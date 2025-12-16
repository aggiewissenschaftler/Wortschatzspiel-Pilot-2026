#!/usr/bin/env python3
"""
Split a CEFR core vocab YAML (vocab_schema_v1) into POS lexicon YAML files.

Input (example):  linguistic_rules/vocab/cefr_a1_core.yaml
Output folder:    linguistic_rules/lexicon/
Outputs:
  nouns.yaml
  verbs.yaml
  adjectives.yaml
  adverbs.yaml
  others.yaml     (everything not in the four above)

Notes:
- This does NOT overwrite your existing lexicon files unless you pass --overwrite.
- It preserves the original item fields (lemma/category/etc.) and adds/overrides:
    source: cefr_a1_core
- This is lemma-based, matching your current pipeline direction.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

import yaml


POS_MAP = {
    "noun": "nouns.yaml",
    "verb": "verbs.yaml",
    "adjective": "adjectives.yaml",
    "adverb": "adverbs.yaml",
}

DEFAULT_OUT_FILES = [
    "nouns.yaml",
    "verbs.yaml",
    "adjectives.yaml",
    "adverbs.yaml",
    "others.yaml",
]


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def dump_yaml(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        # Keep it human-readable and consistent
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            allow_unicode=True,
            width=1000,
        )


def normalize_category(cat: str) -> str:
    return (cat or "").strip().lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in-yaml",
        required=True,
        help="Path to CEFR core vocab YAML (vocab_schema_v1)",
    )
    ap.add_argument(
        "--out-dir",
        default="linguistic_rules/lexicon",
        help="Destination directory for POS lexicon YAMLs (default: linguistic_rules/lexicon)",
    )
    ap.add_argument(
        "--cefr-level",
        default="A1",
        help="CEFR level label to write in file headers (default: A1)",
    )
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing POS files in out-dir",
    )
    ap.add_argument(
        "--fail-on-empty",
        action="store_true",
        help="Exit non-zero if no items are written",
    )
    args = ap.parse_args()

    in_path = Path(args.in_yaml)
    out_dir = Path(args.out_dir)

    if not in_path.exists():
        raise FileNotFoundError(f"Input YAML not found: {in_path}")

    data = load_yaml(in_path)
    items: List[Dict[str, Any]] = data.get("items", []) or []

    buckets: Dict[str, List[Dict[str, Any]]] = {fn: [] for fn in DEFAULT_OUT_FILES}

    written = 0

    for it in items:
        lemma = (it.get("lemma") or "").strip()
        cat = normalize_category(it.get("category") or "")

        if not lemma:
            continue

        out_file = POS_MAP.get(cat, "others.yaml")

        # Copy item + enforce source marker for traceability
        new_item = dict(it)
        new_item["lemma"] = lemma
        new_item["category"] = cat if cat else "other"
        new_item["source"] = "cefr_a1_core"

        buckets[out_file].append(new_item)
        written += 1

    if args.fail_on_empty and written == 0:
        print("ERROR: No items written (fail-on-empty).")
        return 3

    # Write output files
    for fname, bucket_items in buckets.items():
        out_path = out_dir / fname
        if out_path.exists() and not args.overwrite:
            print(f"SKIP (exists): {out_path}  (use --overwrite to replace)")
            continue

        out_data = {
            "schema": "lexical_schema_v1",
            "language": "de",
            "cefr_level": args.cefr_level,
            "source": "cefr_a1_core",
            "items": bucket_items,
        }
        dump_yaml(out_data, out_path)
        print(f"WROTE: {out_path}  ({len(bucket_items)} items)")

    print(f"\nDONE. Total items routed: {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
