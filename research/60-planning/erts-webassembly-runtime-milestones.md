---
title: "ERTS WebAssembly runtime milestones"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - browser
  - compatibility
  - erlang
  - erts
  - implementation-planning
  - milestones
  - otp
  - proof-of-concept
  - runtime-loading
  - webassembly
aliases:
  - "ERTS-Wasm implementation roadmap"
---

# ERTS WebAssembly runtime milestones

## Status and use

This is the executable milestone companion to the [canonical runtime
architecture](../20-notes/erts-webassembly-runtime-architecture-and-milestones.md).
It authorizes no implementation by itself and records no completed work. Every
gate remains unchecked until the named executable evidence exists and has been
reviewed.

The plan has two separate programs:

1. **P0–P6:** establish one minimal, pinned, meaningful proof of concept; and
2. **C1–C10:** expand an accepted proof into an in-depth, maintained ERTS-Wasm
   compatibility profile.

Runtime loading is part of every milestone. It includes browser artifact
delivery, Wasm and Worker startup, ERTS/OTP release boot, BEAM admission and
code lifecycle, update integrity, cancellation, and generation teardown.

## Program A — milestones to the minimal proof of concept

### P0 — Governed baseline and proof contract

**Objective:** freeze exactly what the proof may establish before building it.

**Work and evidence:**

- [ ] Pin OTP 29.0.6 / ERTS 17.0.6 commit
  `e07fd07837e5aa845657f5fa340637121e451d47`, the same-release native
  bootstrap, emsdk/LLVM/Binaryen, build image, Chrome, and Firefox.
- [ ] Review trust zones, protected assets, attackers, non-goals, topology
  candidates, import ABI, quotas, patch policy, and stop conditions.
- [ ] Inventory startup threads, syscalls, `sys.h` services, preloads, boot
  modules, allocator/poll/time dependencies, native edges, loader entry points,
  code indices, literals, purgers, and required `on_load` hooks.
- [ ] Record the pinned-source candidate ERTS/POSIX thread roles and define
  separate instrumented censuses for logical roles, actual Emscripten pthread
  Worker hosts/pool slots, and page/root supervisory agents. Require a measured
  pool-size `N`/`N-1` full-runtime boot test rather than deriving `N` from `+S`.
- [ ] Set the finite boot/dispose cycle count, settling interval, noise envelope,
  experimental safety ceilings, and semantic comparison rules before
  measurement. These ceilings protect the experiment; they are not product
  qualification budgets.
- [ ] Create a finite machine-readable unsupported-operation inventory for the
  POC and a loader/startup bounds matrix naming each resource's owner, unit,
  limit, enforcement point, mechanism, and breach action.
- [ ] Define how product qualification budgets will be approved from named POC
  and native baselines before Program B, so later thresholds cannot be chosen
  to fit a completed implementation.
- [ ] Define native and Wasm assertion/sanitizer/fuzz profiles, seed-corpus and
  coverage retention, failure minimization, and the POC SBOM/provenance schema.

**Runtime-loading obligation:**

- [ ] Specify the manifest schema, fixed argv/environment/root/path/cwd,
  topology-specific loader partial order, immutable module set, loading failure
  matrix, runtime identity attestation, and generation ownership rules.
- [ ] Select the root executable trust anchor and document origin, header,
  redirect, cache, service-worker, CSP, Worker-integrity, and Wasm streaming
  policy. Do not claim that a generated loader authenticates itself.

**Gate:**

- [ ] Reviewed baseline, asset/dependency/patch ledger, trust anchor, bounds and
  unsupported-operation inventories, loader protocol, and reproducible empty
  target environment exist.

**Claim unlocked:** none; this is governance evidence.

**Stop trigger:** the intended deployment cannot support a secure context,
cross-origin isolation, recursive Worker delivery policy, or the required
trust boundary.

### P1 — Target and dependency probes

**Objective:** discover the real Wasm, thread, and platform gaps before a full
link attempt.

**Work and evidence:**

- [ ] Probe Emscripten target recognition, Autoconf cross settings, generated
  interpreter C, function-pointer signatures, dispatch forms, TLS, atomics,
  locks, condition waits, `setjmp`/`longjmp`, alignment, clocks, poll wakeups,
  allocator/page behavior, and 32-bit term/pointer assumptions.
