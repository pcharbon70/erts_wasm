---
title: "TypeScript browser-host type boundaries"
kind: source
created: "2026-09-14"
authors:
  - "TypeScript contributors"
published: null
citation_key: "typescript-project-2026-browser-host-type-boundaries"
container: "TypeScript documentation"
edition: null
isbn: null
doi: null
url: "https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html"
accessed: "2026-09-14"
tags:
  - browser
  - javascript
  - security
  - typescript
  - web-workers
aliases:
  - "TypeScript host-language evidence"
---

# TypeScript browser-host type boundaries

## Reference

TypeScript contributors. [“TypeScript for the New
Programmer”](https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html)
and [“TSConfig Option:
lib”](https://www.typescriptlang.org/tsconfig/lib.html). Living official
documentation, accessed 2026-09-14.

## Research question or contribution

What does TypeScript contribute to a browser Worker/control-plane boundary, and
which security properties remain runtime obligations?

## Method

The record reviews the official language overview's static-checking, runtime-
behavior, and type-erasure sections and the official compiler-library catalog
for DOM, WebWorker, Atomics, SharedArrayBuffer, and typed-array declarations.

## Findings

- TypeScript statically checks JavaScript programs before execution and emits
  JavaScript with the same runtime behavior.
- Type annotations are erased. Emitted JavaScript contains no TypeScript runtime
  type information.
- **Project inference:** An external value therefore does not become trusted
  because it was assigned a TypeScript type; it still needs runtime validation.
- The compiler ships distinct high-level `DOM` and `WebWorker` API declaration
  libraries, plus declarations for Atomics, SharedArrayBuffer, and typed arrays.
- **Project inference:** By explicitly selecting the `lib` option per
  compilation target, this project can omit DOM declarations from Worker and
  shared builds. That catches source references to omitted declarations; it is
  not a runtime authority control, sandbox, or revocation of globals supplied
  by the browser or bundler.

## Relevance

Strict TypeScript is a good authoring language for the generation supervisor,
Worker registry, lifecycle state machine, capability broker, browser test
harness, and later renderer. Separate compilation targets can keep shared
protocol and Worker code from accidentally depending on DOM declarations.
Every manifest, message, frame, handle, and state transition still needs
runtime validation and quota enforcement.

## Limits

The documentation describes the language and compiler declarations, not this
project's architecture, threat model, emitted bundle, or browser behavior. It
does not prove that a TypeScript control plane is secure, race-free, bounded, or
correctly separated after bundling. The pages are living documentation and must
be version-pinned when implementation begins.

## Derived work

- [ADR-0001 — Implementation languages and BEAM qualification sequence](../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md)
- [Artifact loader and runtime generations](../20-notes/components/artifact-loader-and-runtime-generations.md)
- [Capability broker and browser services](../20-notes/components/capability-broker-and-browser-services.md)
- [Language-decision journal](../50-journal/2026-09-14-language-boundary-and-elixir-increment-decision.md)
