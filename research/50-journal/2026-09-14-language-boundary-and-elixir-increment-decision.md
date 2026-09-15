---
title: "2026-09-14 language boundary and Elixir increment decision"
kind: journal
created: "2026-09-14"
tags:
  - architecture-decision
  - compatibility
  - implementation-language
  - research-session
aliases: []
---

# 2026-09-14 language boundary and Elixir increment decision

## Observations

- The corpus already contained an empty architecture-decision directory and an
  ADR template. The canonical location is
  `research/20-notes/architecture-decisions/`, not a new repository-level
  directory.
- The existing architecture preserved the upstream C interpreter, named a
  TypeScript/JavaScript generation supervisor, used Erlang for the Tier-0 proof,
  and deferred exact-version Elixir admission to C5. It did not yet bind those
  choices in one durable decision.
- Using Elixir as the only first payload would combine the ERTS/OTP proof with
  an independently versioned runtime-library and packaging closure. Erlang is
  retained as the diagnostic baseline; Elixir remains a product language and
  advances through separate compatibility increments.
- The project should be multi-language by trust and ownership boundary rather
  than selecting one language for every component.

## Environment

- Repository: `/home/ducky/code/erts_wasm`
- Branch: `codex/language-boundary-decision`
- Date: 2026-09-14
- Evidence baseline: OTP 29.0.6 / ERTS 17.0.6 commit
  `e07fd07837e5aa845657f5fa340637121e451d47`
- No `emcc`, ERTS/Wasm compile, OTP browser boot, Rust target, TypeScript host,
  or Elixir browser execution was run in this session.

## Evidence

- Re-inspected the corpus's ERTS build, loader, broker, compatibility, canonical
  architecture, and milestone conclusions through repository search.
- Re-checked the official TypeScript documentation for static checking, erased
  types, and separate DOM/WebWorker libraries.
- Re-checked the official Rust `wasm32-unknown-emscripten` target documentation
  for target tier, ABI-setting alignment, standard-library rebuild guidance,
  and CI limitations, plus the Rustonomicon's unsafe-boundary guidance.
- Reused the corpus's pinned upstream OTP and Emscripten source notes rather
  than turning toolchain documentation into build evidence.
- Recorded [ADR-0001](../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md)
  as proposed and added unchecked P0/P1/P2/P4/P6/C1/C5/C8/C10 obligations.
- Archive validation passed with 69 completed documents, 14 directories, 471
  local links, and 25 source notes checked. All 11 validator unit tests passed,
  and `git diff --check` reported no whitespace errors. These results establish
  corpus integrity only; they do not accept the ADR or complete an
  implementation gate.

## Threads

- The exact C dialect and Emscripten ABI flags remain outputs of P0/P1, not an
  assumption in the ADR.
- A Rust component becomes credible only when it owns its memory behind a small
  ABI and produces a measured benefit over C or TypeScript alternatives.
- The first Elixir increment must distinguish “one module executed” from an
  admitted `elixir` runtime profile and from representative application support.
- Compiler and package-manager inputs for TypeScript and Elixir become part of
  the trusted, versioned supply chain even though their emitted artifacts are
  JavaScript and BEAM.

## Follow-ups

- Run the P1 C/Emscripten and TypeScript authority-separation probes before
  accepting ADR-0001.
- At C1, select candidate exact Elixir versions only for closure discovery.
  Admission begins within C5 only after P6 is accepted, Tier 1 passes, and
  ELX-0 closes the candidate profile; each later increment depends on the
  preceding one.
- Repeat archive and link validation whenever ADR-0001 or its referenced gates
  change.
