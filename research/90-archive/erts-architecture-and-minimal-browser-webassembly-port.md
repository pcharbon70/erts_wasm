---
title: "ERTS architecture and the minimum browser WebAssembly port"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - architecture
  - beam
  - browser
  - emscripten
  - erlang
  - erts
  - otp
  - porting
  - security
  - webassembly
aliases:
  - "Minimum ERTS browser port"
  - "ERTS component deep dive"
---

# ERTS architecture and the minimum browser WebAssembly port

> **Superseded on 2026-09-14.** This developing note was consolidated into
> [ERTS WebAssembly runtime architecture and milestones](../20-notes/erts-webassembly-runtime-architecture-and-milestones.md).
> It is retained here to preserve the original reasoning and citation trail.

## Executive answer

The minimum credible browser port is **not a minimal BEAM virtual machine**.
It is a largely intact, interpreter-only upstream ERTS semantic core, linked to
a small browser-specific platform layer, booting an immutable and
version-matched OTP profile inside a supervised Worker group.

The distinction matters. BEAM instruction dispatch is only one part of ERTS.
The runtime also implements terms, processes, reductions, scheduling, process
signals, mailboxes, links and monitors, garbage collection, allocators, atoms,
module and export tables, code loading, timers, ETS, BIFs, tracing, ports,
native integration, and the operating-system boundary.[^beam-book] The
upstream source confirms that many of these systems are initialized before the
first Erlang process runs and that a set of runtime service processes is
created before the schedulers take control.[^erts-source]

This produces a counterintuitive result:

- the **minimum ERTS core to preserve is broad**, because OTP semantics emerge
  from interacting runtime subsystems;
- the **minimum new implementation can be narrow**, because most semantic
  machinery should remain upstream code; and
- the **minimum admitted host authority should be narrower still**, limited at
  cold boot to threads and atomics, clocks and wakeups, entropy, bounded
  diagnostics, immutable release bytes, and deterministic termination.

The first implementation target should preserve the BEAM interpreter,
process/signal machinery, scheduler and thread-progress machinery, memory and
garbage collection, atom/module/export/code tables, boot loader, essential
BIFs, timers, ETS, and enough `kernel` and `stdlib` to exercise applications
and supervision. It should add an Emscripten target, an explicit browser
`sys`/poll/time/entropy layer, Worker ownership, an immutable release loader,
and a typed asynchronous capability broker. It should initially disable or
reject BeamAsm/JIT, distribution, raw sockets, OS processes, shell and terminal
features, arbitrary files, dynamic NIFs and drivers, and arbitrary code
loading.

No build or browser boot was produced in this research. The implementation
boundary below is a source- and literature-backed hypothesis against
Erlang/OTP 29.0.6, ERTS 17.0.6, commit
`e07fd07837e5aa845657f5fa340637121e451d47`; it is not a support claim or an
estimate of patch size.

## Research question and method

The practical question is:

> What is the smallest set of upstream ERTS subsystems, browser platform
> services, and version-matched OTP modules that can boot and preserve the
> project's required semantics without importing a general-purpose operating
> system into the browser?

The research combined four evidence classes:

1. pinned upstream OTP 29.0.6 source and official ERTS documentation;
2. official Emscripten, WebAssembly, HTML, and browser-security specifications;
3. books and peer-reviewed work on ERTS memory, scheduling, browser OS
   emulation, WebAssembly performance, and WebAssembly security; and
4. comparative browser-runtime evidence from AtomVM plus a public upstream
   Erlang/OTP WebAssembly demonstration.

Source claims, local source inspection, and recommendations are separated.
The comparative implementations are used to reveal component categories and
browser patterns, not as code or semantics to copy. Repository source
exclusions were honored. Search snippets were discovery aids only.

## A working model of ERTS

ERTS is best understood as five cooperating planes rather than as one bytecode
loop.

