---
title: "Phase 5 — Clean input and container replay"
kind: note
created: "2026-09-16"
maturity: developing
tags:
  - build-environment
  - implementation-planning
  - proof-of-concept
  - reproducibility
  - supply-chain
aliases: []
---

# Phase 5 — Clean input and container replay

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p0.phase_05
entities:
  - id: planning.erts_wasm.proof_of_concept.p0.phase_05
    kind: phase
    source_anchor: '#phase-5-clean-input-and-container-replay'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p0.phase_05
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept.p0.plan
  - subject: planning.erts_wasm.proof_of_concept.p0.phase_05
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p0.phase_06
```

Replay every accepted build/source input from declared origins into a clean,
bounded environment and prove that the pinned native bootstrap and Emscripten
toolchain are ready for P1 without compiling the P1 target probe.

Back to milestone: [P0 plan](README.md).

## Entry, scope, and dependencies

Entry requires accepted `p0-p04-handoff`. Acquisition may access only the
declared HTTPS origins. Verification and build execution must run with network
disabled, explicit environment variables, declared read-only source mounts,
and isolated writable output roots. Required elevated container or namespace
authority must be recorded before use.

This phase verifies inputs and the same-source native bootstrap. It does not
cross-compile ERTS, build a Wasm artifact, run a browser, select a topology, or
claim runtime compatibility. A broader optional OTP build failure does not
invalidate the required bootstrap if the accepted bootstrap outputs pass and
the limitation is retained.

## Research and acceptance traceability

- [Accepted P0 baseline lock](../../../assets/p0-governed-baseline/phase-01/p0-baseline-lock.json)
- [Phase 1 materialization receipt](../../../assets/p0-governed-baseline/phase-01/p0-phase-01-materialization-receipt.json)
- [P0 asset/dependency/patch ledger](../../../assets/p0-governed-baseline/phase-03/p0-asset-dependency-patch-ledger.json)
- [P0 empty-environment contract](../../../assets/p0-governed-baseline/phase-03/p0-empty-environment-contract.json)
- [Phase 4 plan](phase-04-readiness-harness-and-isolation-contract.md)

## Task identity, ownership, and dependencies

| Task ID | Area | Responsible owner | Requires | Requirement / artifact / acceptance IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| p0-p05-acquire-verify | build-release | Pascal Charbonneau (`pcharbon70`), build/reproducibility reviewer | p0-p04-handoff | `p0-clean-input-ledger`; P0-GATE | Exact acquisition and verification receipt; not run. |
| p0-p05-toolchain-container | build-release | Pascal Charbonneau (`pcharbon70`), build-release owner | p0-p05-acquire-verify | `p0-clean-toolchain-replay`; P0-GATE | Image/platform/tool identity evidence; not run. |
| p0-p05-native-bootstrap | c-runtime | Pascal Charbonneau (`pcharbon70`), ERTS C-port reviewer | p0-p05-acquire-verify, p0-p05-toolchain-container | `p0-clean-native-bootstrap`; P0-GATE | Same-source bootstrap build/probe evidence; not run. |
| p0-p05-execution-sandbox | cross-cutting | Pascal Charbonneau (`pcharbon70`), security reviewer | p0-p05-toolchain-container | `p0-clean-execution-sandbox`; P0-GATE | Environment/mount/network/process audit; not run. |
| p0-p05-integration | cross-cutting | Independent reviewer required if Pascal produces the evidence | p0-p05-native-bootstrap, p0-p05-execution-sandbox | P0-GATE clean build readiness | Integrated replay and negative evidence; not run. |
| p0-p05-handoff | research-tools | Pascal Charbonneau (`pcharbon70`), milestone reviewer | p0-p05-integration | Phase 6 entry | Reviewed replay receipt and disposition; not run. |

## Planned work

- [ ] 5 Phase — Clean input and container replay.

  Produce a clean, independently reviewable build-readiness receipt whose
  exact sources, container, tools, environment, mounts, outputs, and failures
  can be replayed without relying on the developer host.

  - [ ] 5.1 Section — Acquire and verify exact immutable inputs.

    Separate networked acquisition from network-disabled verification and
    execution. Treat every cached input as untrusted until its accepted
    identity is reproduced.

    - [ ] 5.1.1 Task [id: p0-p05-acquire-verify] [area: build-release] [after: p0-p04-handoff] — Acquire the pinned OTP source, build image, Chrome archive, Firefox archive/checksum, and any accepted harness dependency from declared origins.

      Completion requires exact URLs or registry references, tag/commit/tree or
      platform-manifest identities, SHA-256 values, sizes, acquisition logs,
      and a clean separation between downloaded bytes and verified inputs.

      - [ ] 5.1.1.1 Subtask — Materialize and verify source and container identities.

        Reproduce OTP tag, commit, and tree; pull the exact linux/amd64 image by
        digest; reject tags, redirects, wrong platforms, and identity drift.

      - [ ] 5.1.1.2 Subtask — Materialize and verify browser and harness inputs.

        Reproduce the recorded Chrome local digest, Firefox official checksum,
        archive identities, and any accepted certificate/profile dependency.

    - [ ] 5.1.2 Task [id: p0-p05-toolchain-container] [area: build-release] [after: p0-p05-acquire-verify] — Reproduce the pinned container toolchain and declared read-only input boundary.

      Run the exact linux/amd64 image, record its immutable image ID, and verify
      `emcc`, Clang, Binaryen, Node, npm, and Python against the accepted ledger.
      The verified canonical source input remains read-only; copy it into a
      declared ephemeral writable working root when a tool must modify its
      tree. The P1 target probe must not be compiled.

      - [ ] 5.1.2.1 Subtask — Inspect the image, platform manifest, entrypoint, user, mounts, and internal tool identities.

        Fail on platform emulation ambiguity, floating image identity, a
        writable canonical source-input mount, undeclared host paths, or
        tool-version drift.

      - [ ] 5.1.2.2 Subtask — Prove network-disabled verification and a clean output root.

        Re-run identity probes with acquisition disabled, a new writable output
        directory, and only the declared read-only inputs and environment.

  - [ ] 5.2 Section — Rebuild the same-source native bootstrap in the execution sandbox.

    Establish the native oracle input without treating a broad optional OTP
    build as a gate or importing the host's installed Erlang.

    - [ ] 5.2.1 Task [id: p0-p05-native-bootstrap] [area: c-runtime] [after: p0-p05-acquire-verify, p0-p05-toolchain-container] — Configure, build, probe, and hash the required OTP 29 native bootstrap from the pinned clean source.

      Copy the verified read-only source into the declared writable working
      root, then use the accepted no-Java/no-wx/no-ODBC profile or document a
      reviewed correction. Completion requires OTP/ERTS identity, bootstrap
      compiler execution, kernel/stdlib inputs, artifact hashes, logs, and
      verification that the canonical source input stayed unchanged. Digest
      drift must be explained rather than hidden.

      - [ ] 5.2.1.1 Subtask — Build and execute the required native bootstrap and probe.

        Record configure/build argv, concurrency, compiler identity, source and
        output roots, exit codes, OTP `29`, ERTS `17.0.6`, and probe output.

      - [ ] 5.2.1.2 Subtask — Hash outputs, verify the source stayed clean, and retain optional-build limitations.

        Compare recorded bootstrap artifacts where meaningful, explain any
        non-reproducible bytes, and preserve the debugger/wx limitation without
        converting it into a successful full OTP build claim.

    - [ ] 5.2.2 Task [id: p0-p05-execution-sandbox] [area: cross-cutting] [after: p0-p05-toolchain-container] — Verify the environment allowlist, local-only filesystem authority, egress denial, process ownership, and teardown of the complete clean replay.

      Observe rather than assume that undeclared environment, network, cache,
      compiler, OTP, and host paths are unavailable during execution.

      - [ ] 5.2.2.1 Subtask — Exercise undeclared environment, mount, path, cache, and network attempts.

        Each attempt must fail or be absent by construction, with the isolation
        mechanism, privilege boundary, and raw observation retained.

      - [ ] 5.2.2.2 Subtask — Tear down containers, namespaces, outputs, and temporary credentials deterministically.

        Record process/container census, exit status, retained evidence,
        recoverability, and zero unexpected running resources.

  - [ ] 5.3 Section — Phase 5 Integration Tests.

    Replay acquisition-to-bootstrap readiness from a fresh root and exercise
    identity skew, missing inputs, unexpected authority, build failure, and
    teardown before browser execution is allowed.

    - [ ] 5.3.1 Task [id: p0-p05-integration] [area: cross-cutting] [after: p0-p05-native-bootstrap, p0-p05-execution-sandbox] — Verify the complete clean input/container/bootstrap replay and inherited P0 identities.

      Pass requires exact source and toolchain identities, a working same-source
      bootstrap, network-disabled execution, declared mounts/environment only,
      retained negative results, and no unexpected post-run resource.

      - [ ] 5.3.1.1 Subtask — Run the positive clean replay from empty acquisition, source, output, and cache roots.

        Record all commands, tool versions, environment, mounts, network mode,
        outputs, hashes, durations, and cleanup without compiling the P1 probe.

      - [ ] 5.3.1.2 Subtask — Exercise wrong commit/tree/image/platform/tool, writable source, inherited host tool, egress, and bootstrap-failure cases.

        Each case must localize the cause, fail closed, preserve evidence, and
        leave no false materialization or readiness state.

    - [ ] 5.3.2 Task [id: p0-p05-handoff] [area: research-tools] [after: p0-p05-integration] — Publish the clean replay receipt and decide entry to browser qualification.

      The reviewed contract-research evidence must bind the exact replay and
      its limitations. It must not claim browser or runtime execution.

      - [ ] 5.3.2.1 Subtask — Publish the Phase 5 execution record, raw artifacts, and machine evidence.

        Bind source/plan revisions, dirty state, acquisition identities,
        toolchains, commands, environment, isolation, outputs, hashes, failures,
        teardown, reviewer, and limitations.

      - [ ] 5.3.2.2 Subtask — Review completion and update Phase 6 entry.

        Proceed only if a different independent reviewer accepts owner-produced
        evidence and no material input or isolation uncertainty remains.
