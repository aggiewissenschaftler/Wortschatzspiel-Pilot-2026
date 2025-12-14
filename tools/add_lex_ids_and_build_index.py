from __future__ import annotations

import re
import sys
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import yaml


LEXICON_DIR = Path("linguistic_rules/lexicon")
INDEX_PATH = LEXICON_DIR / "index.yaml"

# Lexicon files we manage (add more later if needed)
MANAGED_FILES = [
    "nouns.yaml",
    "verbs.yaml",
    "adjectives.yaml",
    "adverbs.yaml",
    "numbers_time.yaml",
]

# German articles (nominative singular; your PPT nouns are largely in this form)
ARTICLES = {"der", "die", "das"}

# Characters allowed in ID parts
NON_ID_CHARS = re.compile(r"[^A-Z0-9]+")

# Some common German characters normalization
UMLAUT_MAP = str.maketrans({
    "ä": "AE", "ö": "OE", "ü": "UE",
    "Ä": "AE", "Ö": "OE", "Ü": "UE",
    "ß": "SS",
})

# If you want to keep digits (e.g., "2026"), we keep them.
# We also keep A-Z, 0-9 only, underscore removed in favor of dot-separated parts.


@dataclass
class SourceRef:
    ppt: str
    slide: int


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse to a dict.")
    return data