| Plane | Principal responsibilities | Why the browser port needs it |
| --- | --- | --- |
| Language execution | BEAM loading and transformation, interpreter dispatch, terms, exceptions, calls, BIF entry | Executes ordinary version-matched BEAM modules; loader-time specialization is part of execution semantics and performance.[^interpreter] |
| Actor runtime | Processes, reductions, run queues, scheduler classes, signals, mailboxes, links, monitors, process exit | Provides the concurrency and failure semantics on which OTP supervision depends.[^messages] |
| Memory and shared state | Process heaps and stacks, generational GC, binaries, literals, allocator families, atoms, ETS, persistent terms | Preserves term lifetime and isolation while fitting all native allocations into finite Wasm linear memory.[^memory-paper] |
| Time and external progress | Time sources, timers, polling, async threads, ports, drivers, host completions | Allows schedulers to sleep, wake, and receive browser events without blocking the UI agent. |
| Boot and operations | Preloaded modules, boot script, module/code indices, `init`, system processes, tracing, diagnostics, crash/exit handling | Turns the emulator into a usable OTP runtime and makes failures observable and terminable.[^otp-boot] |

These planes are conceptually distinct but not independently removable.
Message delivery uses the signal machinery and term allocator. Timers wake
processes through scheduler-visible state. Loading updates code indices and
module/export tables. ETS and binaries introduce shared global structures.
OTP supervision depends on links, monitors, exits, registered names, timers,
and deterministic application boot. Academic accounts of Erlang memory and
scalability reinforce this interaction: process-local collection reduces
cross-process pause coupling, while scheduler balancing, ETS, time, timers,
and shared-state contention have evolved together.[^memory-paper][^scaling]

### Execution and loading

The portable upstream execution path is the generated C BEAM interpreter.
Official descriptions show that the loader transforms generic BEAM
instructions into emulator-specific forms and specializes instructions before
execution; the interpreter is not merely a direct switch over the file
format.[^primer][^interpreter] BeamAsm is a separate native-code path for
supported CPU architectures. A browser baseline should disable BeamAsm and
retain the interpreter, then test both computed-goto and `NO_JUMP_TABLE`
dispatch forms under the chosen WebAssembly compiler.

The minimum loader is still a real loader. It must:

- validate the immutable release manifest and content hashes before ERTS sees
  bytes;
- provide the preloaded modules and boot script expected by the pinned release;
- parse and prepare admitted BEAM modules, update the module/export/code-index
  structures, and handle literal areas;
- implement a virtual release root, path, and current-directory model because
  `init.erl` and primitive loading retain file-oriented concepts; and
- reject unmanifested paths, dynamic native libraries, runtime evaluation,
  compiler inputs, and unapproved `on_load` behavior.

Eliminating mutable code updates does not make the code server, loader, literal
collector, or purger infrastructure disappear automatically. The tagged
startup creates `erts_code_purger`, `erts_literal_area_collector`, three dirty
process signal handlers, and `erts_trace_cleaner` as system processes before
scheduler execution begins.[^erts-source] A first port should preserve those
paths unless source probes prove a smaller configuration safe.

### Processes, signals, and scheduling

The process is the unit of Erlang isolation and scheduling, but OS threads are
the unit that executes schedulers. Reductions provide preemption at the BEAM
level. Process signals carry more than user messages: exits, links, monitors,
and other control operations rely on ordered signal queues and scheduler
coordination.[^messages] Replacing this with JavaScript tasks would be a new
runtime, not a platform port.

The minimum semantic target therefore retains:

- process creation, execution state, reduction accounting, yield, wait, and
  exit;
- scheduler run queues, balancing assumptions, thread progress, and wakeup;
- signal queues and mailbox delivery, including ordering required by upstream
  semantics;
- links, monitors, registered names, process flags, trapping exits, and
  supervisor-visible failure; and
- normal, dirty CPU, dirty I/O, auxiliary, async, and poll thread paths until
  each can be measured or deliberately refactored.

`+S 1:1` means one normal online scheduler; it does not mean one browser Worker
or a threadless ERTS. In the pinned source, dirty scheduler counts have their
own startup constraints and other auxiliary runtime threads remain. The exact
Worker pool must be discovered by instrumenting creation, wake, idle, and
termination—not inferred from a single scheduler flag.

### Memory, terms, and garbage collection

