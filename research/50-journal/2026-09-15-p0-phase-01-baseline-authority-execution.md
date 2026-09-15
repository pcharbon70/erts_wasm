---
title: "2026-09-15 — P0 phase 01 baseline authority execution record"
kind: journal
created: "2026-09-15"
tags:
  - governance
  - implementation-planning
  - proof-of-concept
  - runtime-loading
aliases: []
---

# 2026-09-15 — P0 phase 01 baseline authority execution record

Phase 1 produced review-ready baseline contracts and exercised their local
consistency rules. It did not satisfy P0-A01 because the required independent
pin, security, architecture, ERTS, and concurrency reviews were not available.

## Plan and acceptance baseline

The run implemented [Phase 1](../60-planning/01-proof-of-concept/p0-governed-baseline-and-proof-contract/phase-01-baseline-authority-and-runtime-inventory.md)
tasks `p0-p01-pins` through `p0-p01-handoff` against repository base
`3426f8b` and Section 1.1 commit `ccdebe1`. P0-A01 and P0-GATE remained open.
The validation contract is
[`p0-phase-01-validation-contract.json`](../assets/p0-governed-baseline/phase-01/p0-phase-01-validation-contract.json).

## Environment and provenance

- Pinned OTP source: OTP-29.0.6, commit
  `e07fd07837e5aa845657f5fa340637121e451d47`, tree
  `bddab8fbbe44097258572512d689a5be2ec0686f`.
- Local Python: 3.12.12. Local native Erlang/OTP: release 27. `emcc` and
  `clang` were unavailable.
- Locally installed Chrome 140.0.7339.80 and Firefox 134.0 did not match the
  qualification pins and were not used as substitutes.
- The qualification build image, native OTP 29 bootstrap, Emscripten 6.0.9,
  Chrome 153.0.8010.36, and Firefox 155.0 were specified but not materialized
  or executed.
- Evidence kind: contract/source inspection. No C, Wasm, or browser runtime
  evidence was produced.

## Execution and results

| Task / case IDs | Fixture and exact argv | Expected result | Actual observation | Result | Raw evidence / artifact identity |
| --- | --- | --- | --- | --- | --- |
| `p0-p01-pins`; P0-A01 | `git -C /tmp/erts-wasm-otp-29.0.6 rev-parse HEAD`; `git -C /tmp/erts-wasm-otp-29.0.6 rev-parse 'HEAD^{tree}'`; official release metadata | Exact identities and explicit unresolved materialization | OTP source/tree and Firefox checksum resolved; Chrome digest, native bootstrap, and installed toolchain remain unresolved | partial / review pending | [`p0-baseline-lock.json`](../assets/p0-governed-baseline/phase-01/p0-baseline-lock.json) |
| `p0-p01-runtime-inventory` | pinned-source `rg` and `find` procedures recorded in the inventory | Every required category has a method, finding, and uncertainty | Thirteen categories present; runtime reachability remains unmeasured | pass-local | [`p0-runtime-inventory.json`](../assets/p0-governed-baseline/phase-01/p0-runtime-inventory.json) |
| `p0-p01-thread-census` | authored N/N−1 census contract | Separate role, pthread, Worker, pool, supervisor, and generation identities | Contract authored; instrumentation and experiments not run | pass-local / runtime not run | [`p0-thread-census-contract.json`](../assets/p0-governed-baseline/phase-01/p0-thread-census-contract.json) |
| `p0-p01-integration`; P0-P01-CONTRACT | `python3 research/70-tools/p0_contract_validation.py phase-01` | Five contracts validate without closing acceptance | Passed | pass-local | [`p0-phase-01-validation-report.json`](../assets/p0-governed-baseline/phase-01/p0-phase-01-validation-report.json) |
| `p0-p01-integration`; five negative cases | `python3 -m unittest research/70-tools/test_p0_contract_validation.py` | Reject floating pin, duplicate authority, missing category, topology-derived N, and `+S`-derived N | All deterministic rejection tests passed | pass-local | validation report above |
| `p0-p01-handoff`; independent review | Not run | Assigned reviewers accept every required judgment | Reviewers remain unassigned | not run | No planning-evidence record created |

The aggregate command `python3 research/70-tools/check_all.py` passed after the
Section 1.2 changes, including the focused P0 tests. `git diff --check` also
passed. The containing commit is the exact Section 1.2 record revision; later
PR and merge revisions are transport history rather than tested inputs.

## Machine-readable evidence

No `*.planning-evidence.json` record was created. The local validation report
is deliberately not pass-closing evidence because it has no independent
review and includes required not-run cases.

## Review and handoff

Disposition: **draft progression authorized; P0-A01 remains open**. The user
explicitly authorized preparation and merge of later phase drafts while
evidence-bound tasks remain unchecked. Phase 2 may consume these artifacts as
draft inputs, but this does not satisfy its formal `p0-p01-handoff` dependency.

Independent reviewers must still resolve all pin materializations, accept the
trust and language boundaries, audit the runtime inventory, and approve the
thread-census contract. Changes to any pin, trust zone, language owner, runtime
category, or pool-size rule reopen the corresponding local validation.

## Follow-ups

- Materialize and hash the Chrome archive, build image contents, and native
  OTP 29 bootstrap.
- Assign the independent reviewer roles named by the plan.
- Implement and run the census only in the later target/runtime probe.
- Preserve the explicit distinction between draft progression and accepted
  P0 evidence in Phases 2 and 3.
