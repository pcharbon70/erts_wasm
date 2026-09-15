---
title: "Planning"
kind: map
created: "2026-09-14"
tags:
  - archive-navigation
  - directory-index
  - implementation-planning
aliases: []
---

# Planning (`60-planning`)

## Purpose

Translate accepted research into ordered implementation programs, stable work
identities, executable acceptance gates, and evidence-controlled handoffs.

## What belongs here

Explicitly authorized plans, milestone definitions, and phase plans belong
here. Research recommendations alone do not create implementation authority,
and planning checkboxes do not become evidence merely because a document was
reviewed.

## Directory and identity convention

Planning is flattened because this corpus concerns one repository and one
runtime program. A numbered stream sits directly below `60-planning/`; its
milestones retain their established identifiers:

```text
60-planning/
  01-proof-of-concept/
    p0-<milestone-name>/
  02-in-depth-erts-compatibility/
    c1-<milestone-name>/
```

Every planning directory has an exhaustive `README.md`. Every substantive
milestone has a milestone README. Authored phases use
`phase-01-<descriptive-name>.md`, with phase numbering restarting at `01` in
each milestone. Keep delivered identifiers stable and record supersession
instead of renumbering history.

Start numbered streams from the [planning stream
template](../templates/planning-stream-readme.md), milestones from the
[milestone template](../templates/milestone-plan-readme.md), and phases from
the [implementation phase template](../templates/implementation-phase.md).
Each template includes the required `planning-meta` scaffold; replace every
placeholder and validate the resulting document before adding dependent work.

Create no empty milestone directory or dummy phase file. A substantive
milestone definition may precede phase decomposition, but its README must say
`decomposition pending`, retain every required outcome and gate, and identify
the predecessor evidence needed before decomposition.

## Work hierarchy and descriptions

Each phase contains one numbered checkbox hierarchy: Phase, Section, Task, and
Subtask. Every level receives a description before its children. A task must
name a concrete deliverable, constraints, and a completion check; a subtask
must name its inputs, expected result, and verification or parent-test
reference.

Implementation plans must identify the C/ERTS layer, browser host layer,
artifact boundary, target environment, and host-provided services where
relevant. Task labels use an `area` such as `research-tools`, `c-runtime`,
`browser-host`, `build-release`, `beam-fixtures`, `cross-cutting`, or
`unresolved`. Do not invent an implementation repository, assigned person, or
accepted technology. Add a decision task for choices that block later work.

## Task identity and gate mapping

Every task, including integration and evidence handoff, has a stable symbolic
ID qualified by milestone and phase, such as `p1-p02-fixed-memory`. Task labels
also record area and dependencies. Cross-phase dependencies
link the owning phase and state the exact task ID; an ID is not an automatic
Markdown anchor.

Each milestone README maps every governing obligation, artifact, and
acceptance case to actual phase/task IDs or to `decomposition pending`. Missing
phase plans do not make an obligation optional. Preserve the P0–P6 and C1–C10
identifiers and their existing unchecked delivery state.

## Phase-ending integration tests

The last work section of every phase is named `Phase N Integration Tests`.
Before execution it defines the assembled artifacts or contracts, pinned
fixture and target, negative and exhaustion cases, observable pass/fail
criteria, reproducibility record, evidence destination, and proceed/revise/
blocked handoff.

A contract phase tests the consistency of its combined outputs and rejection
of contradictory inputs. A C/Emscripten phase tests its assembled artifacts in
the declared native or browser environment; archive validation and unit tests
alone are not runtime evidence.

## Status, evidence, and review

Plan review, execution state, and test state are separate. All implementation
checkboxes start unchecked. A human or agent may check a subtask after
performing its bounded action and local verification; the mark records plan
progress and does not close a gate. Check a task only after all of its declared
subtasks are complete and validated pass evidence binds its stable task ID.
Check a section only after every descendant task is checked, and check a phase
only after every section is checked. An unchecked parent with completed
children remains valid, but a checked parent with an incomplete child does not.
Parent roll-ups describe work-hierarchy completion; milestone gate tables and
execution journals remain the acceptance authority. Promote a subtask that
needs independent evidence or dependencies to a stable task.

Execution evidence belongs in a dated journal record linked by task and case
ID. It records the plan baseline, tested revision and dirty state, exact C/
Emscripten/browser/tool versions, flags and configuration, commands, artifact
identities, raw results, limits, failures, and handoff decision. A later merge
revision is distinct from the tested revision.

Any task-closing machine record uses the `*.planning-evidence.json` suffix
beneath `research/assets/`, outside the synthetic
`assets/planning-conformance/` directory. It declares one evidence kind:
`contract_research`, `native_c`, `emscripten_wasm`, or `browser_runtime`.
Archive validation resolves its plan/task/gate identities and support graph,
verifies bounded content and digests, and rejects synthetic or vacuous passes.
The matching directory README must inventory the record and its raw artifacts.

## Verification

Run the aggregate corpus, planning-authoring, and synthetic C/Emscripten
evidence checks:

```bash
python3 research/70-tools/check_all.py
```

When isolating the unit suite, retain the complete test pattern so planning
tests are not skipped:

```bash
python3 -m unittest discover -s research/70-tools -p 'test_*.py'
```

These commands validate authoring structure and inert evidence fixtures. They
do not compile C, invoke Emscripten, start a browser, or satisfy a milestone
gate.

## Index

### Subdirectories

- [01 — Proof of concept](01-proof-of-concept/README.md) — P0–P6 establish and qualify the bounded Erlang/OTP browser proof.
- [02 — In-depth ERTS compatibility](02-in-depth-erts-compatibility/README.md) — C1–C10 expand an accepted proof into a maintained compatibility profile.

### Documents

- [ERTS WebAssembly runtime milestones](erts-webassembly-runtime-milestones.md) — stable roadmap into both planning streams, their ordering rules, and their current evidence boundary.

## Maintaining this index

Inventory every direct child, keep roadmap and stream state synchronized, and
never mark a gate from documentation alone. Validate stable task dependencies,
direct-child indexes, relative links, unchecked prospective work, and evidence
references whenever planning changes.
