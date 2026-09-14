---
title: "ERTS WebAssembly runtime architecture and milestones"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - architecture
  - beam
  - browser
  - elixir
  - emscripten
  - erlang
  - erts
  - otp
  - runtime-loading
  - security
  - webassembly
aliases:
  - "ERTS architecture and the minimum browser WebAssembly port"
  - "First-party Erlang/OTP ERTS WebAssembly runtime stack"
  - "Minimum ERTS browser port"
  - "ERTS component deep dive"
  - "First-party ERTS-in-Wasm architecture"
  - "Browser ERTS stack"
---

# ERTS WebAssembly runtime architecture and milestones

## Executive decision

The credible route to ERTS in browser WebAssembly is to preserve the broad
semantic core of upstream Erlang/OTP ERTS, compile its portable BEAM
interpreter with Emscripten, and replace only the operating-system-facing layer
with a small browser platform contract. The initial target is not a new BEAM
implementation, a complete POSIX environment, or a production-ready Erlang
distribution. It is a version-locked, interpreter-only ERTS that boots matching
`kernel` and `stdlib` BEAM modules inside a directly supervised Worker group.

The architecture has one cross-cutting constraint: **runtime loading is part of
the runtime, not packaging around it**. Browser delivery, Wasm instantiation,
pthread Worker startup, ERTS preloads, the OTP boot script, BEAM validation,
loader-time instruction specialization, module/code indices, literal ownership,
and generation teardown form one trust and lifecycle chain. A proof that bypasses
that chain is not a proof of the intended runtime.[^erts-source][^otp-boot]

The first proof of concept is intentionally narrow. It has no DOM integration,
network, persistence, dynamic NIFs or drivers, distribution, shell, compiler,
arbitrary filesystem, hot code replacement, or general Elixir claim. It is
valid only when the pinned upstream runtime:

1. is reproducibly compiled and loaded through a manifest-verified artifact set;
2. boots a matching immutable OTP profile in Chrome and Firefox;
3. demonstrates processes, message ordering and selective receive, timers,
   garbage collection, ETS, links, monitors, application boot, and a supervisor
   restart against a native oracle;
4. sleeps and wakes without ERTS execution or blocking waits on the UI agent;
5. consumes one single-use authorization for a manifest-listed qualification
   module after boot but before `ready`, closes further admission before the
   normal loader runs, and rejects every undeclared module, asset, import,
   capability, argument, bypass, and post-ready loading attempt; and
6. can be aborted and recreated without stale completions, unowned Workers, or
   a positive post-disposal resource slope.

Passing those conditions establishes a meaningful feasibility baseline. It does
not establish production security, broad OTP or Elixir compatibility, browser
support beyond the tested matrix, or acceptable product performance. Those are
the subject of the second milestone program.

No ERTS WebAssembly build or boot exists in this corpus. The pinned research
baseline is Erlang/OTP 29.0.6, ERTS 17.0.6, commit
`e07fd07837e5aa845657f5fa340637121e451d47`. Everything below is a proposed
architecture and evidence plan, not implementation evidence or a support claim.

## Scope and terminology

**ERTS-in-Wasm** means the official upstream ERTS implementation compiled into
a Core WebAssembly module. Ordinary admitted Erlang or Elixir source compiles to
BEAM and is loaded by that ERTS instance; application modules do not ordinarily
become separate native Wasm modules.

The complete browser arrangement has four independent axes:

- **runtime substrate:** upstream ERTS plus matching OTP BEAM modules;
- **execution host:** an Emscripten control shell and directly supervised Worker
  group using shared Wasm memory and atomics;
- **host authority:** a versioned, typed, bounded, deny-by-default capability
  broker; and
- **render or server integration:** optional adapters outside the runtime proof.

The resulting artifact is a Core Wasm module, not automatically a WebAssembly
Component Model component. A later non-browser WASI target may share concepts,
but current browser threads, networking, storage, DOM, and lifecycle still need
a browser-specific embedder.[^wasi]

## Architectural invariants

These invariants apply to the proof of concept and every later milestone:

1. **Preserve upstream semantics.** Do not rewrite the scheduler, process model,
   signal queues, garbage collector, loader, or OTP behaviours to make a demo
   easier.
2. **Pin the complete generation.** ERTS, OTP applications, native bootstrap,
   emsdk, generated JavaScript, Worker scripts, release pack, manifest, and
   tests move as one identified generation.
3. **Establish bootstrap trust before generation effect.** Authenticate the
   manifest and root executable bootstrap before they create generation
   resources. Every later executable artifact is either verified before use or
   obtained through an explicitly trusted immutable delivery path. A generated
   loader cannot be treated as verifying itself.
4. **Keep ERTS off the UI agent.** Neither ERTS execution nor a blocking atomic
   wait may run on the browser main thread.
5. **Deny by default.** No generic JavaScript call, arbitrary URL, DOM object,
   host path, native library, startup argument, environment variable, or module
   path is exposed.
6. **Bound before decoding or allocation.** External frames, BEAM files, release
   records, broker messages, URLs, and renderer operations are hostile until
   their type, length, generation, capability, and quota are checked.
7. **One generation, one owner.** Every Worker, MessagePort, timer, listener,
   request, buffer, mount, capability handle, and renderer handle belongs to a
   runtime generation and can be revoked by its supervisor.
8. **Unsupported means deterministic.** Excluded facilities are absent or fail
   with a declared result; partial ambient emulation is not acceptable.
9. **Compare with native ERTS.** Observable semantic claims use the same BEAM
   workload on the pinned native release as an oracle.
10. **Evidence advances status.** Compilation, boot, or a visual demonstration
    does not mark a later compatibility, security, lifecycle, or performance
    gate complete.

