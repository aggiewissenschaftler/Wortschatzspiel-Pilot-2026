# Wortschatzspiel YAML Schema (Pilot v0.1)

This document defines the canonical schema for all instructional YAML
files used in the Wortschatzspiel pilot. The schema ensures consistency,
pedagogical transparency, and machine-readability across domains.

---

## Global Metadata (Required)

```yaml
schema_version: "0.1"
cefr_level: "A1"
domain: "articles | verbs | word_order"
language: "de"
description: "Human-readable description of this rule set"