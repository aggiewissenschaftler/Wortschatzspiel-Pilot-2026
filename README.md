# Wortschatzspiel-Pilot-2026 — Repository Overview

**Author:** Thomas F. Hallmark  
Department of Teaching, Learning, and Culture, Texas A&M University (College Station, TX, USA)  
Email: thomas.hallmark@tamu.edu  
ORCID: 0009-0002-3124-8140  
GitHub: https://github.com/aggiewissenschaftler

---

## Abstract

This repository summarizes the structure and purpose of **Wortschatzspiel-Pilot-2026**, which supports a **reinforcement learning (RL)**–enhanced micro-tutoring system for first-semester German learners aligned with the **Common European Framework of Reference for Languages (CEFR)** **A1** proficiency level. The pilot focuses on **human-readable YAML** (*YAML Ain’t Markup Language*) linguistic rules, adaptive feedback, and RL-driven instructional strategies implemented over a three-week period in **Spring 2026**. The repository is designed to support submissions to **ASEE Gulf Southwest (GSW) 2026**, **ASEE National 2026**, and **JURE 2026** (Junior Researchers of **EARLI**, the European Association for Research on Learning and Instruction), while also aligning with dissertation and Fulbright Germany research planning.

---

## Keywords

reinforcement learning; language learning; German vocabulary acquisition; adaptive tutoring systems; micro-tutoring; CEFR A1; computer-assisted language learning (CALL); intelligent tutoring systems; Reflexive Reciprocity Theory (RRT); educational AI; spaced repetition; feedback scaffolding; cross-cultural education

---

## Project Summary

This repository documents the design, implementation, and pilot evaluation of **Wortschatzspiel**, an **RL-enhanced micro-tutoring system** for German vocabulary acquisition. The system targets first-semester university German learners and adults at the **CEFR A1** level, with a focus on American learners transitioning into German-speaking academic or professional contexts.

The three-week pilot (Spring 2026) investigates how adaptive, AI-driven instructional strategies can support **reflexive vocabulary learning**—a process in which both the learner and the system co-evolve through reciprocal feedback loops. This work operationalizes **Reflexive Reciprocity Theory (RRT)** by examining the dynamic interplay between human pedagogical intuition and algorithmic instructional discovery.

---

## Core Components

### YAML-Encoded Linguistic Rules

The system uses structured **YAML** files to represent German linguistic patterns, morphological rules, and contextual constraints. This enables:

- **Transparent rule representation:** rules are inspectable and editable without heavy programming knowledge  
- **Version control:** rule evolution is trackable across pilot iterations  
- **Interoperability:** rules integrate with Python RL agents and web-based tutoring interfaces  

### Adaptive Feedback Engine

The tutoring system supports multi-dimensional feedback that adjusts in real time:

- **Error-type classification:** orthographic, morphological, syntactic, semantic  
- **Scaffolded hints:** implicit cues → explicit examples → direct correction  
- **Temporal spacing:** spaced repetition informed by policy behavior  
- **Contextual reinforcement:** adapts feedback based on difficulty, history, and session dynamics  

### Reinforcement Learning–Driven Instruction

The system uses RL concepts to optimize sequencing and feedback timing:

- **State representation:** learner knowledge state + context + error history  
- **Action space:** tutoring moves (introduce, review, contextualize, adjust difficulty, etc.)  
- **Reward signal:** balances short-term accuracy and longer-term retention  
- **Policy optimization:** supports discovery of effective tutoring patterns via interaction data  

### Three-Week Pilot Design

The Spring 2026 pilot includes:

- **Participant recruitment:** 30–40 first-semester German students at a large U.S. research university  
- **Baseline assessment:** pre-pilot CEFR A1 diagnostic  
- **Intervention:** 3 weeks of daily ~15-minute sessions (15 sessions total)  
- **Control:** traditional flashcards with static sequencing  
- **Treatment:** RL-enhanced adaptive tutoring with dynamic feedback  
- **Post-assessment:** immediate post-test + 2-week retention follow-up  

---

## Research Context

### Theoretical Framework: Reflexive Reciprocity Theory (RRT)