## Recommended system architecture

The runtime should be one immutable generation supervised outside ERTS:

```text
Browser page / trusted generation supervisor
  |-- deployment and feature preflight
  |-- manifest, signature/hash, and policy verifier
  |-- capability broker and quota ledger
  |-- watchdog and owned-resource registry
  |-- optional renderer adapter (after the proof of concept)
  +-- Emscripten runtime boundary
        |-- generated JavaScript control shell
        |-- application main / ERTS interpreter Worker
        |-- measured scheduler, dirty, poll, async, and auxiliary Workers
        |-- shared WebAssembly.Memory and bounded queues
        +-- immutable release mount

ERTS-in-Wasm
  |-- generated BEAM interpreter and constrained loader
  |-- terms, processes, reductions, signals, links, and monitors
  |-- schedulers, thread progress, clocks, timers, and poll integration
  |-- per-process GC, binaries, allocators, atoms, ETS, and literals
  +-- matching preloads, init, kernel, stdlib, and admitted BEAM modules
```

The browser supervisor is a recovery layer outside OTP supervision. OTP can
restart application processes; it cannot repair a corrupt, deadlocked, or
over-budget ERTS instance. The outer supervisor must be able to terminate the
entire generation even when the VM cannot cooperate.

### Worker topology

The first implementation must compare two Emscripten arrangements rather than
assume they are equivalent:

- **control shell on the page agent:** Emscripten owns a pre-created pthread
  pool and `PROXY_TO_PTHREAD` moves application `main()` and ERTS to a Worker;
- **outer runtime Worker:** the page creates one dedicated runtime Worker, which
  owns the Wasm instance and any nested Emscripten pthread Workers.

The first is the documented Emscripten route. The second may offer cleaner
generation ownership, but nested Worker creation, script resolution, shared
memory, main-thread-only APIs, and termination need independent browser proof.
The chosen topology must be based on a Worker census, idle/wakeup behavior, and
forced-teardown evidence.[^emscripten]

Instantiation and ERTS entry are separate states. Generated Emscripten output
normally invokes `main()` automatically, so the POC must qualify a pinned
controlled-start seam—first candidate `-sINVOKE_RUN=0` in modularized output,
with a minimal explicit entry export, and comparison with `noInitialRun` under
both topologies. Wasm/runtime initialization may prepare memory and global
initializers, but it must not reach `erl_init` until the verified, write-denied
release tree is mounted and the supervisor makes its single start call.

`+S 1:1` selects one normal online scheduler; it does not create a threadless
ERTS or imply one Worker. Dirty CPU and I/O schedulers, pollers, async work,
thread progress, and auxiliary threads have separate startup paths. Strict
pthread-pool exhaustion should fail visibly during qualification rather than
hang. Pinned-source inspection currently identifies seven candidate ERTS/POSIX
thread roles—normal, dirty CPU, dirty I/O, auxiliary, poll, async, and
system-message dispatch. It does not yet establish seven newly created POSIX
threads or seven Emscripten pool slots: the proxied `main`, root Worker, and
control shell differ between topologies. Qualification must separately census
ERTS/POSIX roles, Emscripten pthread Worker hosts and pool slots, and page/root
supervisory agents. Only that target census sets pool size `N`; `N-1` must fail
promptly and clean up.[^erts-source]

The POC should also hold shared Wasm memory fixed by setting initial and maximum
memory equal. This removes growth, detached or stale JavaScript views, and a
second latency variable from the first semantic proof. The manifest must budget
static data, all Worker stacks, the release image, code and literals, runtime
tables, queues, and operating headroom before instantiation. Bounded growth is a
separate compatibility experiment; allocation failure is generation-fatal.

### Artifact model

One runtime generation contains at least:

- `erts.wasm`, with reviewed imports and exports;
- the exact generated JavaScript control shell and runtime bootstrap;
- every required pthread Worker script;
- one content-addressed read-only release pack containing the boot script,
  `.app`, `.beam`, and approved `priv` assets;
- a compatibility and capability manifest;
- native-oracle and browser conformance capsules;
- source, toolchain, patch, and generated-file provenance; and
- hashes, licenses, an SBOM, and an unsupported-surface report at the maturity
  appropriate to the phase.

The loader must never assemble a generation from independently cached versions.
An update produces a new generation identifier; it does not mutate a live
generation in place.

### Bootstrap trust anchor

The first executable page or Worker bootstrap is necessarily outside the
artifact set it verifies. P0 must choose and document a root of trust. A first
proof may treat a pinned secure origin, its response headers, redirects, and
cache path as part of the trusted computing base, or it may use a smaller
independently trusted bootstrap that verifies fetched bytes and creates Workers
through a CSP-compatible verified-byte mechanism. The generated Emscripten
loader cannot silently fill this role.

Hashes fetched from the same compromised origin establish version consistency,
not authenticity. The selected design must state its service-worker policy,
executable Worker-integrity mechanism, redirect policy, and whether Wasm is
fully verified before compilation or compiled while streaming and barred from
instantiation until trust succeeds. Mixed-cache and mixed-generation failures
must be tested under the actual deployed mechanism.

## A working model of ERTS

BEAM bytecode interpretation is only one plane of ERTS. The runtime is better
understood as five cooperating planes.[^beam-book]

