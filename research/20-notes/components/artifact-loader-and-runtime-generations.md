---
title: "Artifact loader and runtime generations"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - artifacts
  - browser
  - lifecycle
  - runtime-loading
  - security
  - webassembly
aliases:
  - "Trusted ERTS-Wasm loader"
---

# Artifact loader and runtime generations

## Decision

Treat the outer loader as a security- and lifecycle-critical state machine, not
as generated packaging glue. It is the sole creator and revoker of a runtime
generation. No ERTS, Worker, release, browser request, or renderer effect may
escape a generation identity.

## Responsibilities and boundary

The loader owns preflight, root trust, manifest authentication, byte ceilings,
artifact fetch and verification, cache/redirect policy, Worker and memory
creation, release mounting, startup deadlines, runtime identity attestation,
readiness, cancellation, and forced disposal. ERTS owns neither its browser
delivery nor the ability to recover a deadlocked hosting graph.

SRI can protect a root script whose expected digest comes from trusted HTML,
but it does not authenticate an entire Worker/Wasm/release graph. Standard
Worker fetch options do not expose a general integrity field, and descendant
module scripts do not inherit the initial script's integrity metadata.[^integrity]
The first design document must therefore name its trust root instead of saying
only “all files are hashed.”

## POC implementation

Use a small TypeScript/JavaScript generation supervisor, built separately from
the Emscripten output. Its accepted input is a schema-versioned manifest whose
expected digest or verification key is anchored by the trusted bootstrap. A
valid POC may include the pinned HTTPS origin, response headers, redirect and
cache behavior in the trusted base; a stronger design can fetch and verify all
executable bytes, then construct a Worker through a deliberately allowed and
tested mechanism. Both designs must state what a compromised root HTML
response can do.

The manifest binds as one unit:

- OTP/ERTS tag and commit, emsdk and build-image identity, patch digest, build
  flags, generated-source digest, and profile identifier;
- Wasm, generated JavaScript, pthread Worker program, release archive, boot,
  `.app`, BEAM, configuration, and qualification-capsule hashes;
- expected Wasm imports/exports, shared initial/maximum memory, complete Worker
  pool, stack sizes, accepted argv/environment/root/code paths, and required
  browser features/headers;
- modularized-output settings, automatic-`main` suppression, the sole exported
  ERTS entry, and its one-shot invocation policy;
- encoded and expanded size ceilings, startup deadlines, and generation
  resource quotas; and
- admitted module names/hashes, core `on_load` inventory, host capabilities,
  unsupported operations, and runtime identity fields.

Fetch every artifact with an explicit credential, redirect, cache, service-
worker, MIME, and cancellation policy. Check declared and observed length
before buffering; verify expanded archive entries before mounting. If Wasm is
compiled while streaming, do not instantiate it until the selected trust rule
has accepted the representation. Feed the verified module/bytes and release
data into Emscripten hooks so generated code cannot perform a second
unverified fetch.[^emscripten]

Startup advances through explicit states:

```text
created -> preflighted -> bootstrap-trust-established
  -> manifest-authenticated -> artifacts-verified
  -> workers-and-memory-owned -> instance-created-with-main-suppressed
  -> release-mounted -> explicit-erts-entry-invoked
  -> erts-initialized -> otp-booted -> identity-attested
  -> booted-for-qualification
  -> qualification-admission-consumed-and-closed
  -> qualification-module-published -> qualification-module-executed
  -> tier-0-passed -> ready

any state -> cancelling -> resources-revoked -> terminated
```

The exact ordering of Worker, memory, and instance creation varies by selected
Emscripten topology, so those effects form a documented partial order. Register
each resource before it can publish a completion. A failure at any state uses
the same idempotent cleanup routine. The runtime response must attest manifest
digest, source commit, ERTS/OTP version, profile, boot release, and a fresh
nonce before the supervisor accepts it.

The controlled-start seam is versioned build surface, not an assumption about
factory resolution. The first candidate uses modularized output with
`-sINVOKE_RUN=0` and only the necessary explicit entry mechanism exported;
`Module.noInitialRun` is a comparison path. Both must prove under each Worker
topology that factory/runtime initialization cannot call `main` or `erl_init`,
and that the supervisor invokes the entry exactly once only after the release
mount is sealed.[^emscripten]

The qualification authorization is exact and single-use. Its atomic
consumption closes all subsequent module admission before the native parser is
called. Failure during prepare, publication, execution, or the following state
transition enters cleanup and never reopens the gate.

Disposal first closes admission, increments or retires the generation epoch,
aborts browser requests, detaches renderer/event routes, closes ports and
connections, cancels host timers, terminates every recorded Worker, revokes
object URLs and handles, unmounts/drops release objects, and releases all
references to the instance, module, memory, and typed views. Cooperative ERTS
shutdown is useful evidence but not a prerequisite for hard-stop.

## In-depth implementation

Production generations add signed provenance and manifests, key rotation,
revocation and downgrade policy, staged rollout, rollback to an explicitly
allowed non-vulnerable generation, cache namespacing, and a service-worker
update protocol. An update always constructs a fresh generation; it never
mutates the ERTS/OTP/toolchain combination of a live one.

If startup caching stores a compiled `WebAssembly.Module`, the cache key must
include browser engine/build, Wasm feature set, complete generation, and
verification result. Cache corruption, old service workers, redirect changes,
offline startup, interrupted updates, and two tabs using adjacent releases all
belong in qualification.

## Evidence gates

- A valid production-sized generation reaches `ready` in pinned Chrome and
  Firefox; every state and duration appears in a bounded trace.
- Wrong root trust, manifest signature/digest, artifact hash, MIME, redirect,
  expanded size, Worker count, import, release member, module hash, or runtime
  attestation stops before the next privileged state.
- Cancellation at every state leaves no accepted late completion and returns
  Worker, port, timer, listener, request, mount, and memory counts to baseline.
- The P0-predeclared number of successful, failed, cancelled, and forced-stop
  cycles has no positive resource slope; the plan does not invent that count
  after observing results.
- Mixed-cache and mixed-generation injections never produce a partial boot.

## Principal risks

The first executable bootstrap is inherently outside the set it verifies.
Browser caching and service workers can create state not visible in a simple
network trace. Terminating a parent Worker does not, without measurement,
prove that all nested pthread Workers are gone. Browser discard can prevent
any final callback, so correctness cannot depend on `unload`.[^lifecycle]

## Sources

[^integrity]: W3C, WHATWG, and WebAssembly Community Group, [browser executable integrity and CSP](../../30-sources/browser-executable-integrity-and-rendering-standards-2026.md).
[^emscripten]: Emscripten contributors, [browser porting runtime and loading hooks](../../30-sources/emscripten-project-2026-browser-porting-runtime.md).
[^lifecycle]: WHATWG, W3C, and WICG, [browser lifecycle standards](../../30-sources/browser-platform-lifecycle-and-capability-standards-2026.md).
