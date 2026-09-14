---
title: "ERTS WebAssembly component implementation deep dive"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - architecture
  - browser
  - components
  - erlang
  - erts
  - implementation
  - otp
  - runtime-loading
  - webassembly
aliases:
  - "ERTS-Wasm component research"
---

# ERTS WebAssembly component implementation deep dive

## Outcome

The canonical architecture resolves into eleven implementation components.
They do not form eleven independent projects: the trusted loader creates a
generation, the Worker layer supplies ERTS threads, the browser platform layer
keeps schedulers making progress, the genuine upstream loader boots matching
OTP, and the outer supervisor remains able to destroy the complete graph.

The shortest credible proof keeps the full generated BEAM interpreter and core
ERTS semantics, uses a fixed-size shared memory and a pre-created pthread pool,
mounts one verified, write-denied release tree, and exposes only clock, wakeup,
entropy, diagnostic, release-byte, and lifecycle services. It proves one ordinary,
manifest-listed qualification module through the real BEAM loader before
declaring `ready`; a single-use authorization closes further admission before
that loader invocation begins. Network, persistence, renderer,
Elixir, arbitrary native extensions, and hot replacement remain later work.

No source in this archive reports a successful ERTS-Wasm build or boot. The
implementation choices below are research conclusions and falsifiable starting
points, not compatibility claims.

## Component set

| Component | POC implementation decision | In-depth destination |
| --- | --- | --- |
| [Artifact loader and runtime generations](components/artifact-loader-and-runtime-generations.md) | One authenticated manifest, coherent immutable asset set, stateful startup, all-or-nothing disposal | Signed staged generations, rollback, anti-downgrade, cache and service-worker qualification |
| [ERTS build and BEAM interpreter](components/erts-build-and-beam-interpreter.md) | OTP 29.0.6, same-release native generators, Emscripten pthread build, JIT off, switch dispatch first | Rebase discipline, dispatch A/B results, optimized supported build profiles |
| [Worker and pthread topology](components/worker-and-pthread-topology.md) | Compare documented `PROXY_TO_PTHREAD` and outer-Worker arrangements; pre-create the measured complete pool | Qualified scheduler/topology matrix and generation-owned Worker census |
| [Browser platform time, poll, and progress](components/browser-platform-time-poll-and-progress.md) | Narrow `sys`/poll backend; Worker monotonic clock; fixed release root; atomic wakeup; deterministic unsupported results | Browser-state-aware clocks, bounded scratch, qualified async services |
| [OTP boot and BEAM code loading](components/otp-boot-and-beam-code-loading.md) | Embedded Kernel/STDLIB/`erts_wasm_poc` release in verified, write-denied MEMFS; one-shot real load of `erts_wasm_loader_probe`; no later load | Optional signed bundles and rigorously governed load/replace/purge |
| [Processes, schedulers, signals, and timers](components/processes-schedulers-signals-and-timers.md) | Preserve ERTS; one normal scheduler but the complete mandatory auxiliary thread set; differential Tier-0 capsule | Scheduler counts, dirty work, fairness, priority signals, suspend/resume matrix |
| [Memory, garbage collection, and shared state](components/memory-garbage-collection-and-shared-state.md) | Preserve GC/allocators/ETS; fixed linear-memory ceiling; malloc-backed carriers first; OOM kills generation | Bounded growth, fragmentation tuning, full ETS and persistent-term qualification |
| [Capability broker and browser services](components/capability-broker-and-browser-services.md) | Only bootstrap necessities; bounded generation-tagged frames; no generic JS/URL/ETF bridge | Separately removable Fetch, WebSocket, storage, and opaque-key capabilities |
| [OTP and Elixir compatibility profile](components/otp-and-elixir-compatibility-profile.md) | Tier 0 Kernel/STDLIB plus one ordinary Erlang application; no Elixir claim | Tier 1 OTP then exact-patch Elixir profile, one measured closure at a time |
| [Renderer, accessibility, and page lifecycle](components/renderer-accessibility-and-page-lifecycle.md) | No renderer; navigation/unproven bfcache restoration replaces generation | Semantic DOM protocol, accessibility, focus, backpressure, qualified freeze/resume |
| [Security, observability, and supply chain](components/security-observability-and-supply-chain.md) | Import allowlist, bounds, quotas, structured traces, sanitizer/fuzz profiles, provenance and SBOM skeleton | Signed provenance, hardened builder, update drill, production threat and browser matrix |

## Dependency and ownership model

```text
trusted root bootstrap
  -> manifest + artifact loader
      -> generation registry + outer watchdog
          -> Emscripten control shell + Worker/pthread graph
              -> browser sys/time/poll/memory substrate
                  -> ERTS interpreter + processes + GC + loader
                      -> matching OTP release + admitted application

generation registry
  -> capability broker -> optional network/storage/crypto
  -> renderer adapter  -> DOM/accessibility/event return path
  -> observability     -> bounded evidence, never runtime authority
```