| Plane | Preserved responsibilities | Browser-port consequence |
| --- | --- | --- |
| Language execution | BEAM validation, loader transformations, interpreter dispatch, terms, calls, exceptions, BIF entry | Cross-compile the generated interpreter; retain the real loader and test computed-goto and switch dispatch |
| Actor runtime | Processes, reductions, run queues, schedulers, process signals, mailboxes, links, monitors, exits | Keep upstream concurrency semantics and adapt only the thread/wakeup substrate |
| Memory and shared state | Process heaps/stacks, generational GC, binaries, literals, atoms, allocator families, ETS, persistent terms | Audit `wasm32`, fixed ceilings, fragmentation, shared views, global limits, and growth only if a later profile selects it |
| Time and external progress | Monotonic/wall time, timers, polling, async threads, ports, host completions | Provide a bounded queue-and-atomic-wakeup bridge; never block a scheduler on browser I/O |
| Boot and operations | Preloads, `init`, boot script, code indices, runtime service processes, tracing, diagnostics, shutdown | Treat loading and lifecycle as mandatory runtime subsystems |

The planes cannot be removed independently. Message delivery uses process
signals and term allocation. Timers interact with scheduler-visible state.
Loading updates atom, module, export, literal, and code-index structures. ETS and
binaries introduce shared global resources. OTP supervision depends on links,
monitors, exits, names, timers, loading, and deterministic application boot.
Research on Erlang memory and scalability confirms that process-local
collection, message copying, scheduler balancing, ETS, time, timers, and shared
state are interacting design properties rather than incidental server
features.[^memory][^scaling]

### What the pinned source says about the porting floor

OTP 29.0.6 `erl_init()` initializes literals, process relations, unique values,
signal queues, time, process and scheduler state, topology, garbage collection,
allocators, code indices, funs, atoms, exports, records, modules, registration,
messages, the interpreter, tracing, binaries, ETS, node/distribution structures,
driver threads, async work, I/O, the loader, BIF families, external terms, maps,
NIF support, and late system services. Many initializers are unconditional.
Each therefore needs a working target implementation, a deterministic browser
backend, or a reviewed refactor that makes it safely unreachable.[^erts-source]

Before schedulers start, the tagged runtime also creates the code purger,
literal-area collector, three dirty process-signal handlers, and trace cleaner.
Disabling mutable code updates does not automatically remove code-index,
literal, purge, or runtime-service machinery.

The public `sys.h` interface and adjacent system files expose the likely porting
seam: startup, scheduler/system integration, preload I/O, time and date,
environment, terminal and signal behavior, allocator/page information,
polling, and dynamic loading. The browser target should add a named platform
implementation behind those seams rather than scatter Wasm conditionals through
process, GC, loader, and scheduler logic.

## Preserve, adapt, and prohibit

| Component | Initial disposition | Required proof or implementation |
| --- | --- | --- |
| Generated BEAM interpreter | Preserve | Cross-compile; differential instruction, exception, and dispatch tests |
| Loader, literals, atoms, module/export tables, code indices | Preserve and constrain | Manifest-backed release, one pre-ready qualification load, admitted hashes, then immutable POC code generation and loader-negative tests |
| Processes, reductions, signals, mailboxes, links, monitors | Preserve | Native-versus-Wasm semantic capsule and stress tests |
| Normal/dirty scheduling, thread progress, atomics, locks, TLS | Preserve; adapt backend | Exact Worker census, Emscripten pthread qualification, no UI-agent waits |
| GC, binaries, allocator families, ETS, persistent terms | Preserve | `wasm32` audit, finite memory policy, reclamation and fragmentation tests |
| Time, timers, poll and wakeup | Adapt | Declared clock semantics, bounded queues, atomic wake, suspension and late-wakeup tests |
| Preloads, `init`, boot script, matching `kernel` and `stdlib` | Preserve as profile | Immutable release load and application/supervisor boot |
| Entropy, bootstrap logging, fatal exit | Adapt | Fixed-size CSPRNG seed, bounded diagnostics, host-visible failure and cleanup |
| Ports and port tasks | Preserve abstraction, restrict endpoints | Static audited bridge only when admitted; no ambient program or socket port |
| BeamAsm/JIT and executable memory | Prohibit initially | Configure off and assert absence in artifact inspection |
| Dynamic NIF/driver loading | Prohibit initially | No loader authority; static allowlist only for audited platform code |
| Distribution, EPMD, raw TCP/UDP | Prohibit initially | Exclude and return declared unsupported results |
| OS processes, shell, terminal, general signals/environment | Prohibit | Fixed startup manifest and deterministic failure |
| Arbitrary or persistent filesystem | Prohibit initially | Read-only release mount; bounded scratch and persistence are later capabilities |
| Hot/remote code loading and unrestricted `on_load` | Prohibit in POC | Later admission only through a governed code-lifecycle profile |
| Crash dumps and broad tracing | Reduce and bound | No secret exfiltration or unbounded allocation; sufficient structured evidence |

The goal is a small browser platform layer, not small semantics. Browsix shows
that broad Unix emulation in a browser is technically possible and also that it
is an operating-system-sized commitment.[^browsix] That is the wrong default
for this runtime.

## Runtime loading is a first-class subsystem

“Loading” names three different problems, all of which must pass in the proof of
concept and remain governed later.

### 1. Browser artifact loading

The page must obtain a manifest, `erts.wasm`, generated JavaScript, Worker
scripts, and the release pack under a compatible CSP and cross-origin-isolated
deployment. It must prevent version skew, cache mixing, redirect surprises, and
unverified fallback. COOP/COEP and compatible CORS or CORP behavior apply to
every Worker and cross-origin asset, not just the initial HTML response.[^web-threads]
The production-sized ERTS artifact path—not only a small pthread probe—must be
tested for wrong MIME type, header failure, redirect, cache/service-worker skew,
streaming fallback, cancellation, main-agent long tasks, and transient memory.

### 2. ERTS and OTP boot loading