- [ ] Run a production-shaped pthread Wasm loader probe through both Worker
  topology candidates in Chrome and Firefox.
- [ ] Verify `crossOriginIsolated` inside every Worker, synthetic pthread-pool
  exhaustion mechanics, UI heartbeat responsiveness, abort/retry, and direct
  resource accounting. This probe does not establish the full ERTS pool size.
- [ ] Probe fixed shared Wasm memory with `INITIAL_MEMORY == MAXIMUM_MEMORY`,
  including static data, all candidate Worker stacks, queue storage, and
  deliberate allocation failure at the declared ceiling.
- [ ] Probe `-sINVOKE_RUN=0` with modularized output and the documented
  `noInitialRun` alternative under both Worker topologies. Instrument `main`
  and `erl_init` so factory/instantiation resolution proves neither ran.

**Runtime-loading obligation:**

- [ ] Load the probe through the proposed manifest, URL, header, MIME, cache,
  verification, Worker, and cancellation paths rather than a developer-only
  inline loader.
- [ ] Test the P0 bootstrap trust rule, redirects, cache and service-worker
  policy, generation mixing, Worker executable delivery, and pre-verification
  versus streaming behavior.

**Gate:**

- [ ] The production-shaped pthread probe successfully loads, stays
  UI-responsive, aborts, restarts, and completely cleans up in pinned Chrome
  and Firefox; otherwise the program records a stop condition. A reproducible
  matrix records every command, artifact, import, Worker, pass, failure, and
  localized patch.

**Claim unlocked:** browser/toolchain runway only.

**Stop trigger:** mandatory thread, memory, function-pointer, or deployment
behavior has no narrow platform-layer remedy.

### P2 — Interpreter artifact and outer loader

**Objective:** cross-build and instantiate upstream interpreter-only ERTS with
the smallest browser system, host-progress, and generation-cleanup layer.

**Work and evidence:**

- [ ] Cross-configure using the exact same-release native bootstrap.
- [ ] Preserve the generated BEAM interpreter and core runtime; disable BeamAsm,
  dynamic native loading, distribution, OS processes, shell, terminal, raw
  sockets, and other prohibited authority.
- [ ] Add only target/build fixes plus thread, time, poll/wakeup, entropy,
  diagnostics, release-byte, and fatal-exit platform seams.
- [ ] Pre-create a conservative source-inventory-based pthread pool for
  interpreter instantiation; defer the measured full-runtime `N`/`N-1` claim
  until ERTS actually starts its thread graph in P3.
- [ ] Suppress automatic `main`, export only the necessary explicit ERTS entry,
  and make the outer loader enforce one invocation after the verified release
  mount. Bind the exact emsdk-controlled-start settings to the manifest.
- [ ] Instantiate fixed shared Wasm memory with identical initial/maximum
  values and treat allocation failure or a Wasm trap as generation-fatal.
- [ ] Implement the minimum bounded request/completion, atomic-wakeup,
  cancellation, and idempotent partial-generation cleanup path required before
  OTP boot.
- [ ] Review Wasm imports/exports, memory/table declarations, JavaScript glue,
  Worker scripts, flags, generated sources, and patch footprint.
- [ ] Produce assertion/debug plus supported native and Emscripten
  AddressSanitizer/UndefinedBehaviorSanitizer and fuzz-target builds; record
  unsupported combinations instead of silently dropping them.

**Runtime-loading obligation:**

- [ ] Bind Wasm, generated JavaScript, Worker assets, memory settings, imports,
  and build identity to one verified manifest generation.
- [ ] Exercise success, mismatch, cancellation, timeout, and partial-start
  cleanup before attempting OTP boot.
- [ ] Reject oversized or truncated manifests and artifacts, excessive Worker
  or memory declarations, queue overflow, and decompression expansion before
  the affected decode, allocation, Worker creation, or instantiation.

**Gate:**

- [ ] The artifact repeatedly compiles, links, instantiates, and terminates in
  Chrome and Firefox with no undeclared import or unowned Worker.

**Claim unlocked:** compile/link/instantiate evidence only.

