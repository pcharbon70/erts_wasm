---
title: "Rust Emscripten target and FFI boundaries"
kind: source
created: "2026-09-14"
authors:
  - "Rust Project contributors"
published: null
citation_key: "rust-project-2026-emscripten-target-and-ffi-boundaries"
container: "The rustc book and The Rustonomicon"
edition: null
isbn: null
doi: null
url: "https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-emscripten.html"
accessed: "2026-09-14"
tags:
  - emscripten
  - ffi
  - rust
  - toolchain
  - webassembly
aliases:
  - "Rust language-boundary evidence"
---

# Rust Emscripten target and FFI boundaries

## Reference

Rust Project contributors. [“`wasm32-unknown-emscripten`”](https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-emscripten.html),
*The rustc book*, and [“How Safe and Unsafe
Interact”](https://doc.rust-lang.org/stable/nomicon/safe-unsafe-meaning.html),
*The Rustonomicon*. Living official documentation, accessed 2026-09-14.

## Research question or contribution

Could Rust replace or augment C in the first ERTS browser port without adding a
larger ABI, toolchain, or unsafe-FFI burden than the project can justify?

## Method

The record reviews the official target-support, Emscripten ABI compatibility,
testing, and unsafe-FFI guidance. It treats technical availability separately
from architectural suitability.

## Findings

- Rust provides a Tier-2 `wasm32-unknown-emscripten` target that can interoperate
  with Emscripten, C/C++, JavaScript, and browser APIs.
- The target documentation warns that Emscripten does not expose ABI-breaking
  changes through semantic versioning and that linker flags can select
  materially different ABIs. Mismatched Rust standard-library, Emscripten, and
  linked-code settings can produce undefined behavior.
- The documented strongest alignment path rebuilds the Rust standard library
  with the local Emscripten version and settings; the target is not extensively
  tested in the Rust repository's CI.
- Safe Rust can build a checked abstraction over unsafe code, but foreign code
  lies outside the compiler's guarantees.
- **Project inference:** A Rust wrapper does not make C-owned ERTS pointers,
  callbacks, allocators, scheduler state, or loader state safe.

## Relevance

Rust is technically possible but is not the default for the P0–P6 ERTS platform
layer. It would add rustc/Cargo, standard-library rebuilding or exact ABI
matching, allocator and panic policy, and cross-language debugging to an already
fragile cross-build. It remains a candidate for a self-contained later leaf
that owns its memory and exposes a narrow byte or message ABI if measurements
show a net safety and maintenance benefit.

## Limits

Target tier and CI coverage can change. The official documentation does not
evaluate ERTS, this repository, or a concrete Rust component. It is evidence for
additional obligations, not proof that every Rust design is unsuitable. No
Rust/Emscripten probe was run for this corpus.

## Derived work

- [ADR-0001 — Implementation languages and BEAM qualification sequence](../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md)
- [ERTS build and BEAM interpreter](../20-notes/components/erts-build-and-beam-interpreter.md)
- [Language-decision journal](../50-journal/2026-09-14-language-boundary-and-elixir-increment-decision.md)