ERTS must expose the exact preloads expected by its release and create
`init:boot`. `init.erl` starts `erl_prim_loader`, reads the selected boot script,
sets paths and variables, processes `primLoad` and `kernelProcess` instructions,
and can consult `prim_file:get_cwd()`. A release with no ambient filesystem still
needs a virtual root, current directory, loader path, and file-result semantics.
The POC supplies these from a content-addressed release tree in ephemeral
MEMFS. Because MEMFS is writable by default, a lower filesystem/system adapter
must deny write/create flags, rename, unlink, truncate, directory mutation,
links, devices, and undeclared paths after population; negative tests—not the
MEMFS name—establish the read-only claim.[^otp-boot]

### 3. BEAM module and code-lifecycle loading

The loader validates and transforms generic BEAM instructions into
emulator-specific forms before execution. It updates atoms, exports, modules,
code indices, literal areas, fun tables, and related runtime state.[^interpreter]
The POC boots only the generation named in the manifest. The boot script starts
the `erts_wasm_poc` harness application; a separate ordinary
`erts_wasm_loader_probe` module is present in the verified release pack but is
omitted from the boot script and must not be referenced during startup. After
boot and identity attestation, the harness atomically consumes a single-use
authorization for that exact name and digest, thereby closing all future
admission before the normal prepare/finish loader path parses the module. It
then publishes and executes the probe before `ready`. All undeclared,
mismatched, `on_load`, bypass, replacement, purge, and post-ready loads fail.
This proves the actual parser, transformation, code-index publication, and policy boundary
without claiming supported dynamic loading. Later compatibility work may admit
signed bundles or governed code replacement, but only after lower-boundary
enforcement, purge and literal-lifetime tests, `on_load` policy, rollback, and
generation ownership are proven.

### Loader state machine

The outer loader should be explicit and generation-scoped. Startup is a
partial order because the two candidate Worker topologies do not create shared
memory, compile Wasm, start the root Worker, and populate the pthread pool in
the same sequence:

```text
created
  -> platform-preflighted
  -> bootstrap-trust-established
  -> manifest-authenticated
  -> topology-specific startup region
       { artifacts fetched and verified under their trust rule;
         Wasm compiled; shared memory created;
         each Worker created and registered before effect;
         runtime instance created with main suppressed from one coherent generation }
  -> immutable-release-mounted
  -> explicit-erts-entry-invoked
  -> erts-initialized
  -> otp-booted
  -> runtime-identity-attested
  -> booted-for-qualification
  -> qualification-admission-consumed-and-closed
  -> qualification-module-published
  -> qualification-module-executed
  -> tier-0-self-check-passed
  -> ready

any state -> cancelling -> all-generation-resources-revoked -> terminated
```

Within the topology-specific region, manifest authentication and bootstrap
trust precede generation effect, no executable artifact has effect before its
declared trust rule passes, every Worker and handle is registered before it can
affect the generation, and ERTS initialization cannot begin until the coherent
artifact set is accepted and the release is mounted. P3 stops at
`booted-for-qualification`; it packages
but does not yet admit the qualification module and does not publish `ready`.
P4 alone may perform the one manifest-listed normal load by consuming the exact
authorization and closing admission, then run the Tier-0 checks. Closing is
fail-safe: consuming the exact one-shot
authorization closes every future loading path before native parsing begins;
any prepare, commit, execution, or state-transition failure terminates the
generation and cannot reopen admission. Only then may the harness transition
to `ready`, and P6—not `ready` alone—unlocks the POC claim.

After boot, ERTS must attest the expected source/build identity, ERTS and OTP
versions, release generation, and boot profile back to the outer supervisor.
A mismatch enters cleanup. A failure, timeout, user navigation, or replacement
request from any state uses the same idempotent cleanup path.

### Manifest minimum

The signed or otherwise authenticated manifest fixes:

- format and runtime-generation identifiers;
- the bootstrap trust root, executable-integrity mechanism, redirect/cache/
  service-worker policy, and streaming-compilation rule;
- OTP/ERTS source tag and commit, emsdk revision, build image, and patch digest;
- hashes and expected locations for Wasm, JavaScript, Worker, release, and
  configuration assets;
- initial/maximum memory, scheduler/thread/pool settings, and required browser
  features and headers;
- the modularized-runtime, automatic-main suppression, exported-entry, and
  one-shot start policy;
- the boot file, preloaded modules, admitted BEAM module names and hashes, and
  approved `on_load` policy;
- the only accepted argv, environment, root, current directory, and code paths;
- Wasm import/export allowlists and broker capability grants; and
- size, queue, process, memory, timer, request, and lifecycle quotas.

Every loader and startup bound also has a named owner, unit, enforcement point,
mechanism, and breach action. This includes compressed and expanded release
bytes, individual BEAM files, manifest records, Worker declarations, initial
and maximum memory, queue slots, and startup time. A numerical limit without a
pre-allocation enforcement point is not a bound.

Verification must occur before importing powerful host functions or publishing
Worker handles. JavaScript allowlists alone are insufficient; the lowest
practical ERTS loading boundary must reject an unmanifested module even if a
higher layer is bypassed.

### Loading policy by maturity

| Phase | Startup code | Post-boot code | Updates |
| --- | --- | --- | --- |
| Proof of concept | One immutable release generation | One manifest-listed qualification load after boot and before `ready`; permanently denied afterward | Terminate old generation, verify and start a complete new one |
| Early compatibility | Immutable base plus explicitly signed, hashed bundles if required | Manifest-listed modules only; no arbitrary binary load | Generation replacement with rollback evidence |
| In-depth profile | Governed code lifecycle selected per product need | Optional constrained load/replace/purge; unrestricted loading may remain unsupported | Signed staged rollout, compatibility checks, revocation, rollback, resource convergence |