The initial port should keep ERTS term representation and garbage collection
unchanged unless compilation forces a localized fix. Sagonas and Wilhelmsson
show why process-local heaps are an architectural property: they permit
independent collection and cheap whole-process reclamation, while message
copying and shared regions trade synchronization against copy cost.[^memory-paper]
Current ERTS adds off-heap reference-counted binaries, literal areas, allocator
instances, and global tables that make the aggregate memory model more complex
than “one heap per process.”

WebAssembly's linear memory can host these C data structures, but it changes
the surrounding assumptions:

- `wasm32` pointer width and address-space ceilings make fragmentation, peak
  live bytes, allocator metadata, and contiguous-growth failures product
  constraints;
- ERTS allocator families and scheduler-specific instances must either work
  over Emscripten's memory primitives or select documented fallbacks;
- `mmap`, page reservation, executable memory, and native guard-page behavior
  cannot be assumed;
- shared memory growth can invalidate JavaScript views, so broker code must not
  retain stale views; and
- Wasm bounds checks contain out-of-linear-memory accesses from the browser
  host, but do not turn ERTS or linked C extensions into memory-safe code.[^wasm-security]

The first semantic suite must separately measure small-heap GC, large live
heaps, binary sharing, mailbox accumulation, ETS ownership, process death,
literal loading, and repeated boot/dispose. A payload-size number cannot stand
in for a memory model.

### Time, timers, polling, and I/O progress

ERTS requires monotonic and wall-clock time, timer wheels or services, scheduler
wakeup, and an I/O polling path even when the initial product exposes no
network or persistent storage. A browser event loop is asynchronous, and a
blocking native-style loop on the page agent freezes progress. Emscripten maps
pthreads to Workers with shared memory and atomics; its documentation warns
that blocking on the main browser agent can busy-wait or deadlock and recommends
moving application `main()` to a pthread Worker when appropriate.[^emscripten]

The initial browser adapter should implement one explicit poll bridge:

1. a scheduler or poll thread publishes a bounded request or next-deadline;
2. the JavaScript broker performs the allowed browser operation;
3. completion is copied into a bounded shared queue with operation, capability,
   runtime-generation, length, and status fields;
4. an atomic wakeup makes the poller or owning process runnable; and
5. stale generations, duplicate completions, oversized payloads, and exhausted
   quotas are rejected before term decoding.

AtomVM independently uses the same broad pattern—off-main-thread execution, a
mutex/condition-backed event queue, and browser events converted into runtime
messages—which makes the pattern plausible.[^atomvm] It does not prove that
ERTS can reuse the implementation: ERTS has a different startup graph,
scheduler topology, thread-progress system, and port machinery.

Asyncify or JavaScript Promise Integration could suspend selected C-to-JavaScript
calls, but neither should be applied across the whole runtime by default.
Asyncify transforms code and can increase size and overhead; Emscripten still
documents JSPI as experimental even though the WebAssembly proposal registry
has advanced it.[^asyncify][^jspi] A queue-and-wakeup bridge has a narrower
semantic surface and keeps browser suspension out of arbitrary scheduler
stacks. Both alternatives remain worthwhile bounded probes.

## What the pinned source says about the porting floor

The OTP 29.0.6 source makes “minimal” more concrete than the conceptual model.
`erl_init()` initializes, in broad order, literals and process relations;
unique values and process-signal queues; time, system, process, and scheduler
state; CPU topology, garbage collection, and late allocator state; code
indices, funs, atoms, exports, records, modules, registration, and messages;
the interpreter and optional native-code machinery; binary, iolist,
breakpoint, ETS, node, distribution, driver-thread, async, I/O, loader, BIF,
Unicode, external-term, map, NIF, instrumentation, and late system services.
Many calls are currently unconditional.[^erts-source]

That list should not be read as a requirement to expose every feature. It says
that each initializer needs one of three outcomes: its upstream implementation
works on the target, it receives a deterministic browser backend, or a reviewed
refactor makes the subsystem unreachable without breaking startup. Link-time
success alone cannot distinguish those cases.

