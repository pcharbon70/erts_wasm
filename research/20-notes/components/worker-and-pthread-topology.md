---
title: "Worker and pthread topology"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - emscripten
  - lifecycle
  - pthreads
  - scheduling
  - web-workers
  - webassembly
aliases:
  - "ERTS browser thread topology"
---

# Worker and pthread topology

## Decision

Use Emscripten pthreads over shared Wasm memory and compare two concrete
ownership arrangements before selecting the POC topology. Pre-create the full
measured Worker pool, keep all ERTS execution and blocking waits off the page's
UI agent, and make pool exhaustion fail visibly.

## Why this is irreducibly threaded

ERTS configuration requires a thread library. `+S 1:1` selects one normal
online scheduler; it does not remove dirty schedulers, polling, async work,
thread progress, auxiliary work, or runtime service threads. Pinned-source
inspection identifies at least seven candidate ERTS/POSIX roles—normal, dirty
CPU, dirty I/O, auxiliary, poll, async, and system-message dispatch—but does
not prove seven newly created pthreads or seven Emscripten pool slots. The
proxied `main`, outer runtime Worker, and control shell overlap differently in
the two topologies, and allocator choices may create more work. Only separate
target censuses of ERTS/POSIX roles, Emscripten pthread Worker hosts/pool slots,
and page/root supervisory agents can size the pool.[^erts-source]

Browser pthreads require `SharedArrayBuffer`, a shared
`WebAssembly.Memory`, atomics, consistent `-pthread` compile/link flags, and a
cross-origin-isolated context. Worker creation is asynchronous; code that
immediately waits for a new thread can deadlock unless Workers already exist.
The browser main agent cannot perform a blocking `Atomics.wait`.[^emscripten]

## POC topology experiment

Compare:

1. **Page control shell plus `PROXY_TO_PTHREAD`.** The generated Emscripten
   shell is created from the page, pre-creates its pool, and moves application
   `main()`/ERTS into a Worker. This follows the documented toolchain path and
   leaves page-only proxying available, but the generated shell and internal
   Worker registry become part of the page's trusted surface.
2. **Outer runtime Worker.** The page creates one generation Worker, which
   loads the Emscripten shell and creates nested pthread Workers. This gives a
   cleaner apparent owner, but nested script resolution, recursive COEP,
   toolchain proxy assumptions, and whether killing the root reliably removes
   children require separate Chrome/Firefox proof.

Instrument ERTS/POSIX thread creation, Worker construction, pool-slot
assignment, and pthread registration through stable hooks where available;
otherwise carry a small version-pinned patch to generated runtime code and
review it at every emsdk update. Record logical ERTS role, logical pthread ID,
Worker host, pool slot or proxied-main status, creation parent, stack range,
readiness, last heartbeat, supervisor role, and generation. The page
supervisor must possess a terminable handle—or an explicitly proven transitive
termination path—for every Worker.

Begin with one normal scheduler and the smallest accepted dirty, poll, async,
and auxiliary settings discovered from the pinned build. Set
`PTHREAD_POOL_SIZE` to the complete observed startup high-water mark plus only
justified later dynamic threads, enable strict exhaustion behavior, and set
main-thread blocking to an error. A pool of `N` must boot repeatedly; `N-1`
must stop with a named failure and clean up, never wait indefinitely.

Check `crossOriginIsolated`, shared-memory construction, required Wasm atomics,
Worker CSP, and recursive embedder policy in every participating Worker before
ERTS initialization. There is no transparent non-threaded fallback binary. If
deployment lacks shared memory, fail preflight; a cooperative threadless ERTS
would be a different research program.

## Thread progress and memory ordering

Preserve `ethread`, ERTS atomics/locks, scheduler sleep, and thread-progress
epochs. Do not replace them with JavaScript booleans. WebAssembly's relaxed
memory model provides specified atomic wait/notify and data-race-free
consistency, but Worker creation and forward progress remain embedder concerns.
All shared rings and wake words need aligned atomic fields and documented
release/acquire publication; ordinary racy reads remain nondeterministic.[^weakening]

No ERTS thread may hold a thread-progress delay or scheduler lock while
awaiting a Promise or page message. Browser work returns asynchronously through
the platform completion queue, then an owned runtime thread wakes ERTS.

## In-depth implementation

Increase normal and dirty scheduler counts only with evidence for fairness,
parallel throughput, stack and memory cost, Worker limits, wake latency, idle
CPU, background throttling, and teardown. Qualify work stealing, run-queue
balancing, delayed deallocation, dirty jobs, concurrent ETS/code reclamation,
and no-op priority/affinity behavior separately.

Shared-Everything Threads and Component Model concurrency are future standards
directions, not prerequisites. The maintained browser profile should continue
to bind a specific emsdk/browser topology until a newer standard demonstrably
reduces code and authority without changing ERTS semantics.

## Evidence gates

- Produce three linked phase-by-phase graphs for both topologies in Chrome and
  Firefox: logical ERTS/POSIX roles, actual pthread Worker hosts/pool slots, and
  page/root supervisory agents, including failed boot and cancellation.
- Run atomic width/alignment/order, TLS, condvar, mutex, rwlock, event,
  wait/notify, timed wait, and thread-progress stress probes.
- Show no ERTS or blocking wait on the UI agent through performance traces and
  an adversarial CPU-bound workload.
- Force a scheduler deadlock and prove an independently schedulable outer owner
  terminates every Worker within its declared active-time deadline once browser
  scheduling permits it.
- Repeated creation/disposal returns Worker count, shared-memory references,
  MessagePorts, and timers to baseline.

## Principal risks

Browsers may impose lower practical Worker/stack/memory limits than desktop
ERTS assumes. Emscripten proxying can create hidden dependencies on the page
agent. An outer Worker may not own nested Workers as strongly as its shape
suggests. Browser freeze can suspend the watchdog along with the VM, so the
hard-stop deadline is guaranteed only while its supervisory agent is scheduled.

## Sources

[^erts-source]: Erlang/OTP Project, [pinned ERTS thread and scheduler source](../../30-sources/erlang-otp-project-2026-erts-build-runtime-and-source.md).
[^emscripten]: Emscripten contributors, [pthreads and browser runtime](../../30-sources/emscripten-project-2026-browser-porting-runtime.md).
[^weakening]: Conrad Watt, Andreas Rossberg, and Jean Pichon-Pharabod, [Weakening WebAssembly](../../30-sources/watt-rossberg-pichon-pharabod-2019-weakening-webassembly.md).