Hot code replacement is not automatically required for browser ERTS validity.
If the product does not need it, keeping it disabled is a smaller and safer
supported profile. If it is admitted, it is a separate compatibility and
security feature, not a free consequence of retaining the upstream loader.

## Browser platform contract

The cold-boot contract exposes only the authority needed for runtime progress:

| Capability | Contract | POC status |
| --- | --- | --- |
| Threads and atomics | Predeclared Workers, shared Wasm memory, atomics, fixed pool policy | Required |
| Monotonic time | Nondecreasing timestamp, declared resolution and suspension behavior | Required |
| Wall time | Language-visible timestamp, never an authorization oracle | Required |
| Timer/poll wake | Publish deadline/completion and atomically wake the runtime | Required |
| Entropy seed | Fixed-length bytes from browser CSPRNG with explicit failure | Required |
| Release bytes | Verified content-addressed, read-only assets | Required |
| Diagnostics | Bounded, rate-limited records and fatal status | Required |
| Supervisor lifecycle (outside ERTS imports) | Start, cancel, hard-stop, reject stale generations, revoke all ownership | Required |
| DOM renderer | Bounded semantic protocol to a separate adapter | Deferred |
| Fetch or WebSocket | Origin/method/header/size/concurrency/lifetime policy | Deferred |
| Persistence | Namespaced schema, transaction, quota, and deletion contract | Deferred |
| Cryptographic keys | Opaque purpose-bound handles | Deferred |

Browser operations complete asynchronously. The preferred bridge uses bounded
shared request/completion queues and atomic wakeup. An ERTS process publishes a
request through an audited port or BIF boundary; the broker validates policy
before allocating or calling the browser; the completion carries operation,
capability, length, status, and runtime generation; the runtime copies it into
owned memory before releasing the slot. Scheduler threads do not block on host
completion.

Asyncify or JSPI may be tested at tightly controlled boundaries, but not spread
through arbitrary scheduler stacks. Asyncify rewrites call stacks and can add
size and runtime cost; Emscripten still treats JSPI support as experimental even
as the standards proposal advances.[^asyncify]

## How OTP fits into the stack

OTP is primarily version-matched BEAM code loaded into ERTS, not a second native
port. The initial profile must include enough `kernel` and `stdlib` to boot an
application and prove supervision, but package presence alone does not establish
compatibility. Modules can depend on files, sockets, terminals, dynamic code,
NIFs, drivers, distribution, runtime configuration, and timing assumptions.

The compatibility closure therefore combines:

- `.app` and release metadata;
- BEAM import and instruction analysis;
- native artifact, NIF, driver, and `on_load` inventory;
- runtime tracing in the native oracle and browser target;
- loader-policy and capability decisions; and
- positive and negative conformance tests.

The proposed support tiers are:

- **Tier 0 — POC semantic kernel:** terms, processes, messages, selective
  receive, timers, GC, ETS, links, monitors, names, application boot, and a
  supervisor restart using matching `kernel`/`stdlib` modules;
- **Tier 1 — core OTP behaviours:** `gen_server`, `gen_statem`, `supervisor`,
  application lifecycle, and selected standard-library modules;
- **Tier 2 — pinned Elixir core:** only modules whose reachable closure and
  semantics pass the same loading, native-boundary, and runtime tests; and
- **Tier 3 — optional applications and browser capabilities:** admitted one at
  a time with explicit authority and support records.

Elixir compatibility is downstream of ERTS and OTP validity. The POC does not
need Elixir. A later Elixir profile pins exact Elixir, OTP, and application
versions; disables compiler, shell, runtime eval, arbitrary code paths, and
unsupported native dependencies; and compares representative workloads with
the native oracle.

## Security from day one

Core Wasm validation constrains module and linear-memory access and supplies no
ambient host authority. It does not make ERTS or linked C code memory-safe.
Memory-unsafe bugs can corrupt data or control-relevant state inside linear
memory, and microarchitectural threats require browser-engine defenses beyond
architectural bounds checks.[^wasm-security][^swivel]

One ERTS instance and its admitted code form one trusted failure domain.
Mutually untrusted BEAM programs require separate Worker-plus-Wasm generations
unless a future design proves a stronger boundary. The browser engine, loader,
manifest verifier, generated JavaScript, broker, page bootstrap, delivery
origin, and update path are part of the trusted computing base.

Non-negotiable controls include:

- immutable, verified startup code and lower-boundary BEAM admission;
- a small reviewed import ABI and no generic JavaScript escape;
- fixed argv, environment, boot file, root, and code path;
- validation and overflow-safe length checks before allocation or term decode;
- per-generation quotas and backpressure for processes, memory, queues, timers,
  host requests, output, and Workers;
- no untrusted Erlang External Term Format at the browser boundary;
- structured diagnostics with redaction and rate limits;
- forced termination and stale-generation rejection;
- sanitizers, fuzzing, failure injection, and loader-negative tests; and
- reproducible builds, SBOM, provenance, security-update ownership, and browser
  delivery policy.

## Build, verification, and upgrade discipline

The initial cross-build uses a same-release native Erlang bootstrap and a pinned
Emscripten SDK. All compile and link stages use consistent pthread settings.
BeamAsm is disabled. Generated sources, configure cache entries, target flags,
link settings, memory settings, and JavaScript glue are captured as provenance.

Testing proceeds from focused target probes to native/Wasm differential tests,
browser integration, adversarial loading, lifecycle failure injection, and
resource scaling. The same manifest and test identities appear in every result.
An upstream security update or toolchain update creates a fresh generation and
reruns the complete applicable suite.

## Milestones to the first proof of concept

