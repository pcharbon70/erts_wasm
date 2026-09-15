---
title: "2026-09-14 phased planning system adoption"
kind: journal
created: "2026-09-14"
tags:
  - implementation-planning
  - research-session
  - validation
aliases: []
---

# 2026-09-14 phased planning system adoption

## Observation

The existing ERTS-Wasm milestone document was a useful gated roadmap but did
not yet provide separate stream, milestone, phase, task-identity, dependency,
or execution-evidence artifacts. The local Metagraph workspace contained a
more rigorous planning convention that could be adapted without its multi-
project hierarchy or organization-specific authority roles.

## Source inspected

- Local reference repository:
  `/home/ducky/code/metagraph/metagraph-workspace`
- Planning convention: `60-planning/README.md`
- Templates: `templates/milestone-plan-readme.md`,
  `templates/implementation-phase.md`, and
  `templates/phase-execution-record.md`
- Structural tooling: `validate_archive.py` and
  `90-tools/planning-graph/`

This was a local design reference, not implementation or conformance evidence
for ERTS-Wasm. The Metagraph Project census, subject/repository directory
matrix, named governance roles, evidence authorities, and pilot-specific
fixtures were deliberately excluded.

## Adaptation

- Use `research/60-planning/<numbered-stream>/<milestone>/` without an
  intermediate subject, Project, or repository directory.
- Preserve P0–P6 and C1–C10 as stable milestone identities.
- Give each milestone a substantive README with entry decisions, gate/artifact
  mapping, ordered phases, and exit criteria.
- Author detailed phase files only for near-term P0 and P1; later milestones
  retain explicit `decomposition pending` state rather than placeholder files.
- Use stable task IDs, repository-local implementation areas, explicit
  dependencies, and a final integration/evidence-handoff section in every
  phase.
- Keep execution evidence in dated journal records and machine-readable
  artifacts, separate from plan checkboxes.
- Keep validators in Python. Treat C11, Emscripten, generated interpreter
  sources, the Wasm ABI, native/Wasm comparisons, browser behavior, and cleanup
  as the evidence domain being validated rather than rewriting corpus tools in
  C.
- Require validators to treat recorded commands as inert data.

## Evidence boundary

This session changes planning structure and validation contracts only. During
integration verification, the fixed repository-owned fixture was compiled with
`cc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0` using `-std=c11 -Wall -Wextra
-Werror`; its native assertion executable returned zero. That is a development
smoke test of the synthetic fixture, not retained P1 evidence. The session did
not install or run `emcc`, compile ERTS, boot OTP, run a browser test, or
complete any P0/P1 task. Synthetic conformance fixtures and archive validation
cannot satisfy implementation gates.

Final structural verification covered 96 durable documents, 34 archive
directories, 687 local links, and 25 source notes. After the checkbox-semantics
correction on 2026-09-15, the complete 63-test unit suite passed, as did the
fixture verifier over eight streamed and hash-bound inputs, four graph
entities, three relations, sixteen inert negative cases, and one schema-valid
synthetic `not_run` C/Emscripten record. `git diff --check` also passed.

An initial validator draft incorrectly treated every checkmark as a machine-
evidence closure and therefore required phase, section, and subtask boxes to
remain open. Review established that this made the files evidence ledgers
rather than executable plans. Planning profile v1 now treats checked subtasks
as human/agent progress, checked tasks as evidence-bound completion, and
checked sections/phases as consistent roll-ups. An incomplete or newly reopened
child invalidates a checked ancestor; aggregate completion still does not
establish milestone acceptance.

## Follow-ups

- Review the newly decomposed P0 and P1 plans before authorizing execution.
- Assign owners and implementation locations only through an explicit project
  decision.
- Promote any subtask requiring independent evidence or dependencies into a
  stable task rather than adding ambiguous subtask-level gate semantics.

## Connections

- [Planning index](../60-planning/README.md)
- [Runtime roadmap](../60-planning/erts-webassembly-runtime-milestones.md)
- [ADR-0001](../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md)
