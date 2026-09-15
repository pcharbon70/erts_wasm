---
title: "P4 — Tier-0 semantic capsule"
kind: map
created: "2026-09-14"
tags:
  - compatibility
  - directory-index
  - erlang
  - implementation-planning
  - runtime-loading
  - semantics
aliases: []
---

# P4 — Tier-0 semantic capsule

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p4
entities:
  - id: planning.erts_wasm.proof_of_concept.p4
    kind: milestone
    source_anchor: '#p4-tier-0-semantic-capsule'
  - id: planning.erts_wasm.proof_of_concept.p4.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p4
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept
  - subject: planning.erts_wasm.proof_of_concept.p4
    predicate: contains
    object: planning.erts_wasm.proof_of_concept.p4.plan
  - subject: planning.erts_wasm.proof_of_concept.p4
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p5
```

## Purpose

Prove the minimum meaningful ERTS behavior against the pinned native runtime.

## What belongs here

Ordinary same-toolchain Erlang proof modules, normalized native/Wasm semantic
comparison, bounded pressure, deterministic unsupported behavior, exact module
identity, single-use pre-ready admission through the normal loader path,
publication and failure atomicity, purger/literal behavior, and the transition
to `ready` belong here. Elixir and broad OTP compatibility do not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted P3 evidence. Execution and tests: not started. All eleven
source checkboxes, including the gate, remain unchecked.

## Authoritative inputs

- [P3 plan](../p3-immutable-erts-and-otp-cold-boot/README.md) must supply an accepted immutable boot at `booted-for-qualification`.
- [Processes, schedulers, signals, and timers](../../../20-notes/components/processes-schedulers-signals-and-timers.md) defines the Tier-0 differential surface.
- [OTP boot and BEAM code loading](../../../20-notes/components/otp-boot-and-beam-code-loading.md) defines the ordinary prepare/finish and code-index boundary.
- [OTP and Elixir compatibility profile](../../../20-notes/components/otp-and-elixir-compatibility-profile.md) requires Erlang-first proof artifacts.

## Entry decisions and dependencies

P4 cannot be decomposed or executed until P3 passes. The exact normalizer,
pressure bounds, and implementation locations remain unresolved. The two proof
modules must be byte-identical ordinary Erlang BEAM artifacts for the native
and browser oracle; an Elixir module cannot replace them.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| P4-A01 | Build identical oracle artifacts and compare the complete Tier-0 semantics and bounded-pressure surface. | `p4-poc-beam`, `p4-loader-probe-beam`, `p4-native-wasm-traces` | Decomposition pending | Accepted P3-GATE | Not run / blocked. |
| P4-A02 | Consume exactly one module authorization, close admission, use the upstream prepare/finish path, reject all bypass/failure cases, and preserve code/literal cleanup. | `p4-admission-trace`, `p4-loader-negative-matrix` | Decomposition pending | P4-A01 and `booted-for-qualification` | Not run / blocked. |
| P4-GATE | Normalized traces show no Tier-0 divergence outside predeclared environmental tolerances, and `ready` follows successful qualification. | Complete P4 semantic and loading evidence | Decomposition pending | P4-A01 and P4-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Build `erts_wasm_poc` and `erts_wasm_loader_probe` as ordinary Erlang
  modules with the pinned same-release toolchain; assert byte-identical BEAM
  digests for the native and browser oracle inputs. No Elixir module may replace
  either foundational proof.
- [ ] Compare terms, calls, arithmetic, exceptions, process creation and yield,
  selective receive, message ordering, links, monitors, trapped exits, names,
  timers/cancellation, GC, binaries, ETS ownership/reclamation, application
  boot, and one supervisor child crash/restart.
- [ ] After `erts_wasm_poc` attests that startup never referenced
  `erts_wasm_loader_probe`, atomically consume its exact single-use name/digest
  authorization and close all future admission before invoking the normal
  upstream prepare/finish path; publish and execute it before `ready`.
- [ ] Exercise bounded process, mailbox, timer, binary, allocator, and ETS
  pressure while retaining scheduler and timer progress at `+S 1:1`.
- [ ] Assert deterministic unsupported results for every entry in the finite
  P0 unsupported-operation inventory.

## Runtime-loading obligations

- [ ] Record the name and digest of every participating module and prove no
  undeclared module, alternate loader, direct `code:load_binary`, replacement,
  purge, native library, or unapproved `on_load` path contributes. The harness
  owns the sole pre-ready qualification request; all post-ready requests fail.
- [ ] Confirm direct loading-boundary bypass and name/digest mismatch tests fail
  even for code paths not reached during the positive capsule.
- [ ] Confirm the qualification module is ordinary pinned-toolchain BEAM output,
  becomes visible atomically through active/staging code-index publication, and
  cannot be loaded again after admission closes.
- [ ] Inject failure after authorization consumption and during prepare,
  publication, execution, and each following loader state; every case disposes
  the generation and none reopens admission or reaches `ready`.
- [ ] Verify required internal purger and literal-collector behavior under the
  immutable profile.

## Ordered phases

Decomposition pending accepted P3 evidence. Expected seams are oracle artifact
and trace construction, Tier-0 semantics and bounded pressure, then single-use
admission and code-lifecycle negatives. The actual boot and loader observables
must determine the executable phases.

## Milestone exit

- [ ] Normalized native/Wasm traces contain no Tier-0 process, message, link,
  monitor, GC, ETS, application, or supervision semantic divergence.
  Environmental differences such as clock resolution or suspension behavior
  remain inside separately predeclared tolerances. The qualification harness
  reaches `ready` only after these checks pass.

**Claim unlocked:** minimum semantic evidence, but not yet a completed POC.

**Stop trigger:** any Tier-0 core semantic divergence remains, or its fix
requires replacing upstream semantic machinery. Only predeclared environmental
tolerances may be resolved as profile decisions.

Closure requires exact module identities, native/Wasm traces, pressure results,
loader and failure matrices, and reviewed tolerance and stop-condition
disposition.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted P3 evidence.

## Maintaining this index

Retain every obligation and unchecked state until phase decomposition maps it
to stable task IDs. Do not permit a lower-level loading success or Elixir smoke
module to substitute for this Erlang semantic oracle.