This project examines:

- **Pedagogical intuition:** formalizing instructor insights into constraints/reward shaping  
- **Algorithmic discovery:** patterns that may not be obvious to human tutors  
- **Co-learning dynamics:** emergent strategies from learner–system interaction  

### Dissertation Integration

Wortschatzspiel is positioned as the second empirical study in a three-paper dissertation:

1. **Paper 1 (PedagoReLearn):** RL framework for adaptive cross-cultural competence training  
2. **Paper 2 (Wortschatzspiel):** RL-enhanced vocabulary learning  
3. **Paper 3 (Comparative Analysis):** RRT as a unifying explanatory framework  

### Fulbright Germany Research Alignment

This pilot supports planned work in Germany at **RPTU Kaiserslautern-Landau**, including:

- Expansion to German university contexts (e.g., A2/B1 learners; German students learning academic English)  
- Inclusion of German pedagogical perspectives on AI-enhanced language learning  
- Comparative analysis of RL-driven instruction across U.S. and German contexts  

---

## Conference Submission Targets

- **ASEE Gulf Southwest (GSW) 2026:** system architecture + early pilot signals  
- **ASEE National 2026:** full pilot evaluation (RL vs. traditional) + implications  
- **JURE 2026:** theoretical positioning (RRT operationalization) + cross-cultural considerations  

---

## Technical Stack (Planned / Target)

- **Frontend:** React 18, Next.js 14, Tailwind CSS  
- **Backend:** Python 3.11, FastAPI, PostgreSQL  
- **RL Framework:** Stable-Baselines3 (PPO/A2C)  
- **NLP Processing:** spaCy (German models), Hugging Face Transformers  
- **Data Storage:** PostgreSQL, Redis  
- **Analytics:** Pandas, NumPy, Matplotlib, Seaborn, SciPy  

---

## Key Research Questions

- **RQ1:** Do learners using RL-enhanced micro-tutoring demonstrate greater vocabulary acquisition than those using traditional flashcard methods?  
- **RQ2:** Does adaptive feedback improve long-term retention compared to static instructional sequences?  
- **RQ3:** How do learners perceive AI-driven adaptive feedback in terms of helpfulness, transparency, and trust?  
- **RQ4:** What tutoring strategies emerge from RL optimization that differ from traditional approaches?  
- **RQ5:** How does the Wortschatzspiel case study inform RRT as a framework for AI-enhanced education?  

---

## Timeline

- **Jan 2026:** IRB approval, recruitment, system finalization  
- **Feb 2026:** Pilot launch (3-week intervention)  
- **Mar 2026:** Analysis + ASEE GSW submission  
- **Apr–May 2026:** ASEE National paper preparation  
- **Jun–Jul 2026:** ASEE National + JURE presentations  
- **Fall 2026:** Dissertation integration + Fulbright preparation  

---

## Scholarly Contributions

- **AI in Education:** RL applied to micro-tutoring in authentic contexts  
- **Language Learning:** advances CALL via adaptive tutoring  
- **Engineering Education:** supports technical language for international collaboration  
- **Cross-Cultural Research:** enables U.S.–Germany comparative work  
- **Theory:** operationalizes RRT through empirical case studies  

---

## Installation and Setup (Quick Start)

Detailed setup instructions live in this repository’s README. Typical quick start:

1. **Clone repository**
   - `git clone https://github.com/aggiewissenschaftler/Wortschatzspiel-Pilot-2026.git`
2. **Create and activate virtual environment**
   - `python -m venv .venv`
   - `source .venv/bin/activate` (macOS/Linux)  
3. **Install dependencies**
   - `pip install -r requirements.txt`
4. **Configure environment variables**
   - `cp .env.example .env`
5. **Start services (if applicable)**
   - `docker-compose up`

**System requirements (target):** Python 3.11+, Node.js 18+, PostgreSQL 14+, 8 GB RAM minimum (16 GB recommended for RL training).

---

## Ethics and Data Management

