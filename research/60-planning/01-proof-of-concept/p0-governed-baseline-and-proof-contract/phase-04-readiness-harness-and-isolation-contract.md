---
title: "Phase 4 — Readiness harness and isolation contract"
kind: note
created: "2026-09-16"
maturity: developing
tags:
  - browser
  - implementation-planning
  - proof-of-concept
  - security
  - test-harness
aliases: []
---

# Phase 4 — Readiness harness and isolation contract

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p0.phase_04
entities:
  - id: planning.erts_wasm.proof_of_concept.p0.phase_04
    kind: phase
    source_anchor: '#phase-4-readiness-harness-and-isolation-contract'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p0.phase_04
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept.p0.plan
  - subject: planning.erts_wasm.proof_of_concept.p0.phase_04
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p0.phase_05
```

Create the smallest reproducible harness that can prove environment readiness
without loading ERTS artifacts. This phase freezes the local HTTPS, certificate,
browser-result, environment, egress, process-ownership, and teardown contracts
before acquiring or executing the pinned fixtures.

Back to milestone: [P0 plan](README.md).

## Entry, scope, and dependencies

Entry requires accepted [P0-A03 evidence](../../../assets/p0-governed-baseline/phase-03/p0-phase-03-acceptance.planning-evidence.json).
The phase may add bounded research tools and fixtures beneath `research/`, but
it does not pull containers or browsers, rebuild OTP, launch a qualification
browser, load Wasm, or claim P0-GATE. Network and privilege mechanisms remain
unresolved until the decision task records an enforceable choice.

The fixture must not add Playwright, Selenium, a package manager dependency, or
a certificate-validation bypass merely for convenience. Prefer a self-reporting
same-origin page and existing pinned runtimes where they satisfy both browsers.
Any new executable dependency must receive an exact identity, owner, acquisition
rule, and evidence role before use.

## Research and acceptance traceability

- [P0 empty-environment contract](../../../assets/p0-governed-baseline/phase-03/p0-empty-environment-contract.json)
- [Accepted bootstrap trust policy](../../../assets/p0-governed-baseline/phase-03/p0-bootstrap-trust.json)
- [P0 role assignments](../../../assets/p0-governed-baseline/phase-03/p0-role-assignments.json)
- [Planning conventions](../../README.md)
- P0-GATE and `p0-p03-integration` in the [milestone plan](README.md)

## Task identity, ownership, and dependencies

| Task ID | Area | Responsible owner | Requires | Requirement / artifact / acceptance IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| p0-p04-harness-contract | cross-cutting | Pascal Charbonneau (`pcharbon70`), security and integration reviewer | p0-p03-loader-contract, p0-p03-bootstrap-trust | `p0-readiness-harness-contract`; P0-GATE | Reviewed decision matrix and digest-bound contract-research evidence; not run. |
| p0-p04-https-fixture | research-tools | Pascal Charbonneau (`pcharbon70`), deployment owner | p0-p04-harness-contract | `p0-static-https-fixture`; P0-GATE | Fixture source, certificate policy, header matrix, and unit/negative results; not run. |
| p0-p04-browser-harness | browser-host | Pascal Charbonneau (`pcharbon70`), browser-test owner | p0-p04-harness-contract, p0-p04-https-fixture | `p0-browser-readiness-harness`; P0-GATE | Launcher/result/teardown harness and non-browser tests; not run. |
| p0-p04-integration | cross-cutting | Independent reviewer required if Pascal produces the evidence | p0-p04-https-fixture, p0-p04-browser-harness | P0-GATE readiness harness | Integrated positive and negative fixture evidence; not run. |
| p0-p04-handoff | research-tools | Pascal Charbonneau (`pcharbon70`), milestone reviewer | p0-p04-integration | Phase 5 entry | Reviewed execution record and proceed/revise/stop disposition; not run. |

## Planned work

- [ ] 4 Phase — Readiness harness and isolation contract.

  Deliver a reviewable, dependency-minimal harness whose authority, network,
  certificate, profile, process, result, timeout, and cleanup behavior are
  explicit before exact environment inputs are replayed.

  - [ ] 4.1 Section — Freeze harness authority and implement the static fixture.

    Keep the preflight independent of ERTS and make every host-side effect
    generation-owned and observable.

    - [ ] 4.1.1 Task [id: p0-p04-harness-contract] [area: cross-cutting] [after: p0-p03-loader-contract, p0-p03-bootstrap-trust] — Select and specify the certificate, browser-result, network-isolation, environment-allowlist, timeout, process-registry, and teardown mechanisms.

      Compare feasible mechanisms against both pinned browsers and the accepted
      trust model. Completion requires exact dependency identities, privilege
      requirements, failure behavior, and a browser-runtime evidence contract.

      - [ ] 4.1.1.1 Subtask — Inventory host and container prerequisites and resolve the minimal dependency set.

        Record exact versions and availability for the container engine, TLS
        tooling, browser runtime libraries, profile certificate tooling, and
        egress enforcement. Reject unpinned convenience dependencies.

      - [ ] 4.1.1.2 Subtask — Freeze isolation, ownership, and result contracts.

        Define the explicit environment allowlist, temporary roots, local-only
        network boundary, process tree ownership, deadlines, result schema,
        raw-log retention, cleanup order, and breach actions.

    - [ ] 4.1.2 Task [id: p0-p04-https-fixture] [area: research-tools] [after: p0-p04-harness-contract] — Implement a deterministic local HTTPS fixture with exact positive and negative delivery modes.

      Serve no ERTS artifact. The fixture must emit the accepted CSP, COOP,
      COEP, CORP, MIME, no-sniff, and no-store policy; provide controlled
      missing/conflicting-header and redirect modes; and expose a bounded
      same-origin result endpoint.

      - [ ] 4.1.2.1 Subtask — Implement the fixture server and versioned preflight page.

        The page reports secure context, isolation, SharedArrayBuffer,
        WebAssembly/thread prerequisites, service-worker controller state,
        supported policy/schema versions, and exact received headers without
        loading runtime bytes.

      - [ ] 4.1.2.2 Subtask — Implement certificate creation/import inputs and negative delivery modes.

        Use a temporary test CA trusted only by the fresh profiles; do not use
        ignore-certificate flags. Add deterministic redirect, missing header,
        conflicting header, wrong MIME, and service-worker-control fixtures.

    - [ ] 4.1.3 Task [id: p0-p04-browser-harness] [area: browser-host] [after: p0-p04-harness-contract, p0-p04-https-fixture] — Implement dependency-minimal browser launch, result collection, deadline, and teardown orchestration.

      Launch only an explicitly provided browser binary and temporary profile.
      Register every process, profile, listener, certificate database, result,
      and timer before effect, and reject stale or duplicate results.

      - [ ] 4.1.3.1 Subtask — Implement browser-neutral invocation and result collection.

        Use a same-origin bounded result submission or another accepted
        dependency-free mechanism. Validate the result schema, browser identity,
        run token, fixture digest, timestamps, and single-use completion.

      - [ ] 4.1.3.2 Subtask — Implement timeout, cancellation, process-tree termination, and artifact retention.

        Prove idempotent cleanup for launch failure, no result, duplicate
        result, fixture failure, and external cancellation without deleting
        evidence needed to explain the failure.

  - [ ] 4.2 Section — Phase 4 Integration Tests.

    Assemble the fixture and harness without running the qualification browsers.
    Test deterministic configuration, dependency closure, authority boundaries,
    malformed results, failure modes, and teardown using local substitutes.

    - [ ] 4.2.1 Task [id: p0-p04-integration] [area: cross-cutting] [after: p0-p04-https-fixture, p0-p04-browser-harness] — Verify the integrated harness contract and inherited P0 trust rules.

      Pass requires exact generated configuration, no ERTS/runtime fetch path,
      bounded inputs and results, local-only authority, deterministic negative
      modes, and zero registered harness resources after every test.

      - [ ] 4.2.1.1 Subtask — Run the integrated fixture and harness acceptance path.

        Start the HTTPS fixture with a non-browser client substitute, exercise
        the positive result path, verify exact headers and certificate inputs,
        and retain commands, logs, configuration, and hashes.

      - [ ] 4.2.1.2 Subtask — Exercise malformed configuration, result, timeout, redirect, header, certificate, and cleanup cases.

        Each case must reject predictably, preserve its raw cause, terminate
        owned processes/listeners, and leave the later browser evidence gate
        explicitly unpassed.

    - [ ] 4.2.2 Task [id: p0-p04-handoff] [area: research-tools] [after: p0-p04-integration] — Record evidence and decide entry to clean input replay.

      A reviewed contract-research record must bind the harness contract,
      source, dependency identities, tests, raw results, limitations, and exact
      revision. Browser execution remains outside this phase.

      - [ ] 4.2.2.1 Subtask — Publish the Phase 4 execution record and evidence.

        Record plan/source revisions, dirty state, commands, versions,
        privileges, environment, ports, certificate identities, outputs,
        digests, negative cases, cleanup, reviewer, and limitations.

      - [ ] 4.2.2.2 Subtask — Review completion and update Phase 5 entry.

        Proceed only if the harness is bounded, dependency-complete, locally
        reproducible, and independently reviewed; otherwise record revise or
        stop without acquiring qualification inputs.