These milestones are a bounded feasibility program. Detailed unchecked work and
gates live in the [runtime milestone plan](../60-planning/erts-webassembly-runtime-milestones.md).

| Milestone | Outcome | Runtime-loading obligation | Exit evidence |
| --- | --- | --- | --- |
| P0 — governed baseline | Fix trust model, POC non-goals, source/toolchain pins, topology candidates, safety ceilings, finite unsupported inventory, and stop conditions | Specify trust anchor, manifest, bounds matrix, boot profile, module policy, loader partial order, and generation ownership before code | Reviewed baseline and reproducible empty toolchain environment |
| P1 — target and dependency probes | Identify actual compile, thread, atomic, TLS, function-pointer, allocator, time, poll, and `wasm32` gaps | Run production-shaped synthetic pthread, fixed-memory, and automatic-main-suppression probes through the selected trust/delivery paths; validate topology and exhaustion mechanics without claiming the ERTS pool size | Successful load, responsiveness, abort/restart, and cleanup in pinned Chrome and Firefox—or stop |
| P2 — interpreter artifact and outer loader | Link interpreter-only ERTS with the smallest browser system, progress, and generation-cleanup layer | Verify manifest/assets; enforce bounds; use a conservative pool and fixed shared memory; instantiate with `main` suppressed and an import/export allowlist; reject early entry, skew, and cancellation leaks | Repeatable instantiate/cancel/fail cleanup in both browsers; no OTP or full-pool claim yet |
| P3 — immutable ERTS/OTP cold boot | Reach `init`, start the matching minimal `kernel`/`stdlib` plus `erts_wasm_poc`, and stop at `booted-for-qualification` | Mount and seal the verified release before the one explicit ERTS entry; keep `erts_wasm_loader_probe` out of startup; enforce the full closure; separately census roles, Worker hosts/pool slots, and supervisors; prove measured pool `N`/`N-1`; attest identity | Deterministic boot/idle/wakeup, pool sizing, UI responsiveness, delivery-negative tests, bounded-input rejection, and boot-failure cleanup in both browsers |
| P4 — Tier-0 semantic capsule | Preserve non-waivable core ERTS behavior against native OTP and execute `erts_wasm_loader_probe` | Atomically consume the sole exact authorization and close admission before normal prepare/finish publication; prove direct/undeclared/`on_load`/post-ready bypasses fail | Native/Wasm core semantics match; predeclared environmental tolerances pass; the qualification harness may reach `ready` |
| P5 — bounded host progress and teardown | Harden asynchronous progress, cancellation, crash recovery, and generation cleanup | Bind all requests/completions to generation; abort during each loading state; prove the watchdog terminates the complete Worker graph within a declared supervisor-scheduled-time deadline and replaces frozen/discarded generations at the next lifecycle opportunity | UI responsiveness, Worker/resource census, forced-stop tests, stale-completion rejection, and stable repeated-cycle slope |
| P6 — POC qualification package | Produce and review a bounded go/no-go result for deeper work | Publish artifact/manifest hashes, exact load trace, negative and cancellation matrices, closure/admission report, and unsupported surface | Accepted P6 package plus reproducible P0–P5 evidence in both browsers and no stop condition |

The proof of concept is not achieved at P2 or P3. It is achieved only after P6.
DOM rendering, network, storage, Elixir, hot code replacement, and broad OTP are
explicitly outside this program.

## Milestones from proof of concept to in-depth ERTS compatibility

This program begins only after the POC evidence is reviewed and accepted.
Before C1, product owners must freeze qualification budgets or approve a
non-gameable method that derives them from named POC/native baselines. P0 safety
ceilings protect the experiment; they are not product-performance budgets.

| Milestone | Outcome | Runtime-loading obligation | Exit evidence |
| --- | --- | --- | --- |
| C1 — compatibility inventory and oracle | Expand and automate the POC machine-readable OTP/ERTS support surface and differential harness | Extend the already enforced module/native/capability closure, hashes, dependencies, and bypass-negative tests | No unresolved module, native, import, loader, or capability edge in the admitted profile |
| C2 — hardened code lifecycle | Decide and implement immutable-only, signed-bundle, or constrained replace/purge semantics | Fuzz BEAM validation; govern `on_load`, literals, code indices, purge, rollback, cache, and generation replacement | Positive/negative loader conformance and rollback without leaked literals or stale code |
| C3 — scheduler and browser-state compatibility | Qualify scheduler counts, dirty/async work, fairness, timers, throttling, suspension, and bfcache policy | Loader declares topology and browser features; resume/replacement cannot revive a stale generation | Native/Wasm scheduler traces and browser-state matrix within approved semantic tolerances |
| C4 — memory and shared-state compatibility | Bound GC, binaries, allocators, ETS, atoms, literals, mailboxes, and fragmentation | Enforce artifact/module budgets before load and reclaim generation-owned code/literals on replacement | Stress distributions and repeated-load/dispose memory slopes within approved budgets |
| C5 — core OTP and pinned Elixir profile | Expand through Tier 1 and Tier 2 one reachable closure at a time | Every admitted module, application, native edge, and boot change updates the manifest and loader tests | Versioned compatibility matrix and representative application conformance |
| C6 — hardened broker and optional browser capabilities | First prove overflow-safe frames, immutable publication/snapshots, ERTS-owned response copies, queue saturation, concurrent-mutation resistance, and `+S 1:1` progress; then add services separately | Loading a profile grants only declared capability handles; removing a feature removes its imports and modules | Generic broker gate plus per-capability security review, failure tests, quotas, and removable build/profile |
| C7 — renderer and application lifecycle | Connect a bounded semantic UI protocol and multiple same-trust components | Component/release bundles are admitted, versioned, cancelled, and unloaded with runtime generations | Functional, accessibility, ownership, backpressure, and teardown evidence |
| C8 — security and supply-chain hardening | Establish production-oriented trust, fuzzing, CSP, provenance, incident, and update controls | Sign/verify releases, exercise revocation and rollback, reject downgrade/skew, audit loader and broker | Reviewed threat model, fuzz/sanitizer results, reproducible SBOM/provenance, update drill |
| C9 — performance and browser qualification | Test against the previously frozen size, startup, memory, latency, responsiveness, and support budgets | Measure fetch/verify/compile/instantiate/mount/boot/module-load phases separately; validate caching | Supported browser/OS matrix and budget report with native baselines and distributions |
| C10 — maintained ERTS-Wasm release profile | Own upstream rebases, compatibility policy, release cadence, and deprecation | Loader/manifest versioning supports migrations without accepting old vulnerable generations | Two successful upstream/toolchain update rehearsals and an approved support decision |

