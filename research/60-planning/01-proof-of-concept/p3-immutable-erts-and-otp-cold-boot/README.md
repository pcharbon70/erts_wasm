---
title: "P3 — Immutable ERTS and OTP cold boot"
kind: map
created: "2026-09-14"
tags:
  - browser
  - directory-index
  - erlang
  - implementation-planning
  - otp
  - runtime-loading
aliases: []
---

# P3 — Immutable ERTS and OTP cold boot

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p3
entities:
  - id: planning.erts_wasm.proof_of_concept.p3
    kind: milestone
    source_anchor: '#p3-immutable-erts-and-otp-cold-boot'
  - id: planning.erts_wasm.proof_of_concept.p3.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p3
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept
  - subject: planning.erts_wasm.proof_of_concept.p3
    predicate: contains
    object: planning.erts_wasm.proof_of_concept.p3.plan
  - subject: planning.erts_wasm.proof_of_concept.p3
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p4
```

## Purpose

Load matching preloads and a minimal immutable OTP release, reach `init`, idle
without blocking the UI agent, and stop at `booted-for-qualification` rather
than publishing `ready`.

## What belongs here

Release closure, immutable MEMFS policy, full-runtime thread census, measured
pthread capacity, topology selection, manifest-bound browser requirements,
controlled ERTS entry, preload and BEAM loading, runtime identity attestation,
delivery negatives, fuzzing, responsiveness, cancellation, and failed-load
cleanup belong here. Tier-0 semantic qualification and readiness do not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted P2 evidence. Execution and tests: not started. All seventeen
source checkboxes, including the gate, remain unchecked.

## Authoritative inputs

- [P2 plan](../p2-interpreter-artifact-and-outer-loader/README.md) must supply the accepted interpreter artifact and generation-owned outer loader.
- [OTP boot and BEAM code loading](../../../20-notes/components/otp-boot-and-beam-code-loading.md) defines release closure and boot boundaries.
- [Worker and pthread topology](../../../20-notes/components/worker-and-pthread-topology.md) defines the topology evidence needed for selection.
- [Artifact loader and runtime generations](../../../20-notes/components/artifact-loader-and-runtime-generations.md) defines the pre-ready state sequence.

## Entry decisions and dependencies

P3 cannot be decomposed or executed until P2 passes. The Worker topology is
selected here only after the complete ERTS thread graph is measured; P1 probe
results alone cannot decide it. The exact preload/release closure and
implementation location remain unresolved until generated from pinned inputs.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| P3-A01 | Build and mount a closed immutable release, start and census the full ERTS role graph, prove pool N/N-1, and select the topology from evidence. | `p3-release`, `p3-closure`, `p3-thread-census`, `p3-topology-decision` | Decomposition pending | Accepted P2-GATE | Not run / blocked. |
| P3-A02 | Trace and enforce the complete controlled load through `booted-for-qualification`, including trust, bounds, bypass, mutation, fuzz, delivery, responsiveness, cancellation, and cleanup cases. | `p3-load-trace`, `p3-negative-matrix`, `p3-fuzz-corpus`, `p3-resource-trace` | Decomposition pending | P3-A01 | Not run / blocked. |
| P3-GATE | Repeatable cold/warm boot and all declared identity, delivery, bounds, responsiveness, wake, and cleanup results pass in pinned Chrome and Firefox. | Complete P3 evidence package | Decomposition pending | P3-A01 and P3-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Build the exact preload set and minimal `kernel`/`stdlib` boot release.
  Start one small harness application named `erts_wasm_poc`; separately package
  an ordinary `erts_wasm_loader_probe` module that is manifest-listed but absent
  from `primLoad` and every startup import/call path.
- [ ] Generate and review the POC's conservative transitive BEAM import,
  native-artifact, NIF/driver, `on_load`, host-import, and capability closure;
  no unresolved edge may enter the release.
- [ ] Populate a verified ephemeral MEMFS root, then enforce write-denied path
  semantics below callers: reject write/create flags, rename, unlink, truncate,
  directory mutation, links, devices, and undeclared paths.
- [ ] Start every required ERTS runtime service and scheduler/dirty/poll/async/
  auxiliary role at the declared settings; separately census ERTS/POSIX roles,
  Emscripten Worker hosts/pool slots, and supervisory agents.
- [ ] Set `PTHREAD_POOL_SIZE` from the measured full-runtime census and prove
  pool `N` boots repeatedly while `N-1` fails promptly with complete cleanup.
- [ ] Compare the two Worker topologies and select one from loading,
  responsiveness, ownership, and teardown evidence.
- [ ] Bind the selected topology, complete Worker graph, required browser
  features, delivery headers, and pinned browser versions to the manifest.

## Runtime-loading obligations

- [ ] Trace preflight, manifest verification, asset acquisition, Wasm compile,
  main-suppressed instantiation, Worker readiness, release mount, explicit ERTS
  entry, preloads, BEAM prepare/commit, code-index/literal effects, OTP boot,
  runtime identity attestation, and `booted-for-qualification` separately.
- [ ] Prove the supervisor invokes the ERTS entry exactly once after mount;
  early, duplicate, stale-generation, or post-failure calls must fail before
  `erl_init` and trigger or preserve cleanup as declared.
- [ ] Enforce module names and digests at the lowest practical ERTS loading
  boundary and directly test undeclared, mismatched, alternate-loader, native,
  and unapproved-`on_load` bypasses. The one qualification module remains
  unopened until P4; no other post-boot load is admitted.
- [ ] Reject missing, corrupt, truncated, oversized, decompression-expanding,
  or skewed release/BEAM assets; alternate boot/path/argv/environment; and
  manifest, memory, Worker, or startup values beyond the P0 bounds matrix.
- [ ] After mount, test every prohibited release-tree mutation and verify that
  all manifest-bound bytes and paths remain unchanged through boot.
- [ ] Fuzz manifest, release archive, boot term, and pre-admission BEAM inputs;
  retain minimized crashes and deterministic rejection cases for native/Wasm
  replay, including atom and expanded-literal resource slopes.
- [ ] Exercise the full ERTS artifact path under CSP, COOP/COEP, CORP/CORS,
  redirect, wrong-MIME, streaming-fallback, cache, service-worker, and
  mixed-generation failures.
- [ ] Measure UI heartbeat/long tasks and transient memory across fetch,
  verification, compilation, Worker startup, instantiation, release mount, and
  boot—not only in the P1 probe.
- [ ] Inject cancellation or failure at every loader state and reach complete
  generation termination.

## Ordered phases

Decomposition pending accepted P2 evidence. Expected seams are immutable
release closure, full-runtime census/topology selection, enforced controlled
boot, and adversarial delivery/cleanup, but P2 artifacts and failures must set
the actual phase boundaries.

## Milestone exit

- [ ] Repeatable cold and warm boot, runtime-identity attestation,
  `booted-for-qualification`, idle, wake, actual-delivery negative tests,
  bounded-input rejection, UI responsiveness, and failed-load cleanup pass in
  pinned Chrome and Firefox without a blocking wait or busy loop.

**Claim unlocked:** boot evidence only.

**Stop trigger:** boot needs ambient files, broad POSIX emulation, mutable code,
unbounded imports, or a main-agent wait.

Closure requires exact release and artifact identities, topology and census
evidence, full load traces, fuzz and negative matrices, browser measurements,
and a reviewed stop-condition disposition.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted P2 evidence.

## Maintaining this index

Retain every obligation and unchecked state until phase decomposition maps it
to stable task IDs. Do not infer readiness, semantic compatibility, or a
topology decision from an isolated boot or earlier synthetic probe.
