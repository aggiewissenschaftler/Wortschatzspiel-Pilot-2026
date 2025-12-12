# Contributing to Wortschatzspiel-Pilot-2026

Thank you for your interest in contributing to **Wortschatzspiel-Pilot-2026**.  
This repository supports a research pilot study scheduled for Spring 2026.  
Contributions are welcome, but must align with the scope, ethics, and research integrity of the project.

---

## Scope and Ground Rules

Please ensure all contributions adhere to the following principles:

- Contributions must align with the **Spring 2026 pilot study scope**.
- **Do NOT commit**:
  - Personally identifiable information (PII)
  - Consent forms
  - Raw participant data
  - Real `.env` files or secrets
- Use **small, focused, and reviewable pull requests**.
- All contributions should support transparency, reproducibility, and research rigor.

---

## Development Setup

To set up a local development environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

	•	The virtual environment isolates dependencies.
	•	The .env file should remain local only and must never be committed.

⸻

Coding and Content Standards

Python
	•	Follow PEP 8 style guidelines.
	•	Include docstrings for all public functions and classes.
	•	Keep research logic explicit and readable.

YAML
	•	YAML rule files must remain human-readable.
	•	Use comments liberally to explain linguistic or pedagogical logic.
	•	Avoid over-optimization that obscures instructional intent.

Data
	•	Raw or processed data must not be committed unless:
	•	Fully anonymized
	•	Explicitly approved for inclusion
	•	Use external storage (e.g., OSF) for research datasets.

⸻

Reporting Issues

If you encounter a bug or problem, please open an issue that includes:
	1.	What you expected to happen
	2.	What actually happened
	3.	Steps to reproduce the issue
	4.	Relevant logs or error messages
(Please redact anything sensitive)

Clear, reproducible issue reports help maintain research quality.

⸻

Review and Approval

All contributions are subject to review by the repository maintainer.
Acceptance of contributions does not imply authorship or endorsement unless explicitly stated.

⸻

Questions

For questions about contributions, scope, or research alignment, please contact the repository maintainer via GitHub.

Thank you for helping keep Wortschatzspiel-Pilot-2026 rigorous, ethical, and reproducible.