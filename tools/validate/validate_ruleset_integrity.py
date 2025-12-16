#!/usr/bin/env python3
"""
Validate integrity of Wortschatzspiel linguistic ruleset.

Checks:
- lexicon/index.yaml loads
- any *_lex_id fields in YAML files point to a real lex_id in the index
- warns about likely places where raw strings are used instead of IDs (optional)
"""

from __future__ import annotations

from pathlib import Path
import sys
import yaml
import re
from typing import Any, Dict, Set, List, Tuple

ROOT = Path(".")
LEX_INDEX = ROOT / "linguistic_rules" / "lexicon" / "index.yaml"

# Directories to scan for YAML rule files (add more as your repo grows)
SCAN_DIRS = [
    ROOT / "linguistic_rules" / "grammar",
    ROOT / "linguistic_rules" / "morphology",
]

LEX_ID_KEY_RE = re.compile(r".*_lex_id$")


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def collect_lex_ids(index_data: Dict[str, Any]) -> Set[str]:
    ids: Set[str] = set()
    for it in index_data.get("items", []):
        lex_id = it.get("lex_id")
        if lex_id:
            ids.add(str(lex_id))
    return ids


def iter_yaml_files() -> List[Path]:
    files: List[Path] = []
    for d in SCAN_DIRS:
        if d.exists():
            files.extend(sorted(d.rglob("*.yaml")))
    return files


def find_lex_id_refs(obj: Any, path: str = "") -> List[Tuple[str, str]]:
    """
    Return list of (field_path, lex_id_value) for any *_lex_id keys found in obj.
    """
    found: List[Tuple[str, str]] = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            k_str = str(k)
            subpath = f"{path}.{k_str}" if path else k_str
            if LEX_ID_KEY_RE.match(k_str) and v is not None:
                found.append((subpath, str(v)))
            found.extend(find_lex_id_refs(v, subpath))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            subpath = f"{path}[{i}]"
            found.extend(find_lex_id_refs(v, subpath))

    return found


def main() -> int:
    if not LEX_INDEX.exists():
        print(f"ERROR: missing lexicon index: {LEX_INDEX}")
        return 2

    index = load_yaml(LEX_INDEX)
    lex_ids = collect_lex_ids(index)
    if not lex_ids:
        print("ERROR: lexicon/index.yaml loaded but contains no lex_id entries.")
        return 2

    yaml_files = iter_yaml_files()
    if not yaml_files:
        print("WARN: No YAML files found under expected scan dirs.")
        return 0

    errors = 0
    checked = 0

    for ypath in yaml_files:
        try:
            data = load_yaml(ypath)
        except Exception as e:
            print(f"ERROR: failed to parse YAML: {ypath} :: {e}")
            errors += 1
            continue

        refs = find_lex_id_refs(data)
        if not refs:
            continue

        checked += 1
        for field_path, ref_id in refs:
            if ref_id not in lex_ids:
                print(f"ERROR: {ypath}:{field_path} -> '{ref_id}' not found in lexicon/index.yaml")
                errors += 1

    print("\nValidation summary:")
    print(f"  Lexicon IDs loaded: {len(lex_ids)}")
    print(f"  YAML files scanned: {len(yaml_files)}")
    print(f"  Files with *_lex_id refs: {checked}")
    print(f"  Errors: {errors}")

    if errors:
        print("\nFix the missing IDs OR rebuild index.yaml before committing.")
        return 1

    print("\nOK: All referenced *_lex_id values resolve in lexicon/index.yaml.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