Ownership points outward. OTP owns application processes; ERTS owns its
threads and linear-memory structures; the generation supervisor owns Workers,
ports, browser requests, DOM handles, mounts, timers, and the right to revoke
the entire instance. OTP supervision cannot recover corrupt ERTS memory or a
deadlocked pthread, while browser Worker termination cannot preserve in-memory
OTP state.

## Research-derived POC refinements

### Prove the real loader without opening runtime loading

The immutable boot profile should start a small `erts_wasm_poc` harness
application. It should also package `erts_wasm_loader_probe` without listing or
referencing that module in the boot script or startup path. After identity
attestation, the harness atomically consumes the probe's exact single-use name
and digest authorization; that transition closes all further admission before
the normal prepare/finish loader parses, publishes, and executes it. Any load,
execution, or transition failure disposes the generation rather than reopening
the gate. Every unmanifested, mismatched, `on_load`, and
post-ready attempt fails. This proves loader parsing, transformation, code-index
publication, and lower-boundary admission without claiming hot-code support.
The upstream loader is a structural validator, not an authenticity policy, and
can intern atoms before a later module failure, so hash, identity, and expanded
size checks precede it.[^otp-load]

### Budget the irreducible thread graph, not `+S`

Pinned-source inspection identifies at least seven candidate ERTS/POSIX thread
roles despite `+S 1:1`: normal, dirty CPU, dirty I/O, poll, auxiliary, async,
and system-message dispatch. That does not prove seven newly created pthreads
or seven Emscripten pool slots, and adding a browser control Worker would
double-count some topologies. Instrumentation must separately census logical
ERTS/POSIX roles, actual Emscripten pthread Worker hosts/pool slots, and
page/root supervisory agents. The POC pre-creates the measured pool and shows
that `N` starts while `N-1` fails promptly rather than deadlocking.[^erts-source][^emscripten]

### Hold memory fixed for the first semantic proof

Shared-memory growth changes JavaScript buffer/view behavior and adds another
latency and correctness variable. Initial and maximum Wasm memory should be
equal for the POC. The manifest budgets static data, Worker stacks, release
bytes, code/literals, runtime tables, and operating headroom before
instantiation. Allocation failure is generation-fatal. Bounded growth is a
separate later experiment; memory64 is a separate target.[^memory][^weakening]

### Treat browser suspension as lifecycle, not transparent sleep

Browser callbacks can be throttled, frozen, dropped by Worker termination, or
resumed from bfcache with an old JavaScript heap. The safe POC policy replaces
the runtime on navigation, detected discard, and any restoration path not yet
qualified; it rejects all completions from the old generation. Hidden-tab
operation, freeze/resume continuity, overdue timer ordering, and open browser
capabilities belong to the later browser-state matrix.[^browser-platform]

### Separate content consistency from root authenticity

Hashes bind a generation only if the expected hash or manifest is itself
trusted. SRI covers selected HTML subresources, not a complete Worker/Wasm/data
graph, and standard Worker fetch options do not provide a general integrity
field. P0 must choose either a pinned secure-origin delivery path as part of
the trusted base or a small independently trusted bootstrap that verifies
bytes and creates Workers through a tested CSP-compatible mechanism. The
generated Emscripten loader cannot authenticate itself.[^browser-integrity]

### Separate Wasm instantiation from ERTS entry

Emscripten normally invokes `main()` as part of its run lifecycle. The outer
loader therefore needs a version-pinned controlled-start seam, not merely a
promise that resolves after factory creation. The first candidate is
modularized output with `-sINVOKE_RUN=0` and only the required explicit entry
mechanism exported; the documented `noInitialRun` input is a comparison path.
Both Worker topologies must prove that factory/runtime initialization cannot
reach `erl_init`, that the verified write-denied release tree is mounted first,
and that the supervisor can cross the ERTS entry boundary exactly once.[^emscripten]

## POC integration sequence

1. Pin source, bootstrap OTP, emsdk, build image, browser versions, deployment
   headers, trust root, topology candidates, memory and resource ceilings.
2. Compile isolated probes for atomics/TLS/wait-notify, Worker creation, clocks,
   fixed shared memory, function pointers, `setjmp`/`longjmp`, allocation, poll,
   and forced termination.
3. Cross-build the complete generated interpreter and required ERTS
   initialization surface; inspect imports, exports, native artifacts, and
   generated JavaScript.
4. Authenticate one manifest, fetch and verify bounded artifacts, create and
   register the complete generation with automatic `main` suppressed, mount
   and seal the release, then invoke the ERTS entry exactly once.
