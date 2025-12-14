.PHONY: help setup install env run stop clean

help:
	@echo "Available commands:"
	@echo "  make setup    - Create virtual environment and install dependencies"
	@echo "  make install  - Install Python dependencies"
	@echo "  make env      - Copy .env.example to .env"
	@echo "  make run      - Start services with Docker"
	@echo "  make stop     - Stop Docker services"
	@echo "  make clean    - Remove virtual environment and cache files"

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

install:
	pip install -r requirements.txt

env:
	cp .env.example .env

run:
	docker-compose up

stop:
	docker-compose down

clean:
	rm -rf .venv __pycache__


- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

.PHONY: validate pipeline relink rebuild ids clean_backups

validate:
	python tools/validate_ruleset_integrity.py

rebuild:
	python tools/rebuild_lexicon_from_items_csv.py

ids:
	python tools/add_lex_ids_and_build_index.py

relink:
	python tools/link_conjugation_tables_to_lexicon.py

pipeline:
	python tools/rebuild_lexicon_from_items_csv.py
	python tools/add_lex_ids_and_build_index.py
	python tools/link_conjugation_tables_to_lexicon.py
	python tools/validate_ruleset_integrity.py

clean_backups:
	@echo "Removing .bak backups (safe cleanup)..."
	@find . -name "*.bak" -type f -print -delete
