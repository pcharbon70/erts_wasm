---
title: "C8 — Security and supply-chain hardening"
kind: map
created: "2026-09-14"
tags:
  - directory-index
  - implementation-planning
  - provenance
  - security
  - supply-chain
aliases: []
---

# C8 — Security and supply-chain hardening

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.in_depth_compatibility.c8
entities:
  - id: planning.erts_wasm.in_depth_compatibility.c8
    kind: milestone
    source_anchor: '#c8-security-and-supply-chain-hardening'
  - id: planning.erts_wasm.in_depth_compatibility.c8.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.in_depth_compatibility.c8
    predicate: belongs_to
    object: planning.erts_wasm.in_depth_compatibility
  - subject: planning.erts_wasm.in_depth_compatibility.c8
    predicate: contains
    object: planning.erts_wasm.in_depth_compatibility.c8.plan
  - subject: planning.erts_wasm.in_depth_compatibility.c8
    predicate: precedes
    object: planning.erts_wasm.in_depth_compatibility.c9
```

## Purpose

Freeze and review the candidate profile's security and supply-chain evidence
across build, load, runtime, update, failure, and teardown.

## What belongs here

Threat review, sanitizers, fuzzing, failure injection, CSP and cross-origin
delivery, secret/redaction review, SBOM, provenance, reproducibility, signing,
revocation, downgrade, incident procedures, TypeScript/npm and emitted output,
exact Elixir artifacts, loader/origin/cache/Worker/broker/update trust, and
independent trust roots belong here. Security claims based solely on Wasm
memory isolation do not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted C7 evidence and a frozen candidate profile. Execution and
tests: not started. Three source work items remain unchecked; the source gate
is not run.

## Authoritative inputs

- [C7 plan](../c7-renderer-and-application-lifecycle/README.md) must supply the complete candidate runtime/browser surface.
- [Security, observability, and supply chain](../../../20-notes/components/security-observability-and-supply-chain.md) defines the threat, evidence, and maintenance boundary.
- [Artifact loader and runtime generations](../../../20-notes/components/artifact-loader-and-runtime-generations.md) defines the trusted loading/update path.

## Entry decisions and dependencies

C8 cannot be decomposed or executed until C7 passes and the candidate profile
is frozen. Trusted-component disposition, signing and revocation mechanisms,
incident authority, implementation/evidence locations, and independent
reviewers remain unresolved.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| C8-A01 | Complete threat, sanitizer, fuzz, fault, browser-delivery, secret, signing, downgrade, revocation, and incident evidence for the frozen profile. | `c8-threat-model`, `c8-security-matrix`, `c8-fuzz-corpus` | Decomposition pending | Accepted C7-GATE | Not run / blocked. |
| C8-A02 | Produce complete reproducibility, SBOM, provenance, and trusted-component disposition across C/Emscripten, TypeScript/npm/JavaScript, OTP/BEAM, and admitted Elixir. | `c8-sbom`, `c8-provenance`, `c8-trust-disposition` | Decomposition pending | C8-A01 | Not run / blocked. |
| C8-GATE | Reviewed security evidence covers build, load, runtime, update, failure, and teardown for the frozen candidate profile. | Complete C8 security package | Decomposition pending | C8-A01 and C8-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Complete threat review, sanitizers, fuzzing, failure injection, CSP and
  cross-origin delivery tests, secret/redaction review, SBOM, provenance,
  reproducibility, signing, revocation, downgrade, and incident procedures.
- [ ] Include TypeScript/npm inputs and emitted JavaScript/source maps, plus the
  exact Elixir compiler, sources, dependencies, and BEAM outputs for every
  admitted increment, in provenance and vulnerability-response exercises.
- [ ] Treat the loader, origin, caches, Worker responses, broker, and update path
  as explicit trusted components or prove an independent trust root.

## Ordered phases

Decomposition pending accepted C7 evidence and a frozen candidate profile.
Expected seams are adversarial runtime/delivery security and complete
supply-chain/update-trust qualification, but the final component and artifact
inventory must establish actual phases.

## Milestone exit

**Gate:** reviewed security evidence covers build, load, runtime, update,
failure, and teardown for the frozen candidate profile.

Closure requires reproducible artifact identities, complete SBOM/provenance,
sanitizer and fuzz results, fault and browser-delivery matrices, trusted-base
disposition, signing/revocation/downgrade evidence, incident procedure, and
independent review at a named revision.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted C7 evidence and a frozen profile.

## Maintaining this index

Retain every work item unchecked and the gate not run until decomposition and
evidence exist. Any candidate-profile or trusted-base change reopens the
affected security and provenance evidence.