**Stop trigger:** the patch spreads materially into scheduler, process, GC, or
loader semantics instead of remaining a reviewable target/platform layer.

### P3 — Immutable ERTS and OTP cold boot

**Objective:** load matching preloads and a minimal immutable OTP release, reach
`init`, idle without blocking the UI agent, and stop at
`booted-for-qualification` rather than publishing `ready`.

**Work and evidence:**

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

**Runtime-loading obligation:**

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

**Gate:**

- [ ] Repeatable cold and warm boot, runtime-identity attestation,
  `booted-for-qualification`, idle, wake, actual-delivery negative tests,
  bounded-input rejection, UI responsiveness, and failed-load cleanup pass in
  pinned Chrome and Firefox without a blocking wait or busy loop.

**Claim unlocked:** boot evidence only.

**Stop trigger:** boot needs ambient files, broad POSIX emulation, mutable code,
unbounded imports, or a main-agent wait.

### P4 — Tier-0 semantic capsule

**Objective:** prove the minimum meaningful ERTS behavior against the pinned
native runtime.

**Work and evidence:**

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

**Runtime-loading obligation:**

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

**Gate:**

- [ ] Normalized native/Wasm traces contain no Tier-0 process, message, link,
  monitor, GC, ETS, application, or supervision semantic divergence.
  Environmental differences such as clock resolution or suspension behavior
  remain inside separately predeclared tolerances. The qualification harness
  reaches `ready` only after these checks pass.

**Claim unlocked:** minimum semantic evidence, but not yet a completed POC.

**Stop trigger:** any Tier-0 core semantic divergence remains, or its fix
requires replacing upstream semantic machinery. Only predeclared environmental
tolerances may be resolved as profile decisions.

### P5 — Bounded host progress and lifecycle

**Objective:** prove asynchronous liveness, cancellation, forced recovery, and
complete generation ownership.

**Work and evidence:**

- [ ] Harden and adversarially test the P2 bounded bootstrap
  request/completion, atomic-wakeup, cancellation, and cleanup path needed for
  clocks, timers, entropy, diagnostics, and control.
- [ ] Prove process and timer progress while host work is pending.
- [ ] Hard-stop during fetch, verification, compilation, Worker startup,
  instantiation, release mount, preload, boot, idle wait, timer wait, allocation,
  GC, and CPU-bound execution.
- [ ] Account for Workers, pthread registry, MessagePorts, timers, listeners,
  requests, shared memory/views, mounts, loading promises, and generation data.
- [ ] Place a watchdog/supervisor outside the ERTS scheduling and failure
  domain, prove that it remains independently schedulable while its browser
  agent runs, and set maximum active/supervisor-scheduled detection and
  complete-termination deadlines before the test.
- [ ] Prove active-time deadline-bounded termination while ERTS is CPU-bound,
  wedged, and waiting with an outstanding host request or occupied queue slot.
- [ ] Freeze, navigate, discard where test automation permits, and restore from
  bfcache; do not promise wall-clock cleanup while the browser schedules no
  supervisor work, and never reuse the old generation at the next lifecycle
  opportunity.
- [ ] Fuzz bounded queue frames, ownership transitions, cancellation, duplicate
  and late completions, generation rollover, and cleanup idempotence.

**Runtime-loading obligation:**

- [ ] Every callback and message carries its runtime generation; stopping closes
  admission, and late or duplicate completions cannot reach a replacement.
- [ ] Run the predefined boot/dispose series and settling interval after both
  successful and failed loads.

**Gate:**

- [ ] While the supervisor is scheduled, its watchdog terminates the complete
  Worker graph within the declared active-time deadline; after freeze/discard,
  the next lifecycle opportunity rejects and replaces the old generation. No
  owned resource survives settlement, and Worker/memory metrics have no
  positive slope outside the declared noise envelope.

**Claim unlocked:** basic disposable browser-runtime evidence.

**Stop trigger:** any partial generation cannot be revoked, or stale completion
crosses into a new generation.

### P6 — Proof-of-concept qualification package

**Objective:** make a bounded go/no-go decision for the compatibility program.

**Work and evidence:**

