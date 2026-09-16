---
title: "Phase 6 — Pinned browser readiness and P0 gate evidence"
kind: note
created: "2026-09-16"
maturity: developing
tags:
  - browser
  - implementation-planning
  - proof-of-concept
  - runtime-loading
  - security
aliases: []
---

# Phase 6 — Pinned browser readiness and P0 gate evidence

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p0.phase_06
entities:
  - id: planning.erts_wasm.proof_of_concept.p0.phase_06
    kind: phase
    source_anchor: '#phase-6-pinned-browser-readiness-and-p0-gate-evidence'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p0.phase_06
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept.p0.plan
```

Run the accepted static readiness fixture in exact Chrome and Firefox builds,
prove secure delivery and clean-profile behavior, exercise deployment-negative
cases, and publish the browser evidence consumed by the existing P0 integration
and handoff tasks.

Back to milestone: [P0 plan](README.md).

## Entry, scope, and dependencies

Entry requires accepted `p0-p05-handoff` and the exact Phase 4 harness revision.
Each positive run uses a new empty profile, a temporary trusted test CA, the
local fixture origin as the only permitted network destination, and no ERTS,
Wasm, generated JavaScript, release, or BEAM artifact. Dedicated negative
profiles may be prepared only for the service-worker and certificate cases and
must never be reused as positive profiles.

This phase proves browser/deployment readiness, not runtime loading. Failure to
provide recursive isolation headers, verified-Blob-compatible CSP, service-
worker exclusion, trusted local TLS, or complete process/profile cleanup invokes
the accepted P0 stop/revise rule.

## Research and acceptance traceability

- [Accepted bootstrap trust policy](../../../assets/p0-governed-baseline/phase-03/p0-bootstrap-trust.json)
- [P0 browser and source pins](../../../assets/p0-governed-baseline/phase-01/p0-baseline-lock.json)
- [P0 empty-environment contract](../../../assets/p0-governed-baseline/phase-03/p0-empty-environment-contract.json)
- [Phase 4 harness plan](phase-04-readiness-harness-and-isolation-contract.md)
- [Phase 5 clean replay plan](phase-05-clean-input-and-container-replay.md)

## Task identity, ownership, and dependencies

| Task ID | Area | Responsible owner | Requires | Requirement / artifact / acceptance IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| p0-p06-browser-materialization | browser-host | Pascal Charbonneau (`pcharbon70`), browser-test owner | p0-p05-handoff | `p0-browser-fixture-receipt`; P0-GATE | Exact binary/archive/profile evidence; not run. |
| p0-p06-tls-profiles | browser-host | Pascal Charbonneau (`pcharbon70`), deployment owner | p0-p06-browser-materialization | `p0-browser-trust-fixture`; P0-GATE | Temporary CA/profile/header evidence; not run. |
| p0-p06-positive-preflight | browser-host | Pascal Charbonneau (`pcharbon70`), browser/Wasm reviewer | p0-p06-tls-profiles | `p0-browser-readiness-matrix`; P0-GATE | Chrome/Firefox pass records; not run. |
| p0-p06-negative-preflight | browser-host | Pascal Charbonneau (`pcharbon70`), security reviewer | p0-p06-tls-profiles | `p0-browser-negative-matrix`; P0-GATE | Deterministic browser rejection records; not run. |
| p0-p06-cleanup | cross-cutting | Pascal Charbonneau (`pcharbon70`), lifecycle reviewer | p0-p06-positive-preflight, p0-p06-negative-preflight | `p0-readiness-cleanup-report`; P0-GATE | Process/profile/listener/certificate cleanup evidence; not run. |
| p0-p06-integration | cross-cutting | Independent reviewer required if Pascal produces the evidence | p0-p06-positive-preflight, p0-p06-negative-preflight, p0-p06-cleanup | P0-GATE browser readiness | Reviewed browser-runtime evidence; not run. |
| p0-p06-handoff | research-tools | Pascal Charbonneau (`pcharbon70`), milestone reviewer | p0-p06-integration | `p0-p03-integration` | Accepted readiness receipt and proceed/revise/stop disposition; not run. |

## Planned work

- [ ] 6 Phase — Pinned browser readiness and P0 gate evidence.

  Produce exact Chrome and Firefox observations for the static trust/readiness
  surface, retain every negative result, and return a reviewed readiness receipt
  to the existing P0 integration task.

  - [ ] 6.1 Section — Materialize exact browsers and per-run trust/profile roots.

    Browser identity, archive integrity, profile emptiness, certificate trust,
    local origin, environment, and launch arguments must be visible in every run.

    - [ ] 6.1.1 Task [id: p0-p06-browser-materialization] [area: browser-host] [after: p0-p05-handoff] — Verify and extract Chrome for Testing 153.0.8010.36 and Firefox 155.0 from the accepted archives.

      Reject locally installed substitutes. Completion requires archive hash,
      extracted binary hash and reported version, runtime-library resolution,
      launch argv, and a fresh empty profile root for each attempt.

      - [ ] 6.1.1.1 Subtask — Materialize and identify the exact Chrome fixture.

        Reproduce the accepted locally observed archive SHA-256 from the exact
        immutable URL, hash the extracted binary, and record the version without
        reusing a developer profile or cache.

      - [ ] 6.1.1.2 Subtask — Materialize and identify the exact Firefox fixture.

        Verify the official SHA256SUMS entry, hash the extracted binary, record
        the version, and create a separately owned empty profile.

    - [ ] 6.1.2 Task [id: p0-p06-tls-profiles] [area: browser-host] [after: p0-p06-browser-materialization] — Create per-run profiles that trust only the temporary test CA in addition to browser defaults and bind them to the local-only fixture origin.

      Do not use ignore-certificate flags. Record CA/server certificate hashes,
      subject/alternative names, validity, profile database commands, local
      port, run token, and profile pre/post inventory.

      - [ ] 6.1.2.1 Subtask — Create and import the temporary CA and server certificate into both fresh profiles.

        Verify a successful trusted HTTPS navigation and a deterministic failure
        for an untrusted or wrong-host certificate before testing headers.

      - [ ] 6.1.2.2 Subtask — Enforce local-origin-only browser networking and explicit launch environments.

        Prove that the fixture origin is reachable while an external canary and
        browser background request cannot escape the selected egress boundary.

  - [ ] 6.2 Section — Execute positive and adversarial browser preflight.

    Use the same fixture and result schema in both browsers. Never convert a
    failure into a browser-specific waiver after observing results.

    - [ ] 6.2.1 Task [id: p0-p06-positive-preflight] [area: browser-host] [after: p0-p06-tls-profiles] — Run the complete static readiness preflight in empty Chrome and Firefox profiles.

      Pass requires secure context, cross-origin isolation, SharedArrayBuffer,
      WebAssembly and required thread features, no controlling service worker,
      accepted policy/schema versions, exact response headers and MIME, one
      bounded result, and no runtime artifact request.

      - [ ] 6.2.1.1 Subtask — Execute and record the Chrome positive matrix.

        Retain archive/binary/profile/CA/fixture identities, argv, environment,
        network policy, console and result data, requests, timing, exit, and
        teardown.

      - [ ] 6.2.1.2 Subtask — Execute and record the Firefox positive matrix.

        Record the same fields and apply the same pass criteria; differences
        require a predeclared normalization or a failed/revise disposition.

    - [ ] 6.2.2 Task [id: p0-p06-negative-preflight] [area: browser-host] [after: p0-p06-tls-profiles] — Exercise the accepted browser/deployment trust failures in both pinned browsers.

      Cover insecure or untrusted TLS, missing/conflicting COOP/COEP/CORP/CSP,
      wrong MIME, redirect, cache-policy drift, existing service-worker control,
      controller change, duplicate/stale/malformed result, timeout, and fixture
      termination. Each must fail before readiness.

      - [ ] 6.2.2.1 Subtask — Run header, TLS, MIME, redirect, cache, and result-protocol negative cases.

        Preserve exact request/response and browser observations and verify no
        alternate URL, cached success, or result fallback is accepted.

      - [ ] 6.2.2.2 Subtask — Run service-worker, cancellation, timeout, crash, and stale-completion cases.

        Use dedicated negative profiles where necessary, arm controller-change
        cancellation before acquisition, and verify the whole harness generation
        terminates without accepting a late result.

    - [ ] 6.2.3 Task [id: p0-p06-cleanup] [area: cross-cutting] [after: p0-p06-positive-preflight, p0-p06-negative-preflight] — Prove deterministic cleanup after every positive and negative readiness run.

      Account for browser descendants, profiles, certificate databases, fixture
      listeners, result requests, timers, logs, namespaces, and temporary roots.

      - [ ] 6.2.3.1 Subtask — Capture pre-run, post-result, post-termination, and settled resource censuses.

        Apply the accepted settling observations and fail on an unowned browser,
        listener, profile lock, namespace, request, or positive resource slope.

      - [ ] 6.2.3.2 Subtask — Verify idempotent cleanup and evidence retention.

        Re-run cleanup after success, timeout, crash, and cancellation; retain
        immutable evidence while removing credentials and ephemeral authority.

  - [ ] 6.3 Section — Phase 6 Integration Tests.

    Reproduce the complete clean source/container/browser/header readiness path
    and bind it to P0-A01 through P0-A03 without running P1 or ERTS/Wasm.

    - [ ] 6.3.1 Task [id: p0-p06-integration] [area: cross-cutting] [after: p0-p06-positive-preflight, p0-p06-negative-preflight, p0-p06-cleanup] — Verify the assembled P0 readiness environment and all inherited regressions.

      Pass requires accepted Phase 4 and 5 evidence, both exact browsers passing
      from empty profiles, every required negative case failing closed, complete
      cleanup, reproducible commands, and no active P0 stop condition.

      - [ ] 6.3.1.1 Subtask — Replay the complete positive environment-readiness recipe from clean roots.

        Bind plan/source revisions, input and tool identities, native bootstrap,
        container isolation, browsers, profiles, TLS, headers, preflight results,
        raw artifacts, hashes, and teardown in a browser-runtime record.

      - [ ] 6.3.1.2 Subtask — Replay inherited identity, authority, delivery, timeout, and cleanup failures.

        Demonstrate that a stale input, ambient host dependency, external egress,
        browser substitution, deployment-policy failure, or leaked resource
        prevents the readiness receipt from passing.

    - [ ] 6.3.2 Task [id: p0-p06-handoff] [area: research-tools] [after: p0-p06-integration] — Publish reviewed readiness evidence and hand it back to `p0-p03-integration`.

      This handoff does not itself close P0-GATE. The existing Phase 3 integration
      and milestone-review tasks must combine it with P0-A01 through P0-A03 and
      issue the final proceed/revise/stop disposition.

      - [ ] 6.3.2.1 Subtask — Publish the Phase 6 execution journal, raw artifacts, readiness receipt, and machine evidence.

        Record every exact identity, command, environment, privilege, request,
        observation, failure, cleanup result, reviewer, limitation, and digest.

      - [ ] 6.3.2.2 Subtask — Obtain independent review and update the P0 integration entry state.

        A different reviewer must accept owner-produced evidence. On acceptance,
        unblock only `p0-p03-integration`; on failure, record revise or stop and
        keep P0-GATE and P1 entry closed.
