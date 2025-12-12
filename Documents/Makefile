.PHONY: help venv install run docker clean

help:
	@echo "Targets:"
	@echo "  venv     - know-how: create local virtual environment"
	@echo "  install  - install Python requirements"
	@echo "  run      - run a placeholder entrypoint (update later)"
	@echo "  docker   - start docker services (if applicable)"
	@echo "  clean    - remove common build artifacts"

venv:
	python -m venv .venv
	@echo "Activate: source .venv/bin/activate"

install:
	pip install -r requirements.txt

run:
	@echo "Update this target to your real entrypoint (e.g., python -m rl_agent.training.train_agent)"

docker:
	docker compose up

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
