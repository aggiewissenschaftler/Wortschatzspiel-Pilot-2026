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

## [v0.1] — 2025-12-13

### Added
- Integration contract documenting the file-based interface between Wortschatzspiel (child) and PedagoReLearn (parent): `docs/INTEGRATION.md`.
- Canonical YAML schema documentation for linguistic rules: `docs/yaml/SCHEMA.md`.
- Initial linguistic rule set (Pilot baseline):
  - Core CEFR A1 vocabulary: `linguistic_rules/vocab/cefr_a1_core.yaml`
  - Article system (normalized; definite/indefinite; nominative/accusative; plural): `linguistic_rules/grammar/articles.yaml`
  - Negation rules for *nicht*: `linguistic_rules/grammar/negation.yaml`
  - Feedback scaffolding templates: `linguistic_rules/feedback/templates.yaml`

### Changed
- README updated to reflect repository purpose and to link to the integration contract.
- Added `typing_extensions` dependency to stabilize Python 3.11 environments.
- `.gitignore` updated to exclude manuscripts, writing artifacts, and local-only files.

### Removed
- Legacy scaffold PDF/DOC files removed from the repository root and replaced with standard markdown documentation.

### Fixed
- Cleaned up accidentally committed manuscript artifacts to keep the repository research-clean.

---

## Versioning Notes
- Tags (e.g., `v0.1`) mark research milestones, not production releases.
- Dates indicate when milestones were finalized and tagged.
- Semantic versioning may be introduced after the pilot phase.