The public system interface in `erts/emulator/beam/sys.h` exposes the likely
platform seam. Its responsibilities include pre-init and program startup,
scheduler/system initialization, terminal handling, file-count and preload
I/O, time and date, floating-point conversion, process identity, hostname and
environment, thread suspension/resumption on supporting systems, page and
allocator information, and dynamic library/driver/NIF loading. A browser port
should add a named browser implementation behind this seam and adjacent poll,
time, preload, and driver boundaries. It should avoid sprinkling WebAssembly
conditionals through process, GC, loader, and scheduler semantics.

The makefiles show why merely replacing `sys.c` will not be enough. The normal
emulator link includes common runtime objects for allocators, startup, BIFs,
processes and signals, ports, time, external terms and distribution, binaries,
ETS, thread progress, atoms, modules, exports, registration, GC, timers, NIFs,
and maps. The Unix system object set adds `sys`, environment, file, float, time,
signal-stack, socket, polling, memory-map, and dynamic-loader implementations.
The browser work is therefore likely to consist of:

- target recognition and generated-build fixes;
- a replacement browser system-object set;
- localized guards or deterministic backends for mandatory-but-prohibited
  subsystems; and
- a constrained release and host layer outside the emulator.

The preloaded-module makefile also includes `erl_prim_loader`, `prim_file`,
network/socket primitives, the code purger, literal collector, trace cleaner,
dirty process-signal handler, atomics, counters, and persistent terms. A
network-free and ambient-file-free product profile cannot assume those modules
vanish. It must discover which are boot dependencies, supply a safe embedded
backend where needed, and prove that the remaining operations fail as declared.

## The actual minimum: preserve, adapt, prohibit

The most useful implementation inventory is a three-way classification.

| Component | Initial disposition | Minimum work or evidence |
| --- | --- | --- |
| BEAM interpreter and generated instructions | Preserve | Cross-compile generated C; validate computed-goto and switch dispatch; differential instruction and exception tests |
| BEAM loader, literals, code indices, atom/module/export tables | Preserve and constrain | Immutable manifest, embedded release backend, admitted module set, deterministic rejection of mutable or native loading |
| Terms, processes, reductions, signals, mailboxes, links, monitors | Preserve | Native-versus-Wasm observable-semantic suite and scheduler stress tests |
| Normal and dirty scheduling, thread progress, atomics, locks, TLS | Preserve; adapt thread backend | Emscripten pthread qualification, exact Worker inventory, strict pool sizing, no UI-thread blocking |
| Per-process GC, binaries, allocators, ETS, persistent terms | Preserve | `wasm32` audit, allocator selection, finite memory limits, fragmentation and reclamation tests |
| Time, timers, poll and wakeup | Adapt | Browser clock contract, suspension semantics, shared completion queue, atomic wake, drift/late-wakeup tests |
| Preloads, `init`, boot script, minimal `kernel` and `stdlib` | Preserve as a versioned profile | Content-addressed release, virtual root/path/cwd, boot and application/supervisor tests |
| Entropy and randomness | Adapt | Seed from `crypto.getRandomValues`; never expose generic JS; separate key-handling capability if later required |
| Logging and fatal exit | Adapt | Bounded structured bootstrap diagnostics, redaction, host-visible exit reason, complete runtime-generation termination |
| Ports and port tasks | Preserve internal abstraction, restrict endpoints | One audited static browser bridge if needed; no ambient program or socket port |
| BeamAsm/JIT and executable-memory paths | Prohibit initially | Configure off and assert absence in artifact/import inspection |
| Dynamic NIF and linked-in driver loading | Prohibit initially | Remove loader authority; deterministic error; static allowlist only for audited platform code |
| Distribution, EPMD, raw TCP/UDP, DNS illusion | Prohibit initially | Exclude from release and fail clearly; later typed Fetch/WebSocket capabilities are separate work |
| OS processes, shell, terminal, signals, arbitrary environment | Prohibit | Fixed startup manifest and deterministic `not_supported` behavior |
| Arbitrary or persistent filesystem | Prohibit initially | Read-only release image; optional bounded ephemeral scratch only after boot proof |
| Hot code loading, remote code loading, unrestricted `on_load` | Prohibit initially | Single immutable code generation and manifest-enforced admission |
| Trace/crash-dump surfaces | Reduce and bound | Minimal diagnostics; no accidental exfiltration or unbounded dump allocation |