- [ ] Rebuild independently and retain exact commands, artifacts, hashes,
  manifests, imports, Worker inventory, patch ledger, native/Wasm traces,
  loading phase timings, resource slopes, minimized fuzz corpus, sanitizer
  results, SBOM, provenance, negative findings, and limitations.
- [ ] Publish the exact supported and unsupported POC surface.
- [ ] Review every P0–P5 gate and every stop condition.

**Runtime-loading obligation:**

- [ ] Publish the complete artifact graph, load trace, loading-negative matrix,
  cancellation matrix, module admission report, and update-by-generation rule.

**Gate:**

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

## Program B — milestones to in-depth ERTS compatibility

Program B starts only after P6 is accepted. Before C1, product owners freeze
qualification budgets or approve a non-gameable method that derives them from
named POC and native baselines. P0 experimental safety ceilings are not product
performance budgets.

### C1 — Compatibility inventory and native oracle

- [ ] Expand and automate the POC module, instruction, native, `on_load`, import,
  and capability closure for each proposed profile.
- [ ] Expand the normalized native/Wasm differential harness and
  machine-readable support matrix.
- [ ] Extend the already enforced module names, hashes, dependencies, and direct
  bypass-negative tests at the lowest practical ERTS loader boundary.

**Gate:** no unresolved module, native, import, loader, or capability edge in
the admitted profile.

### C2 — Hardened code lifecycle

- [ ] Decide through an ADR whether the supported runtime remains immutable or
  admits signed bundles or constrained replace/purge behavior.
- [ ] Fuzz BEAM validation and test prepare/commit rollback, `on_load`, atom and
  export effects, code indices, literals, funs, purging, concurrent calls,
  cancellation, downgrade, cache skew, and generation replacement.
- [ ] Exercise signed manifest sequencing, trust-root rotation, revocation, and
  rollback where applicable.

**Gate:** every loading path is manifest-enforced, transactional at its declared
boundary, and leaves no stale code, literal, capability, or generation state.

An immutable result is valid. Hot loading remains optional.

### C3 — Scheduler and browser-state compatibility

- [ ] Qualify scheduler/dirty/async/poll configurations, fairness, reductions,
  timer ordering, topology, foreground/background throttling, suspension,
  visibility changes, navigation, and bfcache policy.
- [ ] Bind topology and required browser features to the load manifest.

**Gate:** native/Wasm observable behavior and resource ownership remain inside
approved tolerances across the supported browser-state matrix.

### C4 — Memory and shared-state compatibility

- [ ] Stress process heaps, GC generations, binaries, literals, atoms,
  allocators, mailboxes, ETS, persistent terms, fragmentation, fixed-ceiling
  failure, and process/generation reclamation. Qualify linear-memory growth only
  if a separately selected profile admits it.
- [ ] Enforce artifact and module budgets before loading and runtime quotas after
  readiness.

**Gate:** peak, steady, post-GC, post-code-lifecycle, and post-disposal memory
distributions and slopes meet approved budgets.

### C5 — Core OTP and pinned Elixir profile

- [ ] Qualify Tier-1 applications, supervisors, `gen_server`, `gen_statem`,
  selected logging, and standard-library paths.
- [ ] Admit one exact Elixir version and representative applications only after
  their full reachable loading/native/capability closure passes.
- [ ] Regenerate and review the release manifest for every profile change.

**Gate:** a versioned support matrix and representative native/Wasm lifecycle,
fault, and resource evidence pass; no broad compatibility is inferred.

### C6 — Hardened broker and optional browser capabilities

- [ ] Before granting an optional capability, prove overflow-safe frames,
  private JavaScript snapshots of Wasm-authored metadata, producer-owned
  immutable publication, ERTS-owned response copies, atomic slot ownership,
  queue saturation/backpressure, cancellation, and concurrent shared-memory
  mutation resistance.
- [ ] Prove a dedicated or otherwise non-blocking bridge path preserves process
  and timer progress at `+S 1:1` while host work is pending.
- [ ] Add Fetch/WebSocket, persistence, cryptography, and other services one at
  a time with typed schemas, origin/purpose restrictions, quotas, cancellation,
  backpressure, teardown, and adversarial tests.
