---
title: "{milestone ID} — {milestone name}"
kind: map
created: "{YYYY-MM-DD}"
tags:
  - archive-navigation
  - directory-index
  - implementation-planning
aliases: []
---

# {milestone ID} — {milestone name}

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.{stream_id}.{milestone_id}
entities:
  - id: planning.erts_wasm.{stream_id}.{milestone_id}
    kind: milestone
    source_anchor: '#{rendered-milestone-heading-anchor}'
  - id: planning.erts_wasm.{stream_id}.{milestone_id}.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.{stream_id}.{milestone_id}
    predicate: belongs_to
    object: planning.erts_wasm.{stream_id}
  - subject: planning.erts_wasm.{stream_id}.{milestone_id}
    predicate: contains
    object: planning.erts_wasm.{stream_id}.{milestone_id}.plan
```

{Replace every brace-delimited value. The IDs must satisfy the planning schema,
the source anchors must match headings in this document, and the parent stream
entity must already exist. Add a `precedes` relation to the next declared
milestone; omit it only for the terminal milestone.}

## Purpose

{Describe the milestone outcome, integrated system boundary, and why its phases
are necessary.}

## What belongs here

{Describe included responsibilities and explicit non-goals. Do not silently
expand the governing roadmap.}

## Planning and delivery state

{Record plan review state, execution state, and gate results separately. New
work and required tests begin unchecked.}

## Authoritative inputs

{Link the parent stream, governing research, requirements, accepted decisions,
target profile, predecessor evidence, and planning convention. Explain each
input's role.}

## Entry decisions and dependencies

| Decision ID | Choice and evaluation criteria | Resolution task / location | Responsible owner | Blocks | State and evidence |
| --- | --- | --- | --- | --- | --- |
| {milestone}-D{NN} | {alternatives and acceptance criteria} | {task and phase link, or decomposition pending} | {assigned owner or unassigned} | {dependent tasks or gates} | {open, or accepted decision and evidence} |

{Keep accepted inputs separate from unresolved choices. Unknown owners,
toolchains, limits, and implementation locations remain explicit.}

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| {governing gate or case} | {observable result and failure boundary} | {required artifacts} | {phase link and stable tasks, or decomposition pending} | {predecessor gates and decisions} | {not run, or actual result and evidence} |

{Map every required artifact and acceptance case. Name exclusions and the
authority for deferral; an unmapped obligation is not optional.}

## Ordered phases

{List only authored phases in dependency order. Include outcome, entry
dependency, plan state, execution state, and evidence link when available. Do
not create placeholder phase files or impose a fixed phase count.}

## Milestone exit

{Define observable combined acceptance, regression and negative-test coverage,
required browsers/environments, evidence, and stop/revise conditions. Identify
the closure reviewer and changes that reopen the gate.}

## Index

### Subdirectories

- None yet.

### Documents

- None yet.

## Maintaining this index

{Inventory every direct child. Keep order, dependencies, status, scope, and
evidence synchronized with the parent stream and governing research. Preserve
delivered IDs and record supersession explicitly.}