“Prohibit” cannot mean leaving a surprising half-emulation reachable. Each
path must be omitted, fenced by the release profile, or return an explicit and
tested unsupported result. Emscripten's socket proxy and virtual filesystems
are useful porting tools, but adopting them wholesale would enlarge semantics,
authority, and maintenance. Browsix demonstrates that broad Unix emulation in
a browser is technically possible; it also demonstrates that it is an
operating-system-sized project.[^browsix] That is the wrong minimum here.

## The minimum browser platform contract

The target should be expressed as an import/capability contract rather than a
list of POSIX calls. A cold-boot profile needs only these authority classes:

| Capability | Contract | Required at cold boot? |
| --- | --- | --- |
| Worker/thread substrate | Create only predeclared Emscripten Workers; shared Wasm memory; atomics; fixed pool policy | Yes |
| Monotonic time | Nondecreasing timestamp and declared resolution; suspension behavior measured | Yes |
| Wall time | Timestamp for language semantics, never an authorization oracle | Yes |
| Timer/poll wake | Arm or update a deadline, enqueue completion, atomically wake runtime | Yes |
| Entropy seed | Fixed-length bytes from browser CSPRNG with explicit failure | Yes |
| Release bytes | Read-only, content-addressed boot and BEAM assets verified before use | Yes |
| Diagnostics | Bounded and rate-limited log records plus fatal status | Yes |
| Lifecycle | Start one generation; reject stale messages; stop and hard-terminate every owned Worker and handle | Yes |
| DOM rendering | Bounded declarative operations to a separate renderer | No; add after core semantic proof |
| Fetch/WebSocket | Origin-, method-, header-, size-, concurrency-, and lifetime-scoped operations | No; separately admitted |
| Persistence | Namespaced schema, quota, transaction, and deletion contract | No; separately admitted |
| Cryptographic keys | Opaque handles and purpose-bound operations | No; separately admitted |

There should be no import that evaluates JavaScript, obtains an arbitrary DOM
object, opens an arbitrary URL, resolves an ambient file path, or sends an
unbounded byte sequence. Every request is tied to a runtime generation and a
capability handle. The broker validates before allocation, records ownership,
and supplies backpressure. Hard termination is the final recovery mechanism
when OTP supervision cannot recover a wedged or corrupted VM.

### Reference topology

```text
Browser page / trusted supervisor
  |-- immutable manifest + hash verifier
  |-- capability broker + quota ledger
  |-- renderer adapter (separate, optional)
  |-- watchdog + runtime-generation registry
  +-- Emscripten control shell
        |-- application main / ERTS interpreter Worker
        |-- normal and dirty scheduler Workers
        |-- poll, async, and auxiliary Workers as measured
        +-- shared Wasm memory + bounded request/completion queues

ERTS-in-Wasm
  |-- BEAM interpreter and loader
  |-- processes, signals, schedulers, timers
  |-- terms, GC, binaries, allocators, ETS
  +-- immutable OTP boot profile and static browser adapter
```

This topology is a hypothesis, not a claim that each ERTS thread maps one to
one to a long-lived Worker. Emscripten may retain a control shell on the page
agent while `PROXY_TO_PTHREAD` moves `main()`, or the whole generated runtime
may be hosted in an outer dedicated Worker with nested pthread Workers. The
implementation experiment must compare both. The invariant is that ERTS code
and blocking waits never execute on the UI agent and that the page-level
supervisor can enumerate and terminate the complete runtime generation.

Cross-origin isolation, correct COOP/COEP headers, and compatible CORS or CORP
handling for cross-origin resources are part of the runtime contract because
browser pthreads require shared memory. They must be tested with every
application asset and embedding arrangement, not documented as a late hosting
note.[^browser-threads]

## A five-rung definition of “working”

Using one word—port—for every milestone hides the real risk. The evidence
should advance through five explicit rungs.

### M0: target compiles and links

- same-release native bootstrap tools generate target inputs;
- a pinned Emscripten target config compiles the interpreter and platform
  probes;