- [ ] Make each capability removable from imports, modules, manifest, and build.
- [ ] Keep optional application capability-handle creation closed until the
  generation reaches `ready`; pre-ready internal clock, wake, entropy,
  diagnostics, and release services remain fixed bootstrap imports, while
  hard termination remains supervisor-owned out-of-band authority.

**Gate:** the generic broker gate passes before the first optional capability;
then each capability passes a separate security review and cannot be invoked by
an undeclared or stale generation.

### C7 — Renderer and application lifecycle

- [ ] Add a bounded declarative rendering protocol, sink allowlist, atomic
  batches, focus/selection/accessibility behavior, backpressure, and stale-update
  rejection.
- [ ] Test multiple same-trust components, component bundle admission,
  navigation, watchdog recovery, and page/runtime disposal.

**Gate:** functional, accessibility, loading, scaling, ownership, and teardown
evidence passes without generic DOM or JavaScript authority.

### C8 — Security and supply-chain hardening

- [ ] Complete threat review, sanitizers, fuzzing, failure injection, CSP and
  cross-origin delivery tests, secret/redaction review, SBOM, provenance,
  reproducibility, signing, revocation, downgrade, and incident procedures.
- [ ] Treat the loader, origin, caches, Worker responses, broker, and update path
  as explicit trusted components or prove an independent trust root.

**Gate:** reviewed security evidence covers build, load, runtime, update,
failure, and teardown for the frozen candidate profile.

### C9 — Performance and browser qualification

- [ ] Measure fetch, verify, compile, instantiate, Worker readiness, release
  mount, ERTS init, OTP boot, module load, warm restart, and update separately.
- [ ] Measure artifact sizes, transient/steady memory, UI long tasks, idle CPU,
  wake/timer/host latency, scheduler workloads, and cleanup slopes.
- [ ] Run the complete supported browser, OS, cache, network, and deployment
  matrix against the budgets or approval method frozen before C1; do not select
  thresholds from the completed C9 results.

**Gate:** every support claim and budget has reproducible distributions and
failure evidence, not a single warm demo result.

### C10 — Maintained ERTS-Wasm release profile

- [ ] Rehearse at least two upstream ERTS/OTP rebases, an emsdk/toolchain update,
  a browser regression response, a signing-key rotation/revocation, rollback,
  and independent rebuild.
- [ ] Reduce or formally own every patch and generated artifact.
- [ ] Approve versioning, deprecation, compatibility, incident, and release
  policies through an architecture decision.

**Gate:** the project accepts a precise support surface and sustainable update
obligation—or pauses/rejects the candidate with retained evidence.

## Global ordering rules

- Never call compile, instantiate, `init`, or a visual demo the POC.
- Establish a minimal verified manifest and module boundary before first boot;
  do not retrofit loader authority afterward.
- Do not build the renderer or optional browser capabilities before Tier-0
  semantics and generation teardown.
- Do not choose a Worker topology before measuring loading responsiveness,
  actual ERTS threads, ownership, and forced cleanup.
- Do not call `+S 1:1` threadless.
- Do not optimize, split, or lazy-load the generation before correctness and
  atomic version closure are established.
- Do not add a service worker casually; if used, it becomes part of the loading
  and update trusted base and must prevent mixed generations.
- Do not set budgets after observing the result or hide a positive slope behind
  a generous absolute threshold. Freeze P0 safety ceilings before the POC and
  the product-budget values or derivation method before C1.
- Do not infer compatibility from dependency presence, one browser, one boot,
  or a warm developer cache.

## Connections

- [Canonical runtime architecture](../20-notes/erts-webassembly-runtime-architecture-and-milestones.md)
- [Component implementation deep dive](../20-notes/erts-webassembly-component-implementation-deep-dive.md)
- [Component implementation map](../10-maps/erts-webassembly-component-implementation.md)
- [Component-seam inquiry](../40-inquiries/which-component-seams-block-the-first-erts-wasm-proof.md)
- [Minimum browser platform-contract inquiry](../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md)
- [First-party feasibility inquiry](../40-inquiries/can-blazex-build-and-own-an-erts-webassembly-runtime-stack.md)
- [Runtime-stack map](../10-maps/erts-webassembly-runtime-stack.md)
