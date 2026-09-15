---
title: "ADR-0001 — Implementation languages and BEAM qualification sequence"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - architecture-decision
  - implementation-language
  - compatibility
  - elixir
  - erlang
  - erts
  - webassembly
aliases:
  - "ADR-0001"
---

# ADR-0001 — Implementation languages and BEAM qualification sequence

## Decision metadata

| Field | Value |
| --- | --- |
| Status | proposed |
| Date | 2026-09-14 |
| Owners | Repository maintainers; ERTS-port, browser-host, and compatibility owners when assigned |
| Scope | ERTS target code, browser host, Wasm ABI, proof payloads, compatibility profiles, tests, and shipped build inputs |
| Supersedes | None |
| Superseded by | None |
| Review triggers | P1 toolchain or ABI failure; platform changes spreading into ERTS semantics; an OTP or emsdk ABI change; selection of the C5 Elixir patch; inability to preserve Worker/DOM authority separation; or a proposal to add Rust or handwritten C++ |

## Context

This project preserves the official upstream ERTS implementation and matching
OTP BEAM modules while adapting the smallest practical platform layer to a
browser. It also needs a browser-native owner for asynchronous loading,
Workers, lifecycle, capabilities, and an optional renderer. One implementation
language does not fit both sides without either rewriting ERTS or wrapping
browser APIs in another unnecessary native runtime.

The first proof also needs strong fault attribution. An Elixir program is BEAM
code, but a useful Elixir profile adds the exact `elixir` application, compiler
output, modules, metadata, protocols, packaging assumptions, and a larger
reachable dependency closure. If that is the only first payload, a failure may
belong to the ERTS port, OTP boot, code admission, or Elixir compatibility.

This is a source-ownership decision, not an artifact-purity decision.
The selected Emscripten browser build is expected to emit both WebAssembly and
JavaScript, and Erlang or Elixir sources will become BEAM artifacts.

## Decision

1. **Keep ERTS and its browser platform adapter in upstream-compatible C.**
   Preserve the generated portable interpreter and implement only the required
   `sys`, thread, poll/wakeup, time, entropy, filesystem, and small static bridge
   seams in the C dialect and build conventions accepted by the pinned OTP
   source. BeamAsm remains disabled. Do not add handwritten C++ to the initial
   platform layer.
2. **Author the maintained browser control plane in strict TypeScript.** The
   trusted bootstrap, manifest verifier, generation supervisor, Worker registry,
   watchdog, capability broker, browser harness, and later renderer compile to
   pinned JavaScript artifacts. Keep shared protocol code free of ambient DOM
   authority, compile runtime-Worker code against Worker APIs, and isolate DOM
   APIs in the page supervisor or renderer targets that own them.
3. **Treat TypeScript types as development checks, not boundary validation.**
   Decode every manifest, browser event, Worker message, and Wasm-authored frame
   from an untrusted representation. Enforce runtime schemas, lengths, integer
   ranges, generation and capability identity, state transitions, quotas, and
   ownership before allocation or effect.
4. **Use Erlang for the P0–P6 semantic proof.** Build `erts_wasm_poc` and the
   separately admitted `erts_wasm_loader_probe` with the pinned same-release
   toolchain, and run identical BEAM digests against the native and browser
   oracles. This isolates ERTS, OTP, loader, scheduler, and lifecycle evidence
   from the additional Elixir runtime closure.
5. **Admit Elixir incrementally after the Erlang foundation passes.** Program B
   starts only after P6 is accepted, selects one exact Elixir patch and trusted
   compiler, and closes its complete module/native/capability graph. ELX-1
   admission follows the Tier-1 OTP baseline, then advances through separately
   reported language/runtime, OTP-behaviour, and representative-application
   profiles. A smoke module does not establish general Elixir support.
6. **Defer Rust and new C++ components.** Either language requires a new,
   component-specific ADR with measured ownership, ABI, security, size,
   debugging, supply-chain, and update advantages. Rust may be reconsidered for
   an isolated leaf that owns its memory behind a narrow byte or message ABI;
   it is not a wrapper intended to make C-owned ERTS state memory-safe.
7. **Keep the host ABI language-neutral and small.** Prefer fixed-width scalars,
   offsets and lengths into bounded snapshots, opaque handles, explicit status
   values, generation identifiers, and documented buffer ownership. Do not pass
   JavaScript objects, retain ERTS pointers in the host, expose a generic call
   escape, or use ETF at the browser boundary.