- the final import/export inventory is reviewed;
- BeamAsm and prohibited native loaders are absent; and
- thread, atomic, TLS, function-pointer, allocator, and 32-bit assumptions have
  focused probes.

This is only toolchain evidence.

### M1: cold boot reaches `init`

- the runtime loads preloads and the immutable boot script;
- clocks, timers, poll wakeup, entropy, virtual path/cwd, logging, and fatal
  exit work;
- every Worker is registered with the outer supervisor; and
- idle boot does not block or busy-spin the page UI thread.

This is only bootstrap evidence.

### M2: the ERTS semantic core holds

- processes, selective receive, message ordering, links, monitors, exits,
  timers, garbage collection, binaries, ETS, registered names, applications,
  and one supervisor restart match the pinned native runtime for observable
  behavior;
- scheduler and memory stress tests run under bounded resources; and
- unsupported operations fail deterministically.

This is the minimum meaningful ERTS port.

### M3: the browser boundary is safe and disposable

- a versioned capability protocol validates types, lengths, origins, quotas,
  ownership, and generations before allocation or decoding;
- timeouts, cancellation, duplicate/late completions, malformed messages, and
  broker crashes have defined outcomes;
- hard teardown closes every Worker, port, listener, timer, request, renderer
  handle, buffer, and registry entry; and
- repeated boot/dispose cycles settle without a positive resource slope in
  target Chrome and Firefox versions.

This is the minimum deployable runtime substrate.

### M4: a useful OTP and Elixir profile is qualified

- exact ERTS, `kernel`, `stdlib`, optional OTP application, Elixir, and
  application versions are recorded;
- admitted modules and unsupported APIs are machine-readable;
- representative real applications pass conformance, responsiveness, size,
  startup, memory, and latency budgets; and
- the build is reproducible with hashes, SBOM, provenance, patch ledger,
  fuzzing results, and an exercised security-update procedure.

This is the earliest point for a product feasibility decision.

## What comparative implementations do and do not teach

AtomVM is useful precisely because it is not upstream ERTS. Its documentation
lists the same broad responsibilities—opcode execution, processes, messages,
memory, preemptive scheduling, native integration, and platform services—and
its browser port uses Emscripten pthreads, `PROXY_TO_PTHREAD`, and an event
queue feeding runtime messages.[^atomvm] Those are valuable independent
signals about the shape of the problem.

Its documented differences are equally important. A ground-up runtime can
reduce size by supporting a narrower OTP and BEAM surface, omitting dirty
schedulers, distribution, code reload, and other ERTS behavior. That makes it
an alternative product tradeoff, not a recipe for a version-matched official
ERTS profile. Its detached browser threads and no-op join path also provide no
evidence for this project's strict lifecycle requirement.

Anton Vasetenkov's interactive page claims Erlang/OTP compiled through
Emscripten and visibly presents an in-browser `escript` environment.[^demo]
That is useful independent evidence that the bare compilation direction is not
purely hypothetical. Without a version, source, patch set, build record,
Worker inventory, semantic suite, or teardown results, it cannot determine the
minimal component set or support a production claim.

## Performance and security consequences

WebAssembly performance must be measured at the workload and subsystem level.
Jangda and colleagues found that browser Wasm could retain material overhead
relative to native code and attributed costs to instruction selection,
register allocation, bounds checks, and runtime/browser effects.[^wasm-performance]
The exact figures are historical and not forecasts for current engines, but
the methodological lesson remains: compare the same BEAM workload and expose
where time is spent. Required dimensions include scheduler count, process
count, mailbox load, timer density, ETS contention, binary size, allocation
rate, host-call frequency, and Worker topology.

Security similarly cannot be reduced to “Wasm is sandboxed.” Lehmann, Kinder,
and Pradel show that memory-unsafe source bugs can survive compilation into
Wasm and become control- or data-corruption vulnerabilities inside the module;
Wasm changes exploitation and host isolation, not source-language safety.[^wasm-security]
Swivel shows that speculative-execution threats require additional reasoning
beyond architectural bounds checks.[^swivel] For this project:

- all statically linked C and ERTS code shares one failure domain;
- mutually untrusted BEAM programs should use separate Worker-plus-Wasm
  instances, not trust OTP process isolation as a security boundary;
- external terms and broker payloads are hostile and bounded before decoding;
- runtime bytes, boot files, BEAM modules, configuration, and worker scripts are
  one signed or content-addressed release generation;
- sanitizers and fuzzers target the loader, BEAM validator, external decoders,
  broker framing, port adapter, and teardown state machine; and
- CSP, cross-origin isolation, SRI where applicable, dependency provenance,
  SBOM, and emergency rebuild drills are part of feasibility.

## Highest-risk unknowns

The research narrows the project to seven questions that source reading cannot
resolve:

1. Can OTP 29.0.6's generated interpreter and full mandatory initialization
   graph compile and link under a pinned Emscripten SDK without pervasive
   common-code changes?
2. Which exact ERTS threads and Workers exist from pre-init through shutdown,
   and can an outer supervisor own them all in both candidate topologies?
3. Which time, timer, poll, allocator, memory-map, signal, and file assumptions
   fail first under `wasm32` and browser event-loop constraints?
4. What is the smallest boot script and matching `kernel`/`stdlib` module set
   that still demonstrates Tier 0 semantics rather than merely reaching an
   `init` callback?
5. Can ERTS idle without UI-thread work or browser-host busy waiting, and wake
   with acceptable latency under foreground, throttled, and suspended-tab
   conditions?
6. Can hard termination and re-creation eliminate all owned browser resources
   and converge to a stable memory/Worker envelope?
7. Are payload, startup, peak linear memory, steady memory, responsiveness,
   host-call latency, and maintenance patch size inside product-approved
   budgets?

The connected inquiry turns these into executable evidence gates. Numeric
budgets remain deliberately unset until product owners define them.

## Recommendation

Proceed only as a staged porting experiment with a deliberately asymmetric
strategy:

- **maximize reuse inside Wasm:** keep upstream ERTS's semantic machinery;
- **minimize authority outside Wasm:** add only the browser services needed for
  boot and tested application behavior;
- **minimize the supported profile:** lock exact OTP/Elixir versions and admit
  modules and capabilities explicitly; and
- **maximize evidence at the boundary:** instrument Workers, imports, memory,
  host requests, loader decisions, and teardown from the first boot.

The first engineering deliverable should not be an application demo. It should
be a target-matrix and probe harness that answers M0 and inventories the real
startup/thread/platform graph. The first meaningful success is M2; the first
deployable success is M3. A decision to ship belongs only after M4.

## Sources

