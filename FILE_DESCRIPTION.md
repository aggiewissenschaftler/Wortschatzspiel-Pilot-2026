# Wortschatzspiel Root Files Explained

This document explains the purpose, use, and intended audience for each
standard file located in the root directory of the
**Wortschatzspiel-Pilot-2026** repository.

---

## I. README.md

**Purpose:**  
Primary entry point for the repository.

**Use:**  
Explains what the project is, how to install it, and how to run it.

**Audience:**  
Humans — reviewers, collaborators, and future you.

---

## II. LICENSE

**Purpose:**  
Defines the legal permissions governing the project.

**Use:**  
States that others may reuse, modify, and distribute the software under
MIT License terms.

**Audience:**  
Lawyers, publishers, universities, and GitHub’s license detection system.

---

## III. CITATION.cff

**Purpose:**  
Provides machine-readable citation metadata.

**Use:**  
Enables automatic citation support on GitHub, Zenodo, and reference managers.

**Audience:**  
Indexing services, researchers, and academic publishers.

---

## IV. requirements.txt

**Purpose:**  
Lists Python dependencies required to run the project.

**Use:**  
Install dependencies using:

```bash
pip install -r requirements.txt

Audience:
Python runtime environments and developers.

⸻

V. docker-compose.yml

Purpose:
Defines and orchestrates the development environment.

Use:
Launch services using:
docker-compose up

Audience:
Docker and developers running the full system stack.

⸻

VI. .gitignore

Purpose:
Prevents unnecessary or sensitive files from being tracked by Git.

Use:
Automatically applied by Git to ignore specified files and directories.

Audience:
Git version control system.

⸻

VII. .env.example

Purpose:
Provides a template for required environment variables.

Use:
Copy and rename to .env, then customize values as needed.
cp .env.example .env

Audience:
Developers and collaborators.

⸻

VIII. pyproject.toml

Purpose:
Defines Python project metadata and tooling configuration.

Use:
Specifies project information, dependencies, and build or formatting tools.

Audience:
Python packaging ecosystem (pip, build tools, IDEs).

⸻

IX. Makefile

Purpose:
Provides shortcut commands for common tasks.

Use:
Run commands such as:
make setup
make run

Audience:
Developers working with the project.

⸻

X. CHANGELOG.md

Purpose:
Tracks version history and notable changes.

Use:
Documents what changed between releases or milestones.

Audience:
Reviewers, users, and maintainers.

⸻

XI. CONTRIBUTING.md

Purpose:
Defines contribution guidelines.

Use:
Explains how others can propose changes, report issues, or submit pull requests.

Audience:
Collaborators and external contributors.