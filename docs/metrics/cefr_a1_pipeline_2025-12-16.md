# CEFR A1 Pipeline Metrics (2025-12-16)

## Inputs
- Source PDF: `docs/cefr/goethe_a1_wortliste.pdf`
- Extracted CSV: `docs/cefr/goethe_a1_vocab.csv`
- Canonical (dedup) CSV: `docs/cefr/goethe_a1_vocab_canonical.csv`
- Course wordbank: `docs/ppt_extracted/wordbank_dedup.csv`

## Output Artifacts
- A1 YAML: `linguistic_rules/vocab/cefr_a1.yaml`
- Merge debug CSV: `docs/ppt_extracted/cefr_a1_merged.csv`

## Counts
- Extracted CSV rows (incl header): 6806  
- Extracted vocab rows: 6805  
- Canonical rows (unique lemma+category): 1418  
- Wordbank rows: 1970  
- Final merged vocab entries: 2915

## Notes
- Canonicalization key: `(lemma, category)`
- Tag: `cefr-a1-pipeline-stable-2025-12-16`
