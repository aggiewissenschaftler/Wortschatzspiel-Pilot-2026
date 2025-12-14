.PHONY: help setup install env clean clean_backups \
        rebuild ids relink validate pipeline

help:
	@echo "Available commands:"
	@echo ""
	@echo "Environment:"
	@echo "  make setup      Create virtual environment and install dependencies"
	@echo "  make install    Install Python dependencies"
	@echo ""
	@echo "Lexicon pipeline:"
	@echo "  make rebuild    Rebuild lexicon from PPT-extracted CSV"
	@echo "  make ids        Add lexicon IDs and rebuild index"
	@echo "  make relink     Link morphology tables to lexicon IDs"
	@echo "  make validate   Validate cross-file ID integrity"
	@echo "  make pipeline   Run full linguistic pipeline"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean      Remove virtual environment and caches"
	@echo "  make clean_backups  Remove .bak files"

# ---------- Environment ----------

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

install:
	pip install -r requirements.txt

# ---------- Lexicon Pipeline ----------

rebuild:
	python tools/rebuild_lexicon_from_items_csv.py

ids:
	python tools/add_lex_ids_and_build_index.py

relink:
	python tools/link_conjugation_tables_to_lexicon.py

validate:
	python tools/validate_ruleset_integrity.py

pipeline:
	python tools/rebuild_lexicon_from_items_csv.py
	python tools/add_lex_ids_and_build_index.py
	python tools/link_conjugation_tables_to_lexicon.py
	python tools/validate_ruleset_integrity.py

# ---------- Cleanup ----------

clean:
	rm -rf .venv __pycache__ .pytest_cache

clean_backups:
	@echo "Removing .bak backups (safe cleanup)..."
	@find . -name "*.bak" -type f -print -delete
