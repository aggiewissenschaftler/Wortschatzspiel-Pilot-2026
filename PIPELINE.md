Wortschatzspiel Build & Validation Pipeline

Authoritative Ops Manual (Do Not Skip Steps)

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

0. PURPOSE

This document defines the single correct build and validation pipeline for the Wortschatzspiel Pilot 2026 ruleset.

If the pipeline is not followed in order, ID drift, broken morphology links, and invalid game states will occur.

   -->	THIS IS NOT OPTIONAL GUIDANCE.
   -->	This is the system contract.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

1. Source of Truth

Primary source of truth:

	docs/ppt_extracted/items.csv

All lexicon files are derived artifacts.
Manual edits to verbs.yaml, nouns.yaml, etc. will be overwritten on rebuild.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

2. Pipeline Overview (High Level)
	
	items.csv
  	   ↓
	rebuild_lexicon_from_items_csv.py
  	   ↓
	add_lex_ids_and_build_index.py
  	   ↓
	link_conjugation_tables_to_lexicon.py
  	   ↓
	validate_ruleset_integrity.py	

Never reorder these steps.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

3. Phase 1 – Lexicon Reconstruction

Tool

	python tools/rebuild_lexicon_from_items_csv.py

What this does
	•	Rebuilds all lexicon YAMLs from CSV
	•	Buckets by category (verbs, nouns, adjectives, etc.)
	•	Sorts entries deterministically
	•	Overwrites existing YAML files

Outputs

	linguistic_rules/lexicon/
 	  ├── verbs.yaml
  	  ├── nouns.yaml
  	  ├── adjectives.yaml
  	  ├── numbers_time.yaml	


   ⚠ ️ Do  not edit these files before this step.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

4. Phase 2 – Lexical ID Assignment & Index Build

Tool 

	python tools/add_lex_ids_and_build_index.py

What this does
	•	Assigns stable lex_id values
	•	Preserves existing IDs where possible
	•	Builds the global lexicon index

Outputs

	linguistic_rules/lexicon/index.yaml

Invariants
	•	Every lexicon item must have exactly one lex_id
	•	index.yaml is the only file used for ID resolution

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

5. Phase 3 – Morphology Linking

Tool

	python tools/link_conjugation_tables_to_lexicon.py


What this does
	•	Matches conjugation tables by normalized lemma
	•	Injects lemma_lex_id into morphology tables
	•	Skips tables with missing lexicon entries

Output

	linguistic_rules/morphology/conjugation_tables.yaml

Failure Mode

If a lemma is missing:
	•	Check items.csv
	•	Rebuild lexicon
	•	Re-run Phase 2
	•	Re-run this step

Never hard-code IDs.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

6. Phase 4 – Integrity Validation (Gatekeeper)

Tool

	python tools/validate_ruleset_integrity.py

What this validates
	•	All *_lex_id references exist in index.yaml
	•	No stale or orphaned IDs
	•	All YAML files parse cleanly

Output
	•	Zero errors = safe to commit
	•	Any error = STOP

If validation fails, do not commit.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

7. Required Rebuild Order (Non-Negotiable)

If any of the following change:
	•	items.csv
	•	lexicon YAML structure
	•	ID generation logic
	•	morphology tables

You must run:

	python tools/rebuild_lexicon_from_items_csv.py
	python tools/add_lex_ids_and_build_index.py
	python tools/link_conjugation_tables_to_lexicon.py
	python tools/validate_ruleset_integrity.py

Skipping steps will corrupt the ruleset.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

8. Version Control Rules

Only commit when:
	•	Validation passes
	•	No untracked rule-impacting files remain
	•	Morphology and lexicon are in sync

Recommended commit message pattern:

	Phase X: <short description>

Example:

	Phase 4: Rebuild lexicon, relink morphology, validate ID integrity

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -⸻

9. Mental Model (Read This Once)
	•	CSV = truth
	•	Lexicon = derived
	•	Index = authority
	•	Morphology = dependent
	•	Validator = judge

If two files disagree, the index wins.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

10. Final Warning

This pipeline exists because:
	•	German morphology is unforgiving
	•	AI agents are even less forgiving
	•	Silent ID drift will destroy learning validity

Follow the pipeline.
Sleep better. :-)

