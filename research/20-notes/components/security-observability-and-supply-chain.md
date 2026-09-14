---
title: "Security, observability, and supply chain"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - observability
  - provenance
  - security
  - supply-chain
  - testing
  - webassembly
aliases:
  - "ERTS-Wasm assurance component"
---

# Security, observability, and supply chain

## Decision

Build assurance into every component from P0. Wasm contains an instance from
the browser host; it does not make ERTS C code memory-safe or isolate mutually
untrusted BEAM applications inside one VM. The outer Worker generation is the
hard recovery boundary, narrow imports are the authority boundary, and exact
build/runtime evidence is the support boundary.

## Threat model

Adversaries include malicious or malformed release/BEAM/configuration bytes,
host frames and network/storage data, a compromised dependency or build step,
cache/service-worker skew, vulnerable ERTS C or static native code, resource
exhaustion by admitted BEAM code, stale asynchronous completions, and an
unexpected browser lifecycle transition. The browser engine, trusted bootstrap,
manifest verifier, generated Emscripten shell, broker, renderer, delivery
origin, update path, and signing/build systems are in the trusted computing
base.

WebAssembly validation and bounds checks supply no ambient host access and
protect outside the module, but unsafe-source memory bugs can still corrupt
objects and control-relevant state within linear memory. Research has found
real unsafe-language bug classes in Wasm binaries, while speculative threats
can require engine-level defenses beyond architectural isolation.[^wasm-binary][^swivel]

One ERTS generation therefore hosts same-trust code. Strong isolation between
tenants or plugins requires distinct Worker-plus-Wasm generations and distinct
capability sets; Erlang processes and OTP supervisors are not memory-safety
sandboxes.

## POC controls

- Authenticate a coherent immutable generation before effect and recheck BEAM
  admission below high-level code APIs.
- Fix argv, environment, root, code paths, preloads, module hashes, core
  `on_load`, imports, exports, Workers, memory, capabilities, and unsupported
  surface in the manifest.
- Enforce encoded/expanded lengths and integer-overflow-safe calculations before
  decode, allocation, decompression, atom interning, queue reservation, or DOM
  mutation.
- Use fixed shared memory and explicit process/global quotas. Queue saturation,
  OOM, Wasm trap, watchdog timeout, and invariant failure have declared breach
  actions; corrupt or OOM generations are not recovered in place.
- Keep ETF, eval, arbitrary code loading, generic JavaScript, filesystem,
  sockets/distribution, OS processes, dynamic NIF/driver loading, and renderer
  authority outside the POC.
- Run native and Emscripten AddressSanitizer/UndefinedBehaviorSanitizer where
  supported, assertions, stack checks, safe-heap/debug variants, loader and
  bridge fuzzers, malformed corpus replay, and browser failure injection.[^emscripten]
- Make a scheduled owner outside ERTS able to terminate the complete Worker
  graph. Document that the browser can freeze that owner; the deadline applies
  once it is scheduled, not while the user agent runs no tasks.

## Observability model

Use one bounded event envelope:

```text
schema | generation | manifest | monotonic-sequence | timestamp-source
component | state/event | operation/test | subject-id | sizes | outcome
```

The loader, Worker registry, platform queues, ERTS identity endpoint, test
harness, broker, renderer, and cleanup registry emit compatible events. Keep
payloads typed and small; hash or classify artifacts rather than logging bytes.
Do not log secrets, capability tokens, raw request/response bodies, arbitrary
terms, cookies, credentials, URLs with sensitive parameters, or complete DOM
text.

Qualification builds may enable detailed ERTS scheduler, GC, allocator, signal,
code, and ETS tracing. Product builds expose only aggregate, rate-limited health
and fatal records. A diagnostic budget specifies events/bytes per interval,
retention, redaction, dropped-event counters, and behavior when the sink is
unavailable. Logging may never block scheduler or cleanup progress.[^otp-tools]

