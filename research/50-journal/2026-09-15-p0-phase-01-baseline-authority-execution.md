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

Later on 2026-09-15, the phase was resumed to materialize its exact inputs and
prepare a bounded owner-review packet. That work resolves the missing input
identities but does not stand in for Pascal Charbonneau's independent review.

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

Later assignment: Pascal Charbonneau (`pcharbon70`) accepted assignment to all
P0 reviewer roles on 2026-09-15. The historical observation above remains the
state at execution time; the reviews themselves are still not run.

## P0.1 materialization and source-review resumption

The resumed run used repository base
`1a049f45580af13ea42c31afa40d95320acfe11d` with the active P0 correction
changes still dirty. The machine-readable receipt is
[`p0-phase-01-materialization-receipt.json`](../assets/p0-governed-baseline/phase-01/p0-phase-01-materialization-receipt.json),
and the explicit owner checklist is
[`p0-phase-01-owner-review-packet.json`](../assets/p0-governed-baseline/phase-01/p0-phase-01-owner-review-packet.json).

- The exact OTP source tag, commit, and tree were reproduced in a clean
  detached worktree. The same-source bootstrap reported OTP 29 / ERTS 17.0.6,
  compiled and ran a small Erlang probe, and recorded hashes for the VM,
  bootstrap launcher, boot file, `kernel.app`, `stdlib.app`, and probe BEAM.
- The broader native `make -j20` did not complete: after producing the required
  bootstrap and core applications, it failed in the optional `debugger`
  application because `wx_object` was unavailable with `--without-wx` and
  warnings were errors. This run is evidence for the Phase 1 native-bootstrap
  identity, not a claim that a complete OTP installation passed.
- The immutable linux/amd64 Emscripten image was pulled and verified as emcc
  6.0.9 with the recorded Emscripten revision, Clang 24 component, Binaryen 132,
  Node 24.19.0, npm 11.17.0, and Python 3.12.3.
- Chrome for Testing 153.0.8010.36 and Firefox 155.0 were downloaded from their
  exact official URLs, hashed, extracted, and identity-checked. Firefox's hash
  matched Mozilla's SHA256SUMS. Chrome's immutable archive URL does not expose
  a publisher checksum, so its locally observed digest remains an explicit
  item for independent reproduction.
- The browser-host lock now pins Node 24.19.0, npm 11.17.0, and TypeScript
  6.0.3, including the npm integrity value and independently computed SHA-256.
  TypeScript 7's separate native compiler/toolchain transition is deliberately
  outside the first proof until an ADR review trigger and P1 evidence justify
  it.
- Replaying the runtime-inventory procedures found two corpus errors: the
  pinned tree contains 22 preloaded Erlang sources rather than 23, and the
  recorded `erts/emulator/beam/erl_driver.c` path does not exist. The inventory
  now cites the actual dynamic-driver and port implementation files. All
  retained source paths exist in the pinned tree.

The focused P0 validator now rejects unmaterialized required inputs, missing
browser digests, missing TypeScript toolchain pins, the stale driver path, and
the stale preload count. Its 36 tests pass. At that point P0-A01 remained
review-pending and no `*.planning-evidence.json` file had been created.

## Owner acceptance

On 2026-09-16 Pascal Charbonneau (`pcharbon70`) stated: “I accept the P0.1
owner-review packet and its recorded limitations.” The dated machine-readable
review result is
[`p0-phase-01-owner-review-result.json`](../assets/p0-governed-baseline/phase-01/p0-phase-01-owner-review-result.json).
This accepts the six reviewed contract areas and the Phase 1 handoff for
P0-A01 only. ADR-0001, P0-A02, P0-A03, P0-GATE, and every downstream runtime
claim remain open. Clean revision `aaff05d` was subsequently replayed and bound
by
[`p0-phase-01-acceptance.planning-evidence.json`](../assets/p0-governed-baseline/phase-01/p0-phase-01-acceptance.planning-evidence.json).
That record closes the seven Phase 1 tasks and P0-A01 without expanding the
accepted claim.

The aggregate command `python3 research/70-tools/check_all.py` passed after the
Section 1.2 changes, including the focused P0 tests. `git diff --check` also
passed. The containing commit is the exact Section 1.2 record revision; later
PR and merge revisions are transport history rather than tested inputs.

## Machine-readable evidence

The non-synthetic `contract_research` record above binds exact reviewed inputs,
the owner's acceptance result, validation output digests, clean tested revision
`aaff05d`, all seven Phase 1 tasks, and P0-A01. Its limitations preserve the
native optional-debugger failure, locally reproduced Chrome digest, and absence
of downstream runtime evidence.

## Review and handoff

Disposition: **P0.1 accepted; P0-A01 passed on 2026-09-16**. The owner accepted
the recorded limitations, clean revision `aaff05d` passed the contract and
archive suites, and pass-closing evidence binds all seven Phase 1 tasks. Phase
2 may now consume the exact P0.1 inputs through its formal
`p0-p01-handoff` dependency.

Changes to any pin, trust zone, language owner, runtime category, or pool-size
rule reopen P0-A01 and the corresponding local validation.

## Follow-ups

- Begin formal P0.2 review from the accepted P0.1 handoff without treating its
  later instrumentation experiments as already run.
- Implement and run the census only in the later target/runtime probe.
- Preserve the explicit distinction between draft progression and accepted
  P0 evidence in Phases 2 and 3.
