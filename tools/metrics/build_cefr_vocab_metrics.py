#!/usr/bin/env python3
"""
Build CEFR vocabulary coverage metrics from a lemma-based YAML vocab file.

Reads:
  linguistic_rules/vocab/cefr_a1.yaml

Outputs:
  - Printed metrics summary (stdout)
  - Optional Markdown snippet for docs/metrics/cefr_a1.md
"""

import yaml
from collections import Counter
from pathlib import Path

VOCAB_YAML = Path("linguistic_rules/vocab/cefr_a1.yaml")


def main() -> None:
    if not VOCAB_YAML.exists():
        raise FileNotFoundError(f"Missing vocab file: {VOCAB_YAML}")

    with VOCAB_YAML.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    items = data.get("items", [])
    if not items:
        print("No vocab items found.")
        return

    lemmas = []
    pos_types = []

    for item in items:
        # Headword (lemma)
        lemma = (item.get("de") or "").strip()
        if item.get("type") == "verb":
            lemma = lemma or (item.get("infinitive") or "").strip()

        pos = (item.get("type") or "").strip().lower()

        if lemma:
            lemmas.append(lemma)
        if pos:
            pos_types.append(pos)

    unique_lemmas = len(set(lemmas))
    pos_counts = Counter(pos_types)

    core_pos = {"noun", "verb", "adjective"}
    function_words = sum(
        count for p, count in pos_counts.items() if p not in core_pos
    )

    print("\nCEFR A1 Vocabulary Coverage Metrics")
    print("===================================")
    print(f"Total entries        : {len(items)}")
    print(f"Unique lemmas        : {unique_lemmas}\n")

    print("By part of speech (POS):")
    for pos, count in pos_counts.most_common():
        print(f"  {pos:15s} {count}")

    print("\nSummary buckets:")
    print(f"  Nouns          : {pos_counts.get('noun', 0)}")
    print(f"  Verbs          : {pos_counts.get('verb', 0)}")
    print(f"  Adjectives     : {pos_counts.get('adjective', 0)}")
    print(f"  Function words : {function_words}")
    print()


if __name__ == "__main__":
    main()
