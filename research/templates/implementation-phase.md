---
title: "Phase {N} — {phase name}"
kind: note
created: "{YYYY-MM-DD}"
maturity: developing
tags:
  - implementation-planning
aliases: []
---

# Phase {N} — {phase name}

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.{stream_id}.{milestone_id}.phase_{NN}
entities:
  - id: planning.erts_wasm.{stream_id}.{milestone_id}.phase_{NN}
    kind: phase
    source_anchor: '#phase-{N}-{rendered-phase-name-anchor}'
relations:
  - subject: planning.erts_wasm.{stream_id}.{milestone_id}.phase_{NN}
    predicate: belongs_to
    object: planning.erts_wasm.{stream_id}.{milestone_id}.plan
```

{Replace every brace-delimited value. Use a two-digit `NN` matching the
filename, a numeric `N` matching the checkbox hierarchy, and an exact rendered
heading anchor. The parent milestone plan entity must already exist. Add a
`precedes` relation to the next authored phase; omit it only while no successor
phase exists.}

{Describe the phase outcome, system boundary, and why it is needed now.}

Back to milestone: [README](README.md).

## Entry, scope, and dependencies

{Record prerequisites, accepted and unresolved decisions, implementation area,
privilege/host boundary, target fixture, included work, and non-goals. Keep plan
review, execution, and test states separate.}

## Research and acceptance traceability

{Link governing research, decisions, predecessor evidence, the parent stream,
and the planning convention. Map requirements to task and acceptance IDs. Put
all context before the work hierarchy.}

## Task identity, ownership, and dependencies

| Task ID | Area | Responsible owner | Requires | Requirement / artifact / acceptance IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| {milestone}-p{NN}-{task-name} | {c-runtime, browser-host, beam-fixtures, build-release, research-tools, cross-cutting, or unresolved} | {assigned owner or unassigned} | {task IDs or none; keep entry gates in the Entry section} | {governing IDs and links} | {expected evidence; not run until executed} |

{Add one row for every task, including integration and handoff. Resolve missing
prerequisites and dependency cycles before accepting the plan.}

## Planned work

<!-- Add as many described sections, tasks, and subtasks as the work requires.
Keep the Phase N Integration Tests section last. A human or agent may check a
subtask after doing its work and local verification. A task may close only when
all declared subtasks are checked and validated pass evidence binds its stable
ID. A section may close only after all descendant tasks, and a phase only after
all sections. Unchecked parents with completed children are valid. Parent
roll-ups do not replace milestone acceptance. -->

- [ ] {N} Phase — {phase name}.

  {Describe the integrated result and the phase-ending gate.}

  - [ ] {N}.1 Section — {coherent work section}.

    {Describe the section's responsibility and boundary.}

    - [ ] {N}.1.1 Task [id: {milestone}-p{NN}-{task-name}] [area: {implementation-area}] [after: {dependency-IDs-or-none}] — {concrete deliverable}.

      {Describe the artifact or behavior, important constraints, and completion
      check.}

      - [ ] {N}.1.1.1 Subtask — {bounded action}.

        {Describe inputs, action or experiment, expected result, and
        verification.}

  - [ ] {N}.2 Section — Phase {N} Integration Tests.

    {Describe the assembled positive, regression, negative, and handoff gate.}

    - [ ] {N}.2.1 Task [id: {milestone}-p{NN}-integration] [area: cross-cutting] [after: {required-task-IDs}] — Verify the integrated outcome and regressions.

      {Describe the system under test, predeclared criteria and limits, failure
      model, and required native/browser environments.}

      - [ ] {N}.2.1.1 Subtask — Run the integrated acceptance path.

        {Specify fixtures, pinned C/Emscripten/TypeScript/OTP inputs, exact
        command or harness deliverable, observables, and pass/fail criteria.}

      - [ ] {N}.2.1.2 Subtask — Exercise negative cases and inherited behavior.

        {Specify malformed inputs, mismatched toolchains or artifacts, bounds,
        timeouts, cleanup, and expected rejection or containment.}

    - [ ] {N}.2.2 Task [id: {milestone}-p{NN}-handoff] [area: research-tools] [after: {milestone}-p{NN}-integration] — Record evidence and decide phase handoff.

      {Describe the reproducible evidence and review required to proceed,
      revise, or stop. Required blocked or unrun tests keep the gate open.}

      - [ ] {N}.2.2.1 Subtask — Publish the execution record.

        {Link a dated journal and raw artifacts to task/case IDs. Record source
        and plan revisions, dirty state, tool versions, flags, commands,
        outputs, hashes, limits, results, and limitations.}

      - [ ] {N}.2.2.2 Subtask — Review completion and update the milestone.

        {Check every deliverable and gate against evidence and record the next
        phase's entry condition. This does not authorize Git or release work.}
