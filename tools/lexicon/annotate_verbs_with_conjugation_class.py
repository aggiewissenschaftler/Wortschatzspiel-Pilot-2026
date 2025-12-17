#!/usr/bin/env python3
"""
Annotate lexicon verbs with a conjugation_class field by using existing grammar YAMLs.

Writes back to linguistic_rules/lexicon/verbs.yaml (or a --out path).
Default behavior:
- irregular: lemmas listed in grammar/verbs_irregular.yaml (sample_lemmas)
- stemchange: lemmas listed in grammar/verbs_stemchange.yaml (sample_lemmas)
- regular: everything else (default)

This is intentionally conservative: it never invents stem-change/irregular without an explicit list.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import yaml


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def dump_yaml(data, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def extract_sample_lemmas(grammar_yaml: dict) -> set[str]:
    ex = grammar_yaml.get("examples") or {}
    samples = ex.get("sample_lemmas") or []
    out = set()
    for s in samples:
        if isinstance(s, str) and s.strip():
            out.add(s.strip())
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbs-yaml", default="linguistic_rules/lexicon/verbs.yaml")
    ap.add_argument("--grammar-dir", default="linguistic_rules/grammar")
    ap.add_argument("--out", default="", help="Optional output path; if omitted, overwrite verbs.yaml")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing conjugation_class if present")
    args = ap.parse_args()

    verbs_path = Path(args.verbs_yaml)
    grammar_dir = Path(args.grammar_dir)

    irregular_path = grammar_dir / "verbs_irregular.yaml"
    stem_path = grammar_dir / "verbs_stemchange.yaml"

    verbs_data = load_yaml(verbs_path)
    items = verbs_data.get("items", [])
    if not isinstance(items, list) or not items:
        raise SystemExit(f"ERROR: No items found in {verbs_path}")

    irregular_data = load_yaml(irregular_path)
    stem_data = load_yaml(stem_path)

    irregular_set = extract_sample_lemmas(irregular_data)
    stem_set = extract_sample_lemmas(stem_data)

    updated = 0
    kept = 0

    for it in items:
        if not isinstance(it, dict):
            continue
        lemma = (it.get("lemma") or "").strip()
        if not lemma:
            continue

        if "conjugation_class" in it and not args.overwrite:
            kept += 1
            continue

        if lemma in irregular_set:
            it["conjugation_class"] = "irregular"
        elif lemma in stem_set:
            it["conjugation_class"] = "stemchange"
        else:
            it["conjugation_class"] = "regular"

        updated += 1

    out_path = Path(args.out) if args.out else verbs_path
    dump_yaml(verbs_data, out_path)

    print("Annotated verbs with conjugation_class")
    print("-------------------------------------")
    print("verbs.yaml        :", str(verbs_path))
    print("output            :", str(out_path))
    print("irregular samples :", len(irregular_set), sorted(list(irregular_set))[:10])
    print("stemchange samples:", len(stem_set), sorted(list(stem_set))[:10])
    print("updated items     :", updated)
    print("kept items        :", kept)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