5. Preserve upstream preloads and boot an embedded release containing exact
   Kernel, STDLIB, and the `erts_wasm_poc` harness application; prove startup
   did not reference the separately packaged `erts_wasm_loader_probe`.
6. Attest source/build/runtime/profile identity; consume and close the probe's
   single-use admission before its normal prepare/finish load, execute it, and
   run Tier-0 native/Wasm differential tests.
7. Abort or fail at every loader state, force-stop a wedged VM, and repeat
   start/dispose cycles until Worker, request, timer, port, memory, and listener
   counts converge.
8. Publish the exact manifest, load trace, closure, unsupported surface,
   failures, distributions, sanitizer/fuzz results, SBOM, and provenance. Only
   the accepted qualification package establishes the POC.

## Cross-component interface rule

Every interface record should specify:

- version, runtime generation, operation, request and capability identifiers;
- encoded and expanded byte ceilings checked before allocation;
- producer ownership, immutable-publication point, consumer copy, and release;
- queue capacity, deadline, cancellation, and saturation behavior;
- expected state transition and deterministic failure result; and
- bounded diagnostic event with no secret or arbitrary application payload.

No interface may use arbitrary ETF, JavaScript evaluation, object-property
traversal, host paths, URLs, module paths, or environment lookup as its generic
extension mechanism.

## Evidence boundary

The scientific literature supports preserving Erlang's process-local memory
and carefully evolved scheduler/shared-state machinery, testing concurrent
behavior across many interleavings, and attributing whole-runtime WebAssembly
costs by subsystem.[^memory][^scaling][^concuerror][^performance] Capability
research supports explicit delegated handles over ambient namespaces, while
supply-chain research supports attesting the complete build path rather than
shipping only a final checksum.[^capsicum][^supply-chain]

AtomVM's independent Emscripten port corroborates the practical shape of an
off-UI-thread runtime, pthread-backed waiting, and a queue-and-wakeup browser
adapter. It is not an upstream ERTS port: its smaller semantic surface,
different scheduler/runtime internals, detached-thread lifecycle, and no-op
join behavior make its code an architectural comparison, not an implementation
to transplant or compatibility evidence for this project.[^atomvm]

None of those works predicts that OTP 29.0.6 will compile, fit, boot, remain
responsive, or cleanly terminate in current browsers. Those remain executable
gates in the canonical [milestone plan](../60-planning/erts-webassembly-runtime-milestones.md).

## Sources

[^erts-source]: Erlang/OTP Project, [OTP 29.0.6 source and architecture](../30-sources/erlang-otp-project-2026-erts-build-runtime-and-source.md).
[^otp-load]: Erlang/OTP Project, [OTP boot, security, and code-loading evidence](../30-sources/erlang-otp-project-2026-otp-boot-security-and-compatibility.md).
[^emscripten]: Emscripten contributors, [browser porting runtime](../30-sources/emscripten-project-2026-browser-porting-runtime.md).
[^memory]: Konstantinos Sagonas and Jesper Wilhelmsson, [Erlang memory-management research](../30-sources/sagonas-wilhelmsson-2006-erlang-memory-management.md).
[^scaling]: Phil Trinder et al., [Erlang scalability research](../30-sources/trinder-et-al-2017-scaling-reliably-erlang.md).
[^weakening]: Conrad Watt, Andreas Rossberg, and Jean Pichon-Pharabod, [WebAssembly relaxed-memory model](../30-sources/watt-rossberg-pichon-pharabod-2019-weakening-webassembly.md).
[^browser-platform]: WHATWG, W3C, and WICG, [browser lifecycle, time, and capability standards](../30-sources/browser-platform-lifecycle-and-capability-standards-2026.md).
[^browser-integrity]: W3C, WHATWG, and the WebAssembly Community Group, [browser executable-integrity and rendering standards](../30-sources/browser-executable-integrity-and-rendering-standards-2026.md).
[^concuerror]: Maria Christakis, Alkis Gotovos, and Konstantinos Sagonas, [Concuerror research](../30-sources/christakis-et-al-2013-concuerror.md).
[^performance]: Abhinav Jangda et al., [WebAssembly whole-application performance](../30-sources/jangda-et-al-2019-webassembly-performance.md).
[^capsicum]: Robert Watson et al., [Capsicum capability research](../30-sources/watson-et-al-2010-capsicum.md).
[^supply-chain]: Santiago Torres-Arias et al., SLSA contributors, and SPDX contributors, [software supply-chain provenance](../30-sources/software-supply-chain-provenance-research-and-standards.md).
[^atomvm]: AtomVM contributors, [runtime architecture and WebAssembly port](../30-sources/atomvm-project-2026-runtime-and-webassembly-port.md), source inspected at commit `0220c78ee9e7cf6c763a278b44d81ce309fcf1ab`.