def dump_yaml(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def backup_file(path: Path) -> Path:
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    return bak


def to_id_token(s: str) -> str:
    """
    Convert a word/phrase to an uppercase ID-safe token.
    - German umlauts/ß normalized
    - non-alphanumerics collapsed
    - multiple separators collapsed
    """
    if not s:
        return ""
    s = s.strip().translate(UMLAUT_MAP).upper()
    s = NON_ID_CHARS.sub(".", s)
    s = s.strip(".")
    # Collapse repeated dots
    s = re.sub(r"\.+", ".", s)
    return s


def parse_noun_text(text: str) -> Tuple[Optional[str], str]:
    """
    Returns (article, noun_core) where article may be None.
    Handles:
      - "die Katze" -> ("die", "Katze")
      - "Katze" -> (None, "Katze")
      - "die Schuhe" -> ("die", "Schuhe")
    """
    t = (text or "").strip()
    if not t:
        return None, ""
    parts = t.split()
    if len(parts) >= 2 and parts[0].lower() in ARTICLES:
        return parts[0].lower(), " ".join(parts[1:])
    return None, t


def category_prefix(category: str) -> str:
    # category in your lexicon YAML: noun, verb, adjective, adverb, time_numbers (etc.)
    c = category.lower().strip()
    if c == "noun":
        return "LEX.NOUN"
    if c == "verb":
        return "LEX.VERB"
    if c == "adjective":
        return "LEX.ADJ"
    if c == "adverb":
        return "LEX.ADV"
    if c in {"time_numbers", "numbers_time"}:
        return "LEX.TIME"
    # fallback
    return f"LEX.{to_id_token(c) or 'ITEM'}"


def make_lex_id(category: str, text: str) -> str:
    """
    Default ID strategy:
    - Noun: include article if present => LEX.NOUN.KATZE.DIE
    - Verb: lemma-like text => LEX.VERB.GEHEN
    - Others: tokenized text
    """
    prefix = category_prefix(category)

    if category.lower().strip() == "noun":
        art, core = parse_noun_text(text)
        core_tok = to_id_token(core)
        if not core_tok:
            core_tok = "UNKNOWN"
        if art:
            art_tok = to_id_token(art)
            return f"{prefix}.{core_tok}.{art_tok}"
        return f"{prefix}.{core_tok}"

    # time/numbers may include multiword phrases (e.g., "morgen früh")
    tok = to_id_token(text)
    if not tok:
        tok = "UNKNOWN"
    return f"{prefix}.{tok}"


def ensure_unique_id(proposed: str, used: Dict[str, int]) -> str:
    """
    If proposed already used, append .N where N increments.
    """
    if proposed not in used:
        used[proposed] = 1
        return proposed
    used[proposed] += 1
    return f"{proposed}.{used[proposed]}"


def collect_all_existing_ids(files_data: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """
    Return mapping: lex_id -> "file:idx" (first seen) to detect conflicts.
    """
    seen: Dict[str, str] = {}
    for fname, data in files_data.items():
        items = data.get("items", [])
        if not isinstance(items, list):
            continue
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            lex_id = item.get("lex_id")
            if isinstance(lex_id, str) and lex_id.strip():
                key = lex_id.strip()
                if key not in seen:
                    seen[key] = f"{fname}:{i}"
    return seen


def build_index_entry(category: str, item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal index entry. Keep it compact but useful.
    """
    entry: Dict[str, Any] = {
        "lex_id": item["lex_id"],
        "category": category,
        "text": item.get("text", ""),
    }

    # Optional structured bits for nouns
    if category.lower().strip() == "noun":
        art, core = parse_noun_text(item.get("text", ""))
        if art:
            entry["article"] = art
        entry["lemma"] = core.strip() if core else item.get("text", "")

    if category.lower().strip() == "verb":
        entry["lemma"] = item.get("text", "").strip()

    # Copy sources if present (keeps provenance for reviewer safety)
    if "sources" in item:
        entry["sources"] = item["sources"]

    return entry


def main() -> int:
    if not LEXICON_DIR.exists():
        print(f"ERROR: Missing {LEXICON_DIR}. Run from repo root.", file=sys.stderr)
        return 2

    # Load all managed YAML files that exist
    files_data: Dict[str, Dict[str, Any]] = {}
    for fname in MANAGED_FILES:
        path = LEXICON_DIR / fname
        if path.exists():
            files_data[fname] = load_yaml(path)

    if not files_data:
        print("ERROR: No managed lexicon YAMLs found to process.", file=sys.stderr)
        return 2

    # Track used IDs; start by collecting existing IDs
    existing_id_first_seen = collect_all_existing_ids(files_data)
    used_counts: Dict[str, int] = {}

    # Seed used_counts with existing IDs as already used once
    for lex_id in existing_id_first_seen.keys():
        used_counts[lex_id] = 1

    # Add missing IDs
    changed_files: List[str] = []
    index_items: List[Dict[str, Any]] = []

    for fname, data in files_data.items():
        category = data.get("category", "").strip()
        items = data.get("items", [])

        if not category:
            print(f"ERROR: {fname} missing top-level 'category'.", file=sys.stderr)
            return 2
        if not isinstance(items, list):
            print(f"ERROR: {fname} 'items' is not a list.", file=sys.stderr)
            return 2

        file_changed = False

        for i, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            # Ensure lex_id exists
            lex_id = item.get("lex_id")
            if not isinstance(lex_id, str) or not lex_id.strip():
                proposed = make_lex_id(category, item.get("text", ""))
                final_id = ensure_unique_id(proposed, used_counts)
                item["lex_id"] = final_id
                file_changed = True
            else:
                # Normalize whitespace
                item["lex_id"] = lex_id.strip()

            # Add to index list
            index_items.append(build_index_entry(category, item))

        if file_changed:
            changed_files.append(fname)
            # backup + write back
            path = LEXICON_DIR / fname
            bak = backup_file(path)
            dump_yaml(path, data)
            print(f"Updated IDs: {path}  (backup: {bak.name})")

    # Sort index entries by category then lex_id for readability
    index_items.sort(key=lambda e: (e.get("category", ""), e.get("lex_id", "")))

    # Build index payload (schema v0.2)
    index_payload: Dict[str, Any] = {
        "schema_version": "0.2",
        "rule_type": "lexicon",
        "language": "de",
        "description": "Master lexicon index with stable lex_id keys for linking grammar/morphology rules to lexical items.",
        "items": index_items,
    }

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    if INDEX_PATH.exists():
        bak = backup_file(INDEX_PATH)
        dump_yaml(INDEX_PATH, index_payload)
        print(f"Wrote: {INDEX_PATH} (backup: {bak.name})")
    else:
        dump_yaml(INDEX_PATH, index_payload)
        print(f"Wrote: {INDEX_PATH}")

    # Summary
    print("\nSummary:")
    if changed_files:
        print(f"  Updated lexicon files: {', '.join(changed_files)}")
    else:
        print("  No lexicon files needed ID updates (already had lex_id).")
    print(f"  Index items: {len(index_items)}")
    print("\nNext: commit lexicon YAMLs + index.yaml.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