The decision remains proposed until P1 supplies executable toolchain and ABI
evidence. It authorizes no support claim and completes no milestone gate.

## Rationale

- C keeps the target changes legible beside upstream ERTS, uses its existing
  platform seams, and avoids a second systems-language build and ABI across
  scheduler, allocator, loader, and thread state.
- TypeScript directly models browser asynchronous APIs and state machines while
  allowing source-level separation between Worker and DOM authority. Runtime
  validation remains mandatory because its types are erased.
- Erlang provides a smaller, easier-to-attribute qualification closure than the
  planned Elixir profile while exercising the required Tier-0 semantics and
  code-loading path with matching OTP libraries.
- Deferring Elixir makes failures attributable and prevents one successful
  module from becoming an unsupported general-compatibility claim.
- Deferring Rust is provisional rather than ideological. If the supposedly
  small C layer becomes a substantial, self-contained hostile-input parser or
  ownership-heavy subsystem, its safety case must be reconsidered.

## Consequences

### Enables

- Upstream-shaped ERTS patches and clearer OTP/emsdk rebases.
- Browser-native ownership of Workers, requests, capabilities, lifecycle, and
  the DOM without granting ERTS ambient browser authority.
- Identical Erlang BEAM capsules for native/Wasm differential evidence.
- Narrow Elixir claims that grow only with versioned closure and lifecycle
  evidence.
- Independent security review and fuzzing of the C, Wasm ABI, TypeScript, and
  BEAM admission boundaries.

### Constrains

- The shipped system is intentionally multi-language and must pin all compilers,
  package managers, generated outputs, source maps, and runtime libraries.
- C remains memory-unsafe inside Wasm and requires bounds checks, assertions,
  sanitizers where supported, fuzzing, import/export review, and generation-
  fatal handling of corrupted state.
- TypeScript builds must use strict checking and authority-specific library
  scopes, but no type annotation may substitute for an executable validator.
- Mix, IEx, compiler applications, eval, arbitrary code loading, and runtime
  configuration providers remain outside the first Elixir profiles.
- A new Rust or C++ dependency cannot enter incidentally through a helper
  library; it needs an explicit decision and provenance update.

## Alternatives considered

### Rewrite or wrap ERTS primarily in Rust

Rejected for the first proof. ERTS state and the required platform seams are C-
owned, so broad Rust integration would still contain unsafe FFI while adding a
set of allocator ownership and interoperability obligations, a panic model,
build graph, target configuration, and ABI compatibility matrix. Reconsider
only for an isolated owner of its own memory.

### Write the complete host in C or Emscripten inline JavaScript

Rejected. Browser lifecycle, Fetch/WebCrypto, Worker ownership, cancellation,
and DOM operations are browser APIs. Hiding them in inline snippets would make
authority, state, generated code, testing, and teardown harder to review.

### Use handwritten JavaScript rather than TypeScript

Rejected for maintained control-plane code. JavaScript remains the runtime
artifact, but strict TypeScript provides useful static checks for lifecycle
states and message variants. A small Emscripten-specific JavaScript shim may be
unavoidable and must remain pinned, bounded, and reviewed.

### Use Elixir as the only proof payload

Rejected as a proof-ordering strategy, not as a product language. It combines
the foundational ERTS/OTP question with a larger, independently versioned
runtime profile and makes negative evidence harder to localize.

### Introduce a general C++ platform layer

Rejected. The initial target disables the C++ BeamAsm/JIT path, and no POC
requirement currently offsets the added ABI, exceptions, lifetime, and upstream-
drift surface.

## Impact review

### Compatibility

The language split preserves the upstream C runtime and tests ordinary BEAM
artifacts. Erlang establishes only the declared Tier-0 baseline. Elixir support
is an exact-version, machine-readable profile advanced through discrete gates.

### Security and trust

Wasm does not make ERTS or linked C memory-safe. TypeScript types disappear from
the emitted JavaScript. Both sides must validate their own trust boundary, and
all admitted Erlang or Elixir code within one ERTS generation remains in one
trusted failure domain.

### Accessibility

No renderer is part of the POC. A later TypeScript renderer owns a bounded DOM
subtree and keeps semantic/accessibility validation outside ERTS; this decision
does not qualify that renderer.

