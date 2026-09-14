---
title: "2026-09-14 — ERTS WebAssembly corpus recovery and migration"
kind: journal
created: "2026-09-14"
tags:
  - archive-maintenance
  - provenance
  - recovery
  - webassembly
aliases: []
---

# 2026-09-14 — ERTS WebAssembly corpus recovery and migration

## Observations

The ERTS WebAssembly deep-dive bundle was committed in the BlazeX repository as
`b14e8a8` but its pull request was closed and both feature-branch references
were deleted before the intended standalone destination existed. The commit
object remained reachable through local Git history and supplied the recovery
source for this archive.

## Environment

- Source repository: `/home/ducky/code/blazex`
- Source commit: `b14e8a888cc268be29c5dd5db181a3c0a61cfa43`
- Destination repository at recovery time: `/home/ducky/code/erts_wasm`
- Current corpus root after the later directory migration:
  `/home/ducky/code/erts_wasm/research`
- Recovery date: 2026-09-14

## Evidence

The recovery selected the ERTS/Wasm topic map, synthesis, twelve source notes,
feasibility inquiry, and original research journal directly from the source
commit. It did not restore the BlazeX directory-index changes because this
standalone corpus owns new exhaustive indexes.

The runtime-stack map's four links to BlazeX-only maps and planning documents
were replaced with a plain origin-and-project-boundary section. The substantive
runtime findings, citations, security requirements, and evidence limitations
were otherwise preserved.

The standalone scaffold includes the metadata schema, canonical directories,
document templates, archive validator, validator tests, path helper, and a
bounded all-checks runner. The [home map](../10-maps/home.md) is the new entry
point.

Validation from the temporary assembly root passed before installation:

```text
Archive validation passed: 30 completed documents, 13 directories, 160 local links, and 12 source notes checked.
Ran 9 tests
OK
```

The final installed corpus must rerun those checks after copying and Git
initialization; this entry records the observed final result only after that
verification is complete.

## Threads

- Decide whether to rename the BlazeX-framed [feasibility inquiry](../40-inquiries/can-blazex-build-and-own-an-erts-webassembly-runtime-stack.md)
  or preserve it permanently as origin context and open a repository-neutral
  successor.
- Create implementation planning only after the Stage 0 threat-model and
  governance decision is explicitly authorized.

## Follow-ups

- Record the first destination commit and remote only when they exist.
- Preserve source-commit provenance if documents are later renamed or split.