Hot loading is deliberately concentrated in C2. If product requirements do not
justify it, C2 can resolve to a rigorously immutable runtime while still
hardening BEAM admission and generation replacement.

### Required measurements

- raw and compressed bytes for Wasm, loader, Worker scripts, release pack, OTP,
  optional Elixir, symbols, and application bundles;
- fetch, hash/signature verification, compile, instantiate, Worker readiness,
  release mount, ERTS initialization, OTP boot, module admission, and ready time;
- initial, steady, peak, post-GC, post-unload, and post-disposal Wasm, JS, response,
  Worker, and optional DOM memory;
- complete Worker/thread/resource timelines by generation;
- process spawn, local message, selective receive, timer, ETS, link/monitor,
  supervisor recovery, and code-lifecycle behavior;
- UI long tasks, idle CPU, wake latency, timer drift, host-call latency, and
  event-to-paint latency where a renderer exists;
- repeated boot/dispose, load/reject/replace, request/cancel, crash/restart, and
  route-load slopes; and
- build duration, reproducibility, import closure, patch-stack size,
  vulnerability age, and upstream rebase effort.

Numeric budgets must come from product requirements and native/browser baseline
measurements, not from this architecture note or historical benchmark headline
numbers. WebAssembly performance must be attributed by phase and subsystem;
whole-application research cautions against extrapolating from small kernels.[^wasm-performance]

## Stop and reassessment conditions

Stop or explicitly redesign if:

- minimal boot requires broad POSIX emulation or ambient authority;
- the target requires pervasive changes to common process, scheduler, GC, or
  loader semantics rather than a reviewable platform layer;
- a blocking wait or ERTS execution remains on the UI agent;
- the loader can mix generations, accept unmanifested code, bypass lower-boundary
  admission, or leave partial resources after failure;
- any Worker or browser resource cannot be assigned to and revoked with one
  runtime generation;
- any Tier-0 process, message, link, monitor, GC, ETS, application, or
  supervision semantic diverges; only predeclared environmental differences
  such as clock resolution or suspension policy may use approved tolerances;
- repeated load/dispose cycles show a positive resource slope;
- cross-origin isolation is incompatible with the intended deployment; or
- approved size, startup, memory, responsiveness, security-update, or
  maintenance budgets cannot be met.

## Alternatives considered

- **New or clean-room BEAM implementation:** rejects upstream semantic fidelity
  and update leverage; not the default project.
- **Compile applications directly to native Wasm:** useful for a different
  restricted language model, but does not preserve ERTS/OTP semantics.
- **ERTS on the UI thread:** incompatible with responsiveness and hard recovery.
- **Complete Unix emulation:** too broad in code, authority, and maintenance.
- **Browser WASI as the first ABI:** deferred because browser embedder and thread
  gaps remain.
- **Threadless ERTS as a build flag:** not supported by current ERTS; a
  cooperative single-thread fork would be a separate high-risk research program.
- **Asyncify everywhere:** increases transformed surface and reentrancy risk;
  bounded probes only.
- **Arbitrary hot code loading:** unnecessary for the POC and optional even in
  the mature profile.

## Principal unresolved questions

1. Which mandatory OTP 29.0.6 initializers first fail under the pinned
   Emscripten target, and how localized are the fixes?
2. What exact Worker and thread graph exists from preflight through teardown for
   each candidate topology?
3. Which allocator, `mmap`, page, signal, poll, function-pointer, atomic,
   `setjmp`/`longjmp`, and alignment assumptions fail under `wasm32`?
4. What is the exact minimal preload and `kernel`/`stdlib` closure for Tier 0?
5. Where should lower-boundary module admission live without introducing an
   unmaintainable fork of the upstream loader?
6. Can immutable generation replacement fully reclaim Workers, linear memory,
   literal/code state, requests, and JavaScript views?
7. How should foreground, throttled, suspended, and bfcache states affect
   monotonic time, timers, broker requests, and runtime replacement?
8. Which OTP and later Elixir paths implicitly require native libraries, files,
   terminals, sockets, distribution, or mutable code?
9. Is cross-origin isolation compatible with the intended embeddings and
   third-party assets?
10. What measured profile is valuable enough to justify long-term ERTS, emsdk,
    browser, loader, and security-update ownership?

## Recommendation

Authorize P0–P6 only as a bounded proof program. Begin with upstream OTP 29.0.6,
an interpreter-only Emscripten build, matching immutable `kernel`/`stdlib`, no
optional browser capabilities, fixed shared memory, one pre-ready qualification
authorization consumed and closed before its normal load, ERTS execution off
the UI agent, and generation-scoped teardown. Make the outer loader and inner
BEAM admission path observable from the first target probe.