### Packaging and dependencies

The manifest, SBOM, and provenance must cover OTP sources and generators,
emsdk/Clang/LLVM, the TypeScript compiler and package graph, emitted JavaScript
and Worker assets, BEAM compiler inputs, and later the exact Elixir compiler and
profile closure.

### Cross-backend portability

ERTS-facing C and the byte-oriented host ABI may be reusable by another target.
The TypeScript host is intentionally browser-specific. A future WASI or native
embedder must implement the same semantic contract without inheriting browser
authority assumptions.

## Evidence basis

- **Local observation:** The pinned ERTS inspection identifies a generated C
  interpreter and existing target/platform seams rather than a first-party
  browser target.
- **Source fact:** Emscripten documents C/C++ compilation, generated
  JavaScript, pthread Workers, controlled startup, and browser-specific runtime
  limitations.
- **Source fact:** The TypeScript documentation distinguishes DOM and WebWorker
  API libraries and states that compile-time types are erased from emitted
  JavaScript.
- **Source fact:** The Rust target documentation confirms Emscripten
  interoperability but warns that target flags participate in ABI
  compatibility and that the target is not extensively tested in Rust's CI.
- **Project synthesis:** The compatibility profile separates the Tier-0 Erlang
  kernel, Tier-1 OTP behaviours, and exact-version Tier-2 Elixir profile.

These observations, source facts, and architectural inferences are not compile,
boot, security, performance, or maintainability evidence for this repository.

## Unresolved evidence

- P1 must prove that the pinned OTP generators and C sources cross-compile
  without a pervasive rewrite and must record the exact C/JS ABI.
- P1 must compile authority-separated strict TypeScript probes and inspect their
  emitted JavaScript, imports, globals, source maps, and Worker behavior.
- P2 must show that the C adapter and JavaScript shim remain small enough for
  line-by-line review and update ownership.
- P4 must prove identical Erlang BEAM digests and normalized native/Wasm Tier-0
  behavior.
- C1 and C5 must discover, admit, and test the exact Elixir closure one increment
  at a time.
- Security and supply-chain milestones must test whether the multi-language
  build remains reproducible, fuzzable, observable, and updateable.

## Change control

Changing a language owner, adding Rust or handwritten C++, moving a browser
authority into Wasm, or advancing an Elixir support level requires review of
this ADR, the canonical architecture, component notes, milestone gates,
manifest/SBOM/provenance rules, and compatibility matrix. Never reuse
`ADR-0001`; supersede it with a new ADR if the durable decision changes.

## Connections

- [Canonical runtime architecture](../erts-webassembly-runtime-architecture-and-milestones.md)
- [ERTS build and BEAM interpreter](../components/erts-build-and-beam-interpreter.md)
- [Artifact loader and runtime generations](../components/artifact-loader-and-runtime-generations.md)
- [Capability broker and browser services](../components/capability-broker-and-browser-services.md)
- [OTP and Elixir compatibility profile](../components/otp-and-elixir-compatibility-profile.md)
- [Planning roadmap](../../60-planning/erts-webassembly-runtime-milestones.md)
- [P0 governed-baseline plan](../../60-planning/01-proof-of-concept/p0-governed-baseline-and-proof-contract/README.md)
- [P1 target-probe plan](../../60-planning/01-proof-of-concept/p1-target-and-dependency-probes/README.md)
- [C5 OTP and Elixir qualification plan](../../60-planning/02-in-depth-erts-compatibility/c5-core-otp-and-pinned-elixir-profile/README.md)
- [Language-decision journal](../../50-journal/2026-09-14-language-boundary-and-elixir-increment-decision.md)

## Sources

- [Erlang/OTP ERTS build, runtime, and source](../../30-sources/erlang-otp-project-2026-erts-build-runtime-and-source.md)
- [Emscripten browser porting runtime](../../30-sources/emscripten-project-2026-browser-porting-runtime.md)
- [TypeScript browser-host type boundaries](../../30-sources/typescript-project-2026-browser-host-type-boundaries.md)
- [Rust Emscripten target and FFI boundaries](../../30-sources/rust-project-2026-emscripten-target-and-ffi-boundaries.md)
- [Elixir OTP compatibility, code loading, and releases](../../30-sources/elixir-project-2026-otp-29-compatibility-and-releases.md)
