from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple, Any, List
import yaml

IN_PATH = Path("linguistic_rules/morphology/conjugation_tables.yaml")
OUT_PATH = IN_PATH  # overwrite in place (safe because git)

def forms_signature(forms: Dict[str, str]) -> Tuple[Tuple[str, str], ...]:
    # stable signature regardless of key order
    return tuple(sorted((k, (v or "").strip()) for k, v in forms.items()))

def main() -> None:
    if not IN_PATH.exists():
        raise SystemExit(f"Missing: {IN_PATH}")

    data: Dict[str, Any] = yaml.safe_load(IN_PATH.read_text(encoding="utf-8"))
    tables: List[Dict[str, Any]] = data.get("tables", [])

    merged: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], Dict[str, Any]] = {}

    for t in tables:
        lemma = (t.get("lemma_guess") or "").strip()
        forms = t.get("forms") or {}
        sig = (lemma, forms_signature(forms))

        # normalize source -> sources[]
        if "sources" in t and isinstance(t["sources"], list):
            sources = t["sources"]
        else:
            src = t.get("source")
            sources = [src] if isinstance(src, dict) else []
        # drop old single source key for consistency
        t.pop("source", None)
        t["sources"] = sources

        if sig not in merged:
            merged[sig] = t
        else:
            # merge sources, keep first table_id and metadata
            existing = merged[sig]
            existing_sources = existing.get("sources", [])
            seen = {(s.get("ppt"), s.get("slide")) for s in existing_sources if isinstance(s, dict)}

            for s in sources:
                if not isinstance(s, dict):
                    continue
                key = (s.get("ppt"), s.get("slide"))
                if key not in seen:
                    existing_sources.append(s)
                    seen.add(key)

            existing["sources"] = existing_sources

    deduped_tables = list(merged.values())

    before = len(tables)
    after = len(deduped_tables)

    # write back
    data["tables"] = deduped_tables
    OUT_PATH.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    print(f"Deduped tables: {before} -> {after}")
    print(f"Wrote: {OUT_PATH}")

if __name__ == "__main__":
    main()