[^beam-book]: Erik Stenman and contributors, [*The BEAM Book: Understanding the Erlang Runtime System*](https://blog.stenmans.org/theBeamBook/), first edition, 2025. See the archive's [source note](../30-sources/stenman-2025-beam-book.md).
[^erts-source]: Erlang/OTP Project, [OTP 29.0.6 / ERTS 17.0.6 source and documentation](https://github.com/erlang/otp/releases/tag/OTP-29.0.6), commit `e07fd07837e5aa845657f5fa340637121e451d47`. See the [ERTS source-architecture note](../30-sources/erlang-otp-project-2026-erts-build-runtime-and-source.md).
[^otp-boot]: Erlang/OTP Project, [`init` documentation](https://www.erlang.org/doc/apps/erts/init.html) and tagged [`init.erl`](https://github.com/erlang/otp/blob/OTP-29.0.6/erts/preloaded/src/init.erl). See the [boot and compatibility note](../30-sources/erlang-otp-project-2026-otp-boot-security-and-compatibility.md).
[^primer]: John Högberg, [“A brief introduction to BEAM”](https://www.erlang.org/blog/a-brief-beam-primer/), Erlang/OTP blog. The upstream account describes BEAM loading, specialization, and execution; see the combined [engineering-articles source note](../30-sources/erlang-otp-project-erts-interpreter-and-message-passing-articles.md).
[^interpreter]: John Högberg, [“A closer look at the interpreter”](https://www.erlang.org/blog/a-closer-look-at-the-interpreter/), Erlang/OTP blog; see the [engineering-articles source note](../30-sources/erlang-otp-project-erts-interpreter-and-message-passing-articles.md).
[^messages]: John Högberg, [“A few notes on message passing”](https://www.erlang.org/blog/message-passing/), Erlang/OTP blog; see the [engineering-articles source note](../30-sources/erlang-otp-project-erts-interpreter-and-message-passing-articles.md).
[^memory-paper]: Konstantinos Sagonas and Jesper Wilhelmsson, [“Efficient Memory Management for Concurrent Programs that Use Message Passing”](https://doi.org/10.1016/j.scico.2006.02.006), *Science of Computer Programming* 62, no. 2 (2006): 98–121. See the [source note](../30-sources/sagonas-wilhelmsson-2006-erlang-memory-management.md).
[^scaling]: Phil Trinder et al., [“Scaling Reliably: Improving the Scalability of the Erlang Distributed Actor Platform”](https://doi.org/10.1145/3107937), *ACM TOPLAS* 39, no. 4 (2017), Article 17. See the [source note](../30-sources/trinder-et-al-2017-scaling-reliably-erlang.md).
[^emscripten]: Emscripten contributors, [“Pthreads Support”](https://emscripten.org/docs/porting/pthreads.html), [runtime environment](https://emscripten.org/docs/porting/emscripten-runtime-environment.html), and [networking](https://emscripten.org/docs/porting/networking.html). See the [Emscripten source note](../30-sources/emscripten-project-2026-browser-porting-runtime.md).
[^asyncify]: Emscripten contributors, [“Asynchronous Code”](https://emscripten.org/docs/porting/asyncify.html), covering Asyncify and JSPI integration.
[^jspi]: WebAssembly Community Group, [JavaScript Promise Integration overview](https://github.com/WebAssembly/js-promise-integration/blob/main/proposals/js-promise-integration/Overview.md) and [proposal registry](https://github.com/WebAssembly/proposals/blob/main/README.md), accessed 2026-09-14.
[^browser-threads]: WebAssembly Community Group and web standards projects, [WebAssembly Threads](https://webassembly.github.io/threads/core/) and related browser isolation specifications. See the [browser security and threading note](../30-sources/webassembly-standards-2026-browser-security-and-threads.md).
[^atomvm]: AtomVM contributors, [AtomVM source and documentation](https://github.com/atomvm/AtomVM), inspected at commit `0220c78ee9e7cf6c763a278b44d81ce309fcf1ab`. See the [comparative source note](../30-sources/atomvm-project-2026-runtime-and-webassembly-port.md).
[^demo]: Anton Vasetenkov, [“Erlang/OTP WebAssembly”](https://www.antvaset.com/erlang-otp-wasm), undated interactive demonstration. See the [source note](../30-sources/vasetenkov-erlang-otp-webassembly-demo.md).
[^browsix]: Bobby Powers, John Vilk, and Emery D. Berger, [“Browsix: Bridging the Gap Between Unix and the Browser”](https://doi.org/10.1145/3037697.3037727), ASPLOS 2017. See the [source note](../30-sources/powers-vilk-berger-2017-browsix.md).
[^wasm-performance]: Abhinav Jangda et al., [“Not So Fast: Analyzing the Performance of WebAssembly vs. Native Code”](https://www.usenix.org/conference/atc19/presentation/jangda), USENIX ATC 2019. See the [source note](../30-sources/jangda-et-al-2019-webassembly-performance.md).
[^wasm-security]: Daniel Lehmann, Johannes Kinder, and Michael Pradel, [“Everything Old Is New Again: Binary Security of WebAssembly”](https://www.usenix.org/conference/usenixsecurity20/presentation/lehmann), USENIX Security 2020. See the [source note](../30-sources/lehmann-kinder-pradel-2020-webassembly-binary-security.md).
[^swivel]: Shravan Narayan et al., [“Swivel: Hardening WebAssembly against Spectre”](https://www.usenix.org/conference/usenixsecurity21/presentation/narayan), USENIX Security 2021. See the [source note](../30-sources/narayan-et-al-2021-swivel.md).
