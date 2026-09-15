---
title: "C10 — Maintained ERTS-Wasm release profile"
kind: map
created: "2026-09-14"
tags:
  - compatibility
  - directory-index
  - implementation-planning
  - maintenance
  - release
  - supply-chain
aliases: []
---

# C10 — Maintained ERTS-Wasm release profile

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.in_depth_compatibility.c10
entities:
  - id: planning.erts_wasm.in_depth_compatibility.c10
    kind: milestone
    source_anchor: '#c10-maintained-erts-wasm-release-profile'
  - id: planning.erts_wasm.in_depth_compatibility.c10.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.in_depth_compatibility.c10
    predicate: belongs_to
    object: planning.erts_wasm.in_depth_compatibility
  - subject: planning.erts_wasm.in_depth_compatibility.c10
    predicate: contains
    object: planning.erts_wasm.in_depth_compatibility.c10.plan
```

## Purpose

Prove or reject sustainable ownership of the exact ERTS-Wasm release profile
through real upstream, toolchain, browser, language-profile, signing, rollback,
and independent-rebuild rehearsals.

## What belongs here

At least two upstream ERTS/OTP rebases, emsdk/toolchain update, browser
regression response, key rotation/revocation, rollback, independent rebuild,
TypeScript/JavaScript host rebuild, admitted Elixir profile update, patch and
generated-artifact ownership, and approved versioning, deprecation,
compatibility, incident, and release policy belong here. Unsupported long-term
claims without rehearsals do not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted C9 evidence and selected maintenance windows. Execution and
tests: not started. Four source work items remain unchecked; the source gate is
not run.

## Authoritative inputs

- [C9 plan](../c9-performance-and-browser-qualification/README.md) must supply the measured supported profile and browser matrix.
- [Security, observability, and supply chain](../../../20-notes/components/security-observability-and-supply-chain.md) defines update, provenance, and incident obligations.
- [ADR-0001](../../../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md) defines language/toolchain ownership and reopening triggers.
- [Runtime roadmap](../../erts-webassembly-runtime-milestones.md) permits pause or rejection when ownership is unsustainable.

## Entry decisions and dependencies

C10 cannot be decomposed or executed until C9 passes. Exact upstream and
toolchain update candidates, browser regression fixture, key lifecycle,
maintenance ownership, implementation location, release authority, and review
windows remain unresolved. Policy approval follows rehearsal evidence rather
than preceding it as an unsupported claim.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| C10-A01 | Rehearse two upstream rebases and the declared toolchain, browser, signing, rollback, independent rebuild, TypeScript host, and admitted Elixir update paths. | `c10-update-rehearsals`, `c10-independent-rebuilds` | Decomposition pending | Accepted C9-GATE | Not run / blocked. |
| C10-A02 | Reduce or own every patch/generated artifact and approve sustainable versioning, deprecation, compatibility, incident, and release policy through an ADR. | `c10-patch-ledger`, `c10-release-adr` | Decomposition pending | C10-A01 | Not run / blocked. |
| C10-GATE | Project accepts a precise support surface and sustainable update obligation, or pauses/rejects the candidate with retained evidence. | Complete C10 maintenance package | Decomposition pending | C10-A01 and C10-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Rehearse at least two upstream ERTS/OTP rebases, an emsdk/toolchain update,
  a browser regression response, a signing-key rotation/revocation, rollback,
  and independent rebuild.
- [ ] Rehearse the pinned TypeScript/JavaScript host build and, after C5
  admission, the exact Elixir compiler/profile update without silently
  broadening authority or compatibility.
- [ ] Reduce or formally own every patch and generated artifact.
- [ ] Approve versioning, deprecation, compatibility, incident, and release
  policies through an architecture decision.

## Ordered phases

Decomposition pending accepted C9 evidence and selected maintenance inputs.
Expected seams are rebase/update/recovery rehearsals, then patch ownership and
release-policy acceptance. Actual update candidates and incident scenarios
must establish the phases.

## Milestone exit

**Gate:** the project accepts a precise support surface and sustainable update
obligation—or pauses/rejects the candidate with retained evidence.

Closure requires all update and recovery receipts, independent rebuilds,
patch/generated-artifact disposition, measured effort and regressions,
accepted release-policy ADR or a retained rejection decision, and independent
review at exact revisions.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted C9 evidence and selected rehearsal inputs.

## Maintaining this index

Retain every work item unchecked and the gate not run until decomposition and
evidence exist. A successful single rebase, rebuild, browser fix, or key
rotation does not establish maintainability.
