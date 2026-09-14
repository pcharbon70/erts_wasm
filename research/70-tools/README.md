---
title: "Research Tooling"
kind: map
created: "2026-09-14"
tags:
  - archive-navigation
  - directory-index
  - research-tooling
  - validation
aliases: []
---

# Research Tooling (`70-tools`)

## Purpose

Keep structural validation and its focused tests with the corpus.

## What belongs here

Corpus-level validators, shared path helpers, test suites, and bounded runners;
runtime implementation tools belong in their eventual implementation project.

Run the complete suite from the repository root with
`python3 research/70-tools/check_all.py`. The scripts derive the corpus root
from their installed location and do not depend on the caller's working
directory.

## Index

### Subdirectories

- None yet.

### Files

- [All-checks runner](check_all.py) — run archive validation and focused tests.
- [Research path helper](research_paths.py) — locate the standalone corpus.
- [Archive-validator tests](test_validate_archive.py) — exercise schema and link helpers.
- [Archive validator](validate_archive.py) — enforce metadata, inventory, links, and connectivity.

## Maintaining this index

Update this inventory with every tool change and keep tool behavior covered by
focused tests.