Metrics are distributions and slopes, not a single successful screenshot:
loader phase time, Worker census, UI long tasks, idle CPU, scheduler fairness,
timer drift, queue depth, GC pauses, allocator committed/live bytes, atoms,
binaries, ETS, code/literals, capability latency, cancellations, and repeated
resource settlement. Every result carries exact browser, emsdk, manifest,
source, build, profile, and test identities.

## Supply-chain implementation

The generation has many skewable inputs: OTP source and bootstrap OTP, emsdk,
build image and tools, C dependencies, patches, generated interpreter, Wasm,
JavaScript shell, pthread Worker script, release modules/assets, manifest, and
tests. A final checksum does not describe how they were produced.[^supply]

For POC qualification, retain deterministic build commands, source and tool
digests, patch ledger, generated-file provenance, build identity, artifact
hashes, licenses, and an SPDX SBOM. Rebuild independently and compare outputs;
record every explained nondeterministic field. Emit SLSA-compatible provenance
even if it is not yet signed or produced by a hardened builder.

Production hardening moves builds to an isolated hosted builder, signs
provenance and manifests, verifies policy before publication, protects and
rotates keys, supports revocation and anti-downgrade, stages generations, and
rehearses rollback without reinstalling a known-vulnerable version. Track ERTS,
OTP application, emsdk/LLVM, browser, and dependency advisories with named
owners and response targets. Two successful upstream/toolchain update
rehearsals are a release gate.

## Verification program

- Differential tests: exact native/Wasm semantic capsules with predeclared
  tolerances and allowed race outcome sets.
- Structural tests: import/export, module/native/capability closure, generated
  files, manifest schema, archive paths, and unsupported-surface assertions.
- Adversarial tests: fuzz BEAM/boot/manifest/broker/renderer, decompression and
  allocation bounds, queue races, capability revocation, cache skew, and stale
  generations.
- Lifecycle tests: fail/cancel/kill every state, freeze/background where
  supported, and repeat boot/dispose until resources converge.
- Performance tests: attribute fetch, verify, compile, instantiate, mount,
  ERTS init, OTP boot, module load, steady state, broker, render, and cleanup
  separately; older Wasm benchmark ratios are not product budgets.[^performance]
- Maintenance tests: reproduce artifacts, rebuild from an advisory patch,
  rotate trust material, reject downgrade, stage/rollback, and regenerate SBOM
  and provenance.

## Evidence gates

The POC security package contains a reviewed threat model, trust and capability
map, manifest/import/unsupported inventories, minimized fuzz corpus, sanitizer
results, failure-injection matrix, resource slopes, reproducible-build result,
SBOM, provenance, and exceptions. A clean report means tests found no issue in
their stated coverage; it is not a proof of vulnerability absence.

## Principal risks

Security controls can exist only in JavaScript and be bypassed by a lower ERTS
path. Tracing can leak secrets or change schedules. A signed build can faithfully
ship vulnerable inputs. Browser-engine and speculative vulnerabilities remain
outside the module. Fixed ceilings can turn availability attacks into frequent
generation loss if product budgets are guessed rather than measured.

## Sources

[^wasm-binary]: Daniel Lehmann, Johannes Kinder, and Michael Pradel, [binary security of WebAssembly](../../30-sources/lehmann-kinder-pradel-2020-webassembly-binary-security.md).
[^swivel]: Shravan Narayan et al., [Swivel](../../30-sources/narayan-et-al-2021-swivel.md).
[^emscripten]: Emscripten contributors, [sanitizers and debugging in the browser toolchain](../../30-sources/emscripten-project-2026-browser-porting-runtime.md).
[^otp-tools]: Erlang/OTP Project, [testing, time, and runtime observability](../../30-sources/erlang-otp-project-2026-testing-time-and-runtime-observability.md).
[^supply]: Santiago Torres-Arias et al., SLSA contributors, and SPDX contributors, [software supply-chain provenance](../../30-sources/software-supply-chain-provenance-research-and-standards.md).
[^performance]: Abhinav Jangda et al., [Not So Fast](../../30-sources/jangda-et-al-2019-webassembly-performance.md).
