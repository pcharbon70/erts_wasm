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

Subtask checkmarks are human/agent progress assertions and require no separate
machine record. Task checkmarks require every declared subtask plus validated
pass evidence bound to the stable task ID. Checked sections require all
descendant tasks, and a checked phase requires all sections; unchecked parents
with completed children remain valid. Free-form checked boxes are rejected.
These roll-ups do not establish milestone acceptance. Real pass records bind
each command and observation to nonempty, digest-verified result artifacts that
cannot alias declared sources.

## Index

### Subdirectories

- None yet.

### Files

- [All-checks runner](check_all.py) — run every archive, unit, and fixture check even when an earlier check fails.
- [Planning authoring schema](planning-authoring-v1.schema.json) — machine-readable identities and relations for streams, milestones, plans, and phases.
- [Planning evidence policy](planning-evidence-profile-v1.yaml) — role-neutral provenance, review, replay, discovery, size bounds, and contract-binding requirements.
- [Planning evidence schema](planning-evidence-v1.schema.json) — bounded shape for contract/research, native-C, Emscripten-Wasm, and browser-runtime evidence.
- [Planning validation helpers](planning_validation.py) — validate full task projections and graphs, stream hashes, load digest-bound contracts, and discover real `*.planning-evidence.json` records below `research/assets/` while excluding conformance fixtures.
- [Research path helper](research_paths.py) — locate the standalone corpus.
- [Planning-validator tests](test_planning.py) — exercise phase structure, iterative graphs, bounded evidence, contract binding, discovery, and inert command fixtures.
- [Archive-validator tests](test_validate_archive.py) — exercise schema and link helpers.
- [Archive validator](validate_archive.py) — enforce metadata, inventory, links, planning graphs, evidence support references, and evidence-bound checked tasks.
- [Planning fixture verifier](verify_planning_fixtures.py) — run production validators over hash-closed synthetic C/Emscripten inputs without executing authored commands.

## Maintaining this index

Update this inventory with every tool change and keep tool behavior covered by
focused tests.
