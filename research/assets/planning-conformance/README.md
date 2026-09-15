---
title: Planning conformance fixtures
kind: map
created: "2026-09-14"
tags:
  - c
  - emscripten
  - implementation-planning
  - validation
aliases: []
---

# Planning conformance fixtures

## Purpose

Exercise planning identity, evidence-integrity, and C/Emscripten ABI-boundary
validation without asserting that ERTS or the browser runtime has been built.

## What belongs here

Only bounded synthetic inputs for the planning validators belong here. The C
probe describes fixed-width boundary mechanics; its evidence record is
deliberately `not_run` and cannot close a planning or feasibility gate.
Real execution records use the `*.planning-evidence.json` suffix elsewhere
below `research/assets/`; discovery explicitly excludes this fixture subtree.

## Index

### Subdirectories

- None.

### Files

- [ABI contract](abi-contract.json) — logical C/host boundary allowlist and fixture-only memory requirements.
- [C ABI probe](c-emscripten-abi-probe.c) — bounded offset, generation, request, and completion-state fixture.
- [C ABI probe header](c-emscripten-abi-probe.h) — fixed-width status and function declarations.
- [Expected plan graph](expected-plan-graph.json) — small positive identity and relation oracle.
- [Fixture manifest](fixture-manifest.json) — bounds and SHA-256 identities for every validator input.
- [Native host stub](native-host-stub.c) — native-only assertions for the logical ABI fixture.
- [Synthetic negative cases](synthetic-cases.yaml) — inert malformed inputs and expected rejection codes.
- [Synthetic not-run evidence](synthetic-not-run-evidence.json) — schema-valid evidence shape with no execution claim.
- [Synthetic result bytes](synthetic-result-artifact.txt) — nonempty fixture bytes used only to test pass-evidence binding and rejection paths.

## Maintaining this index

Keep every fixture bounded, aggregate-size-limited, content-addressed, and
visibly synthetic. Keep each scalar manifest reference in the hashed file set,
and update the manifest and nested evidence digests when an input changes.
Never execute an authored command from fixture data, promote a fixture through
the real-record naming convention, or reinterpret validator success as C,
Emscripten, browser, or ERTS evidence.
