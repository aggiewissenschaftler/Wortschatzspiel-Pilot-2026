#!/usr/bin/env python3
"""
Build a *core* CEFR vocab YAML (schema: vocab_schema_v1) from a canonical CSV.

Input CSV expected columns:
  text,norm,category,lemma,source

Output YAML (vocab_schema_v1) fields per item:
  lemma, category, gender, notes, seen_in_course, course_examples, source
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple

import yaml


@dataclass(frozen=True)
class Row:
    text: str
    norm: str
    category: str
    lemma: str
    source: str


def load_canonical_csv(path: Path) -> List[Row]:
    if not path.exists():
        raise FileNotFoundError(f"Input CSV not found: {path}")

    rows: List[Row] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        required = {"text", "norm", "category", "lemma", "source"}
        if not r.fieldnames or not required.issubset(set(r.fieldnames)):
            raise ValueError(
                f"CSV schema mismatch. Found: {r.fieldnames}. Required: {sorted(required)}"
            )

        for d in r:
            rows.append(
                Row(
                    text=(d.get("text") or "").strip(),
                    norm=(d.get("norm") or "").strip(),
                    category=(d.get("category") or "").strip(),
                    lemma=(d.get("lemma") or "").strip(),
                    source=(d.get("source") or "").strip(),
                )
            )
    return rows


def build_items(rows: List[Row], default_source: str) -> List[Dict]:
    items: List[Dict] = []
    seen: Set[Tuple[str, str]] = set()

    for r in rows:
        lemma = r.lemma.strip()
        cat = r.category.strip().lower()

        if not lemma or not cat:
            continue

        key = (lemma.lower(), cat)
        if key in seen:
            continue
        seen.add(key)

        items.append(
            {
                "lemma": lemma,
                "category": cat,
                "gender": "",              # filled later (nouns)
                "notes": "",               # filled later (pedagogy / usage notes)
                "seen_in_course": False,   # will be set during merge/overlay step
                "course_examples": "",     # will be populated later
                "source": default_source,  # authoritative CEFR layer
            }
        )

    # Stable ordering for diffs/reviews
    items.sort(key=lambda x: (x["category"], x["lemma"].lower()))
    return items


def write_yaml(out_path: Path, cefr_level: str, items: List[Dict]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "vocab_schema_v1",
        "cefr_level": cefr_level,
        "items": items,
    }
    with out_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            payload,
            f,
            sort_keys=False,
            allow_unicode=True,
            width=120,
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-csv", required=True, help="Canonical CSV (lemma+category unique)")
    ap.add_argument("--out-yaml", required=True, help="Output core vocab YAML (vocab_schema_v1)")
    ap.add_argument("--cefr", default="A1", help="CEFR level label (default: A1)")
    ap.add_argument("--source", default="cefr_a1", help="Source label stored in YAML items (default: cefr_a1)")
    ap.add_argument("--fail-on-empty", action="store_true", help="Exit non-zero if no items were written")
    args = ap.parse_args()

    in_csv = Path(args.in_csv)
    out_yaml = Path(args.out_yaml)

    rows = load_canonical_csv(in_csv)
    items = build_items(rows, default_source=args.source)

    write_yaml(out_yaml, cefr_level=args.cefr, items=items)

    print("DONE: Core CEFR vocab YAML built")
    print(f"  In CSV  : {in_csv}")
    print(f"  Out YAML: {out_yaml}")
    print(f"  Items   : {len(items)}")

    if args.fail_on_empty and len(items) == 0:
        print("ERROR: No items produced (fail-on-empty).")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
