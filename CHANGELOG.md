# Changelog — Wortschatzspiel-Pilot-2026

All notable changes to this project will be documented in this file.

This project follows a research-first development model. Versions reflect
milestones aligned with pilot studies, conference submissions, and dissertation
progress rather than production software releases.

---

## [Unreleased]
### Planned
- Pilot study execution (Spring 2026)
- Data collection and analysis scripts
- Evaluation metrics and reporting artifacts
- Conference manuscript finalization (ASEE GSW, ASEE National, JURE)

---

## [2025-12-12]
### Added
- Initial repository scaffolding
- Core root files:
  - `README.md`
  - `LICENSE` (MIT)
  - `CITATION.cff`
  - `requirements.txt`
  - `.env.example`
  - `docker-compose.yml`
  - `.gitignore`
  - `pyproject.toml`
  - `Makefile`
  - `CHANGELOG.md`
  - `CONTRIBUTING.md`
- Pilot study structure and planning artifacts

---

## Versioning Notes
- Dates are used instead of semantic versioning during the research phase
- Formal version numbers will be introduced at first public pilot release

==========================================

[v0.1] — 2025-12-13

Added
	•	Integration contract documenting the file-based interface between Wortschatzspiel (child) and PedagoReLearn (parent): docs/INTEGRATION.md.
	•	Canonical YAML schema documentation for linguistic rules: docs/yaml/SCHEMA.md.
	•	Initial linguistic rule set (Pilot baseline):
	•	Core CEFR A1 vocabulary: linguistic_rules/vocab/cefr_a1_core.yaml
	•	Article system (normalized; definite/indefinite; nominative/accusative; plural): linguistic_rules/grammar/articles.yaml
	•	Negation rules for nicht: linguistic_rules/grammar/negation.yaml
	•	Feedback scaffolding templates: linguistic_rules/feedback/templates.yaml

Changed
	•	README updated to reflect repository purpose and to link to the integration contract (docs/INTEGRATION.md).
	•	Added typing_extensions dependency to stabilize Python 3.11 environments: requirements.txt.
	•	.gitignore updated to exclude manuscripts/writing artifacts and other local-only files.

Removed
	•	Removed legacy “scaffold PDF/doc” files from the repository root (replaced by standard root files and markdown documentation).

Fixed
	•	Cleaned up accidentally-added manuscript artifacts (added then removed) to keep the repo root and Manuscripts directory tidy.
