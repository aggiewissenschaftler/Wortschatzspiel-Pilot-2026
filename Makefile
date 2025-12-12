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