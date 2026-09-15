---
title: "Elixir OTP 29 compatibility, code loading, and releases"
kind: source
created: "2026-09-14"
authors:
  - "Elixir Project"
published: 2026
citation_key: "elixir-project-2026-otp29-compatibility-releases"
container: "Elixir 1.20 documentation and source"
edition: "Elixir 1.20 series"
isbn: null
doi: null
url: "https://elixir.hexdocs.pm/main/compatibility-and-deprecations.html"
accessed: "2026-09-14"
tags:
  - code-loading
  - compatibility
  - elixir
  - otp
  - releases
aliases:
  - "Elixir browser runtime profile evidence"
---

# Elixir OTP 29 compatibility, code loading, and releases

## Reference

Elixir Project documentation and source, accessed 2026-09-14:

- [compatibility and deprecations](https://elixir.hexdocs.pm/main/compatibility-and-deprecations.html);
- [Elixir 1.20 changelog](https://elixir.hexdocs.pm/changelog.html);
- [`Code`](https://elixir.hexdocs.pm/Code.html);
- [`Mix.Tasks.Release`](https://mix.hexdocs.pm/Mix.Tasks.Release.html); and
- [Elixir source repository](https://github.com/elixir-lang/elixir).

## Research question or contribution

What does a defensible claim that “Elixir runs on ERTS-Wasm” require beyond
booting a few precompiled modules?

## Method

The project's compatibility table, current stable-series changelog, code API,
and release assembly documentation were compared with the proposed immutable
ERTS/OTP browser profile. This note does not select an exact Elixir patch
version; that must be pinned when the C5 compatibility work begins.

## Findings

- The Elixir 1.20 line requires OTP 27 or later and declares compatibility with
  OTP 29. Compatibility is versioned independently from OTP and can change on
  Elixir patch releases.
- Elixir application code remains BEAM code executed by ERTS. It does not need
  a second native WebAssembly compiler to run, provided its reachable ERTS,
  OTP, and native-resource dependencies are supported.
- The `Code` module deliberately exposes source compilation, evaluation,
  bytecode loading, module availability, and purge-related operations. These
  are useful native features and incompatible with an unconditional immutable
  browser-loading policy.
- Mix releases preload compiled code, include release metadata and ERTS, strip
  unused files, and support embedded loading. They also contain OS-specific
  scripts, environment conventions, runtime configuration, temporary files,
  remote commands, and optional distribution. A native Mix release directory
  is therefore an input to a browser packager, not a browser-ready artifact.
- `runtime.exs` and configuration providers execute code during startup and can
  read environment or external services. A deterministic browser profile must
  either evaluate configuration at build time or admit a separately specified
  bounded configuration capability.

## Relevance

Elixir belongs after the ERTS Tier-0 and OTP Tier-1 proofs. The initial Elixir
profile should pin an exact Elixir patch to the exact OTP generation, compile
source on the trusted build host, package only the transitive BEAM/application
closure, and disable Mix, IEx, compiler modules, runtime evaluation, arbitrary
code paths, distribution, and dynamic native dependencies.

A representative qualification application should use ordinary Elixir
modules, processes, protocols, exceptions, maps, binaries, supervisors,
`GenServer`, and application configuration while remaining within the declared
host capability set. Its native and browser observations should be compared
under the same semantic capsule. Each supported module needs a versioned
`supported`, `partial`, or `unsupported` record with the missing primitive or
capability stated explicitly.

## Limits

The compatibility table means that upstream Elixir supports OTP 29 in its
normal environments; it is not a WebAssembly support claim. The closure of
even a small Elixir application is not yet measured here, and no Elixir BEAM
module has run in ERTS-Wasm. Exact compiler, Unicode, I/O, NIF, and application
dependencies remain experimental questions.

## Derived work

- [ADR-0001 — Implementation languages and BEAM qualification sequence](../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md)
- [OTP and Elixir compatibility profile](../20-notes/components/otp-and-elixir-compatibility-profile.md)
- [Component implementation deep dive](../20-notes/erts-webassembly-component-implementation-deep-dive.md)
