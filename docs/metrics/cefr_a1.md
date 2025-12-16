# CEFR A1 Vocabulary – Wortschatzspiel
**Pipeline Metrics and Coverage Summary**  
*Stable snapshot: 2025-12-16*

---

## 1. Purpose and Scope

This document records the construction, validation, and current status of the
**authoritative CEFR A1 vocabulary layer** used by **Wortschatzspiel**.

The CEFR A1 vocabulary serves as the **pedagogical and linguistic baseline**
for the system. All course-specific vocabulary (e.g., from slides or lessons)
is treated as an **overlay** on top of this baseline, not a replacement.

This file exists to ensure:
- transparency of data sources,
- reproducibility of the extraction pipeline,
- and long-term maintainability of the vocabulary layer.

---

## 2. Source Inputs

The following inputs were used to construct the CEFR A1 vocabulary:

- **Goethe A1 Wortliste (PDF)**  
  `docs/cefr/goethe_a1_wortliste.pdf`

- **Raw extracted vocabulary (CSV)**  
  `docs/cefr/goethe_a1_vocab.csv`

- **Canonicalized (deduplicated) vocabulary (CSV)**  
  `docs/cefr/goethe_a1_vocab_canonical.csv`

- **Course wordbank (deduplicated)**  
  `docs/ppt_extracted/wordbank_dedup.csv`

---

## 3. Output Artifacts

The pipeline produces the following authoritative and diagnostic outputs:

- **Authoritative CEFR A1 vocabulary (YAML)**  
  `linguistic_rules/vocab/cefr_a1.yaml`  
  *(lemma-based, part-of-speech aware)*

- **Merged vocabulary debug file (CSV)**  
  `docs/ppt_extracted/cefr_a1_merged.csv`  
  *(used for inspection and validation only)*

---

## 4. Pipeline Metrics

These metrics describe each stage of the extraction and merge pipeline.

- Extracted CSV rows (including header): **6806**
- Extracted vocabulary rows (tokens): **6805**
- Canonical rows  
  *(unique combinations of lemma + grammatical category)*: **1418**
- Course wordbank rows: **1970**
- Final merged vocabulary entries: **2915**

**Canonicalization rule:**  
A vocabulary item is considered unique if the pair  
`(lemma, grammatical category)` is unique.

**Pipeline tag:**  
`cefr-a1-pipeline-stable-2025-12-16`

---

## 5. Vocabulary Coverage

### 5.1 Source Description

- Vocabulary originates from the **Goethe-Zertifikat A1 Wortliste**
- Tokens were extracted from the PDF and processed using **spaCy**
- Each token was reduced to its **lemma** (dictionary form)
- Lemmas were categorized by **part of speech**

The resulting vocabulary is stored as lemma-based entries in:

- `linguistic_rules/vocab/cefr_a1.yaml`

---

### 5.2 Coverage Summary (Planned Metrics)

This subsection defines **where and how vocabulary coverage metrics will be recorded**.
The structure is intentionally present even though exact counts will be computed later.

**Definitions:**
- **Lemma**: the base or dictionary form of a word  
  *(e.g.,* gehen *instead of* geht, ging, gegangen*)*
- **Part of speech**: the grammatical role of a word  
  *(e.g., noun, verb, adjective, article)*

**Metrics to be populated:**
- Total unique lemmas: **TBD**

**Breakdown by grammatical category (part of speech):**
- Nouns: TBD  
- Verbs: TBD  
- Adjectives: TBD  
- Function words  
  *(articles, pronouns, prepositions, conjunctions, particles)*: TBD

These metrics will later be generated automatically from
`cefr_a1.yaml` to support curriculum analysis and validation.

---

## 6. Design Decisions

The following decisions were made intentionally and are considered stable:

- Vocabulary is **lemma-based**, not surface-form-based
- Lemma-based representation improves:
  - pedagogical clarity,
  - grammatical generalization,
  - and long-term maintainability
- Grammar rules operate over **lemmas**, not inflected word forms
- The CEFR A1 vocabulary is treated as **authoritative**
- Course-specific vocabulary is layered as an **overlay**
- Integration with `lex_id` identifiers is **intentionally deferred**
  to avoid premature coupling between vocabulary and grammar systems

---

## 7. Current Status

- ✅ Goethe A1 vocabulary successfully extracted
- ✅ Canonicalization and merge pipeline validated
- ✅ Authoritative A1 vocabulary committed to repository
- ⏳ Grammar rule linkage and automated coverage analytics in progress