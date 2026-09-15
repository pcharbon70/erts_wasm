---
title: "Phase 1 — Target, ABI, and language probes"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - c
  - emscripten
  - implementation-planning
  - typescript
  - webassembly
aliases: []
---

# Phase 1 — Target, ABI, and language probes

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p1.phase_01
entities:
  - id: planning.erts_wasm.proof_of_concept.p1.phase_01
    kind: phase
    source_anchor: '#phase-1-target-abi-and-language-probes'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p1.phase_01
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept.p1.plan
  - subject: planning.erts_wasm.proof_of_concept.p1.phase_01
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p1.phase_02
```

Compile the smallest representative C/Emscripten and TypeScript probes needed
to localize target, ABI, generated-code, and browser-authority risks before
building Worker topology experiments.

Back to milestone: [P1 plan](README.md).

## Entry, scope, and dependencies

Entry requires an accepted `p0-p03-handoff` from the [P0 plan](../p0-governed-baseline-and-proof-contract/README.md).
Plan review is pending; execution and tests are blocked on that evidence. The
C runtime and browser-host implementation locations are unresolved; tasks name
their technical areas without inventing repositories or assignees.

The phase compiles representative generated-interpreter C and narrow protocol
fixtures. It neither attempts a full ERTS link nor treats TypeScript's erased
types as runtime validation or a security boundary.

## Research and acceptance traceability

- [Planning conventions](../../README.md)
- [ADR-0001](../../../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md)
- [ERTS build and BEAM interpreter](../../../20-notes/components/erts-build-and-beam-interpreter.md)
- [Capability broker and browser services](../../../20-notes/components/capability-broker-and-browser-services.md)
- P1-D01, P1-A01, and P1-GATE in the [milestone plan](README.md)

## Task identity, ownership, and dependencies

| Task ID | Area | Responsible owner | Requires | Requirement / artifact / acceptance IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| p1-p01-target-probe | c-runtime | ERTS C-port reviewer unassigned | [p0-p03-handoff](../p0-governed-baseline-and-proof-contract/phase-03-loader-trust-contract-and-p0-acceptance.md) | P1-D01, P1-A01; `p1-target-matrix` | Commands, flags, generated C inputs, compile results, and limitations; not run. |
| p1-p01-host-abi | cross-cutting | C/browser ABI reviewers unassigned | [p0-p03-handoff](../p0-governed-baseline-and-proof-contract/phase-03-loader-trust-contract-and-p0-acceptance.md) | P1-D01, P1-A01; `p1-host-abi-probe` | ABI artifact and import/export/glue report; not run. |
| p1-p01-typescript-authority | browser-host | Browser-host reviewer unassigned | [p0-p03-handoff](../p0-governed-baseline-and-proof-contract/phase-03-loader-trust-contract-and-p0-acceptance.md) | P1-A01; `p1-ts-authority-probe` | Compile-pass/fail fixtures and emitted-JavaScript audit; not run. |
| p1-p01-integration | cross-cutting | Independent reviewer unassigned | p1-p01-target-probe, p1-p01-host-abi, p1-p01-typescript-authority | P1-A01 | Integrated target/ABI/authority matrix; not run. |
| p1-p01-handoff | research-tools | Milestone reviewer unassigned | p1-p01-integration | P1-A01 | Dated execution record and proceed/revise/blocked decision; not run. |

## Planned work

- [ ] 1 Phase — Target, ABI, and language probes.

  Establish whether representative ERTS C and the narrow browser host boundary
  survive the pinned toolchain without hidden target, width, calling-convention,
  or ambient-authority failures.

  - [ ] 1.1 Section — Compile and inspect the target and host boundaries.

    Use bounded fixtures drawn from the pinned source inventory and proposed
    ABI. Retain both successful artifacts and localized failures.

    - [ ] 1.1.1 Task [id: p1-p01-target-probe] [area: c-runtime] [after: p0-p03-handoff] — Probe Emscripten target recognition, Autoconf cross settings, generated interpreter C, function-pointer signatures, dispatch forms, TLS, atomics, locks, condition waits, `setjmp`/`longjmp`, alignment, clocks, poll wakeups, allocator/page behavior, and 32-bit term/pointer assumptions.

      Test every named target dependency with the pinned source, bootstrap, and
      flags. Completion requires reproducible pass/fail results localized to a
      narrow build or platform seam rather than a broad compatibility claim.

      - [ ] 1.1.1.1 Subtask — Build and execute the target-feature probe matrix.

        Record exact compiler/configure commands, inputs, generated files,
        warnings, outputs, failures, and the source location implicated by each
        result; preserve unsupported cases.

    - [ ] 1.1.2 Task [id: p1-p01-host-abi] [area: cross-cutting] [after: p0-p03-handoff] — Compile representative generated-interpreter C and a minimal fixed-width C/JavaScript host-ABI probe with the exact proposed Emscripten flags; record calling convention, integer width, pointer/length ownership, exception or longjmp policy, exports, imports, and generated glue.

      Exercise the actual boundary shape proposed for the runtime and inspect
      the emitted Wasm/JavaScript contract. Completion requires explicit
      ownership and failure behavior for every value and buffer.

      - [ ] 1.1.2.1 Subtask — Compile, run, and inspect the fixed-width ABI fixture.

        Cover minimum/maximum values, offsets and lengths, malformed ranges,
        ownership transfer, cancellation, and any longjmp/exception crossing;
        retain artifact hashes and import/export inspection output.

    - [ ] 1.1.3 Task [id: p1-p01-typescript-authority] [area: browser-host] [after: p0-p03-handoff] — Compile strict TypeScript probes for shared protocol, runtime Worker, and the minimum page supervisor. Include a compile-fail fixture showing that Worker-only code cannot reference DOM declarations. Inspect emitted JavaScript, globals, imports, source maps, runtime validators, and accidental authority; compile-time library separation is not accepted as a security boundary. The renderer remains deferred to C7.

      Prove the build can separate declaration environments while retaining
      runtime validation and an emitted-JavaScript audit. Completion requires
      both the expected compile failure and inspection of actual output.

      - [ ] 1.1.3.1 Subtask — Build the three TypeScript targets and authority-negative fixture.

        Pin compiler and package inputs, retain configurations and source maps,
        enumerate globals/imports, run malformed-message validators, and verify
        the Worker target cannot compile a DOM reference.

  - [ ] 1.2 Section — Phase 1 Integration Tests.

    Test the generated C, host ABI, and emitted browser code as one boundary,
    including malformed values and accidental imports, before Worker topology
    work begins.

    - [ ] 1.2.1 Task [id: p1-p01-integration] [area: cross-cutting] [after: p1-p01-target-probe, p1-p01-host-abi, p1-p01-typescript-authority] — Verify the integrated target, ABI, and language-boundary result.

      Pass only if the pinned toolchain reproduces the fixtures, the ABI has no
      ambiguous width or ownership, emitted glue introduces no undeclared
      import, and runtime validation rejects hostile boundary data.

      - [ ] 1.2.1.1 Subtask — Run the assembled native/Wasm/host probe path.

        Use exact pinned inputs and flags; capture revisions, dirty state,
        compile/link/run commands, artifact hashes, imports/exports, normalized
        output, and browser-host validation results.

      - [ ] 1.2.1.2 Subtask — Exercise ABI and authority negative cases.

        Test overflow, truncation, misalignment, invalid pointers/lengths,
        wrong signatures, stale buffers, unexpected globals/imports, DOM use in
        Worker code, and missing runtime validation with deterministic outcomes.

    - [ ] 1.2.2 Task [id: p1-p01-handoff] [area: research-tools] [after: p1-p01-integration] — Record evidence and decide the Phase 1 handoff.

      Publish actual results and decide whether narrow fixes can proceed to
      Worker experiments, the plan must be revised, or a P1 stop condition is
      active.

      - [ ] 1.2.2.1 Subtask — Publish the dated P1 Phase 1 execution record.

        Link every artifact and failure to P1-A01 and task IDs, with exact
        tools, flags, browsers if used, and limitations.

      - [ ] 1.2.2.2 Subtask — Review completion and update the milestone.

        Keep failed or unrun obligations unchecked and identify the exact
        accepted ABI and generated outputs that Phase 2 may consume.