This study is expected to operate under Texas A&M University IRB oversight (**Protocol #: pending**). Participants provide informed consent prior to enrollment. Personally identifiable information (PII) is stored separately from performance data, and anonymization protocols are documented in `data_collection/privacy/`.

---

## License

This repository is released under the **MIT License**, permitting free use, modification, and distribution with attribution. The complete license text is included in the `LICENSE` file in the repository root.

> **Note:** If you truly intend dual licensing (MIT for code + CC BY-SA 4.0 for rule files), add a short “Dual licensing” paragraph here **and** include a `LICENSES/` folder with the full CC BY-SA 4.0 text. Otherwise, keep it simple: MIT only.

---

## Citation

If you use this repository in academic work, please cite:

Hallmark, T. F. (2026). *Wortschatzspiel-Pilot-2026: Reinforcement Learning–Enhanced Micro-Tutoring for German Vocabulary Acquisition*. GitHub.  
https://github.com/aggiewissenschaftler/Wortschatzspiel-Pilot-2026

A machine-readable citation is also provided in `CITATION.cff`.

---

## Acknowledgments

This research is supported by the U.S. Department of Veterans Affairs Vocational Rehabilitation and Employment (VR&E) program. The author acknowledges doctoral advisors **Dr. Karen Rambo-Hernández** and **Dr. Ali Bicer** (Texas A&M University) and international mentor **Prof. Dr. Leo van Waveren** (RPTU Kaiserslautern-Landau, Germany) for guidance in developing and positioning the Reflexive Reciprocity Theory framework.

---

## Data Availability

Anonymized pilot data will be shared via OSF upon publication of primary findings. Raw data containing personally identifiable information will be retained securely in accordance with IRB protocols and institutional data retention policies.

---

## Competing Interests

The author declares no competing financial or non-financial interests.

---

## Contact

**Thomas F. Hallmark**  
PhD Candidate, Curriculum & Instruction (Engineering Education)  
Texas A&M University  
Email: thomas.hallmark@tamu.edu  
ORCID: 0009-0002-3124-8140  
GitHub: https://github.com/aggiewissenschaftler

---

## Repository Structure (Revised Tree)

> This tree is intentionally **shorter** than your LaTeX version so it stays readable in GitHub.  
> Put the full “mega-tree” in a separate file like `docs/repo-tree.md` if you want it verbatim.

```text
Wortschatzspiel-Pilot-2026/
|
+-- README.md                 # Overview, installation, usage
+-- LICENSE                   # MIT License (project terms)
+-- CITATION.cff              # Citation metadata for GitHub/Zenodo
+-- requirements.txt          # Python dependencies (pip install -r ...)
+-- docker-compose.yml        # Local dev stack orchestration (docker compose up)
+-- .gitignore                # Files Git should NOT track
+-- .env.example              # Environment variable template (copy to .env)
+-- pyproject.toml            # Python packaging/tool config (optional)
+-- Makefile                  # Convenience commands (optional)
+-- CHANGELOG.md              # Version history (optional but recommended)
+-- CONTRIBUTING.md           # Contribution guidelines (optional but recommended)
|
+-- linguistic_rules/
|   +-- vocab/
|   |   \-- cefr_a1_core.yaml
|   +-- grammar/
|   |   +-- verbs_present.yaml
|   |   +-- modal_verbs.yaml
|   |   +-- sentence_structure.yaml
|   |   +-- negation.yaml
|   |   \-- imperative.yaml
|   \-- phonology/
|       +-- umlauts.yaml
|       \-- compound_stress.yaml
|
+-- rl_agent/
|   +-- environment.py
|   +-- reward_functions.py
|   +-- training/
|   \-- utils/
|
+-- tutoring_interface/
|   +-- frontend/
|   \-- backend/
|
+-- data_collection/
|   +-- raw/
|   +-- processed/
|   \-- privacy/
|
+-- evaluation_metrics/
|   +-- pre_test/
|   +-- post_test/
|   \-- surveys/
|
+-- analysis_scripts/
|   \-- figures/
|
\-- conference_papers/
    +-- ASEE_GSW_2026/
    +-- ASEE_National_2026/
    \-- JURE_2026/