Proceed to C1–C10 only if the complete POC—not merely compilation or cold
boot—passes and the product-budget decision method is fixed. Expand
compatibility one manifest closure and one capability at a time. Retain
immutable generation replacement as the default; add hot loading only if a
concrete product need justifies its separate semantic and security burden.

## Consolidation provenance

This note consolidates and supersedes two developing architecture notes without
erasing their dated reasoning:

- [ERTS architecture and the minimum browser WebAssembly port](../90-archive/erts-architecture-and-minimal-browser-webassembly-port.md)
- [First-party Erlang/OTP ERTS WebAssembly runtime stack](../90-archive/first-party-erlang-otp-erts-webassembly-runtime-stack.md)

The archived originals preserve the detailed research path. This note is the
canonical current architecture and the linked plan is the canonical milestone
checklist.

## Related research and planning

- [Component implementation deep dive](erts-webassembly-component-implementation-deep-dive.md)
- [Component implementation map](../10-maps/erts-webassembly-component-implementation.md)
- [Component-seam inquiry](../40-inquiries/which-component-seams-block-the-first-erts-wasm-proof.md)
- [Component research journal](../50-journal/2026-09-14-erts-webassembly-component-implementation-research.md)
- [ERTS WebAssembly runtime milestones](../60-planning/erts-webassembly-runtime-milestones.md)
- [Minimum browser platform-contract inquiry](../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md)
- [First-party ERTS feasibility inquiry](../40-inquiries/can-blazex-build-and-own-an-erts-webassembly-runtime-stack.md)
- [Runtime-stack map](../10-maps/erts-webassembly-runtime-stack.md)
- [Minimum-port component map](../10-maps/erts-architecture-and-minimal-browser-port.md)
- [Component deep-dive journal](../50-journal/2026-09-14-erts-architecture-and-minimal-webassembly-port-deep-dive.md)
- [Original runtime deep-dive journal](../50-journal/2026-09-13-first-party-erts-webassembly-runtime-deep-dive.md)

## Sources

[^beam-book]: Erik Stenman and contributors, [*The BEAM Book*](https://blog.stenmans.org/theBeamBook/), first edition, 2025; [source note](../30-sources/stenman-2025-beam-book.md).
[^erts-source]: Erlang/OTP Project, [OTP 29.0.6 / ERTS 17.0.6 source](https://github.com/erlang/otp/releases/tag/OTP-29.0.6), commit `e07fd07837e5aa845657f5fa340637121e451d47`; [source-architecture note](../30-sources/erlang-otp-project-2026-erts-build-runtime-and-source.md).
[^otp-boot]: Erlang/OTP Project, [`init` documentation](https://www.erlang.org/doc/apps/erts/init.html), boot/release documentation, and tagged source; [boot and compatibility note](../30-sources/erlang-otp-project-2026-otp-boot-security-and-compatibility.md).
[^interpreter]: John Högberg and the Erlang/OTP Project, engineering articles on the [BEAM loader](https://www.erlang.org/blog/a-brief-beam-primer/), [interpreter](https://www.erlang.org/blog/a-closer-look-at-the-interpreter/), and [message passing](https://www.erlang.org/blog/message-passing/); [source note](../30-sources/erlang-otp-project-erts-interpreter-and-message-passing-articles.md).
[^memory]: Konstantinos Sagonas and Jesper Wilhelmsson, [“Efficient Memory Management for Concurrent Programs that Use Message Passing”](https://doi.org/10.1016/j.scico.2006.02.006), 2006; [source note](../30-sources/sagonas-wilhelmsson-2006-erlang-memory-management.md).
[^scaling]: Phil Trinder et al., [“Scaling Reliably”](https://doi.org/10.1145/3107937), 2017; [source note](../30-sources/trinder-et-al-2017-scaling-reliably-erlang.md).
[^emscripten]: Emscripten contributors, [pthreads](https://emscripten.org/docs/porting/pthreads.html), runtime, filesystem, networking, and toolchain documentation; [source note](../30-sources/emscripten-project-2026-browser-porting-runtime.md).
[^asyncify]: Emscripten contributors, [Asyncify and JSPI](https://emscripten.org/docs/porting/asyncify.html); see also the [browser standards note](../30-sources/webassembly-standards-2026-browser-security-and-threads.md).
[^web-threads]: WebAssembly Community Group, WHATWG, W3C, and Emscripten, threading, Worker, CSP, and cross-origin-isolation standards; [source note](../30-sources/webassembly-standards-2026-browser-security-and-threads.md).
[^wasi]: WebAssembly Community Group and WASI Subgroup, proposal records; [WASI and threading source note](../30-sources/webassembly-project-2026-wasi-and-threading-status.md).
[^browsix]: Bobby Powers, John Vilk, and Emery D. Berger, [“Browsix”](https://doi.org/10.1145/3037697.3037727), ASPLOS 2017; [source note](../30-sources/powers-vilk-berger-2017-browsix.md).
[^wasm-performance]: Abhinav Jangda et al., [“Not So Fast”](https://www.usenix.org/conference/atc19/presentation/jangda), USENIX ATC 2019; [source note](../30-sources/jangda-et-al-2019-webassembly-performance.md).
[^wasm-security]: Daniel Lehmann, Johannes Kinder, and Michael Pradel, [“Everything Old Is New Again”](https://www.usenix.org/conference/usenixsecurity20/presentation/lehmann), USENIX Security 2020; [source note](../30-sources/lehmann-kinder-pradel-2020-webassembly-binary-security.md).
[^swivel]: Shravan Narayan et al., [“Swivel”](https://www.usenix.org/conference/usenixsecurity21/presentation/narayan), USENIX Security 2021; [source note](../30-sources/narayan-et-al-2021-swivel.md).
