---
title: "P6 — Proof-of-concept qualification package"
kind: map
created: "2026-09-14"
tags:
  - directory-index
  - evidence
  - implementation-planning
  - proof-of-concept
  - reproducibility
  - runtime-loading
aliases: []
---

# P6 — Proof-of-concept qualification package

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p6
entities:
  - id: planning.erts_wasm.proof_of_concept.p6
    kind: milestone
    source_anchor: '#p6-proof-of-concept-qualification-package'
  - id: planning.erts_wasm.proof_of_concept.p6.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p6
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept
  - subject: planning.erts_wasm.proof_of_concept.p6
    predicate: contains
    object: planning.erts_wasm.proof_of_concept.p6.plan
  - subject: planning.erts_wasm.proof_of_concept.p6
    predicate: precedes
    object: planning.erts_wasm.in_depth_compatibility.c1
```

## Purpose

Make a bounded go/no-go decision for the compatibility program.

## What belongs here

Independent rebuilds, full artifact and toolchain identity, native/Wasm and
browser evidence, negative findings, resource and fuzz results, SBOM and
provenance, support/non-support surfaces, loading and cancellation matrices,
review of every prior gate and stop condition, and the exact bounded claim
belong here. Production or general OTP/Elixir claims do not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted P5 evidence. Execution and tests: not started. All six source
checkboxes, including the gate, remain unchecked.

## Authoritative inputs

- [P5 plan](../p5-bounded-host-progress-and-lifecycle/README.md) must supply accepted disposable-runtime evidence.
- P0–P5 milestone plans and execution records form the required proof chain.
- [Security, observability, and supply chain](../../../20-notes/components/security-observability-and-supply-chain.md) defines reproducibility, SBOM, provenance, and update evidence boundaries.
- [Runtime roadmap](../../erts-webassembly-runtime-milestones.md) defines the only P6 claim and Program B transition.

## Entry decisions and dependencies

P6 cannot be decomposed or executed until P5 passes and every P0–P5 gate and
stop condition has a linked disposition. Independent rebuild ownership and the
review authority remain unresolved. P6 may reject or pause the candidate; it
must not dilute the claim to force a proceed result.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| P6-A01 | Independently rebuild and assemble exact artifacts, identities, traces, matrices, security evidence, negative findings, and limitations. | `p6-rebuild-receipt`, `p6-evidence-index`, `p6-artifact-graph` | Decomposition pending | Accepted P5-GATE and P0–P5 evidence | Not run / blocked. |
| P6-A02 | Publish and review the exact supported/unsupported surface and the bounded Erlang/OTP-only claim. | `p6-support-matrix`, `p6-claim-review` | Decomposition pending | P6-A01 | Not run / blocked. |
| P6-GATE | P0–P5 evidence reproduces and the complete P6 qualification package is reviewed and accepted in pinned Chrome and Firefox. | Complete P6 qualification package | Decomposition pending | P6-A01 and P6-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Rebuild independently and retain exact commands, artifacts, hashes,
  manifests, imports, Worker inventory, patch ledger, native/Wasm traces,
  loading phase timings, resource slopes, minimized fuzz corpus, sanitizer
  results, SBOM, provenance, negative findings, and limitations.
- [ ] Publish the exact supported and unsupported POC surface.
- [ ] Publish the exact C, Emscripten, TypeScript/JavaScript, Erlang/BEAM, build-
  tool, and generated-artifact matrix. State explicitly that P6 establishes a
  bounded Erlang/OTP semantic baseline and no Elixir support claim.
- [ ] Review every P0–P5 gate and every stop condition.

## Runtime-loading obligations

- [ ] Publish the complete artifact graph, load trace, loading-negative matrix,
  cancellation matrix, module admission report, and update-by-generation rule.

## Ordered phases

Decomposition pending accepted P5 evidence. Expected seams are independent
rebuild/evidence assembly and support-surface/go-no-go review, but the actual
P0–P5 evidence inventory must determine the phase and review boundaries.

## Milestone exit

- [ ] P0–P5 evidence is reproducible in pinned Chrome and Firefox with no active
  stop condition, and the P6 support/unsupported surface, artifact graph,
  loading-negative and cancellation matrices, closure/admission report,
  reproducibility report, limitations, and bounded claim are complete,
  reviewed, and accepted.

**Claim unlocked:** only this statement: the pinned upstream interpreter ERTS
can be loaded, boot the declared matching OTP profile, atomically consume the
single-use authorization that closes further admission, load and execute one
declared ordinary module through its normal pre-ready loader path, execute the
Tier-0 capsule, and be completely terminated in the tested browser/deployment
matrix.

**Excluded claim:** production readiness, general OTP/Elixir compatibility,
network/DOM/storage/crypto support, hot loading, or long-term maintainability.

Closure requires independently reproduced evidence at a named revision,
reviewed acceptance of every package artifact and prior stop condition, and an
explicit proceed/revise/blocked decision. Only accepted P6 evidence may unlock
Program B.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted P5 evidence.

## Maintaining this index

Retain every obligation and unchecked state until phase decomposition maps it
to stable task IDs. Do not broaden the exact P6 claim when summarizing a
successful build, boot, browser run, or qualification package.
