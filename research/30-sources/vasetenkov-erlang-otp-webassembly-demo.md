---
title: "Erlang/OTP WebAssembly demonstration"
kind: source
created: "2026-09-14"
authors:
  - "Anton Vasetenkov"
published: null
citation_key: "vasetenkov-erlang-otp-webassembly-demo"
container: "antvaset.com"
edition: null
isbn: null
doi: null
url: "https://www.antvaset.com/erlang-otp-wasm"
accessed: "2026-09-14"
tags:
  - browser
  - demonstration
  - emscripten
  - erlang
  - erts
  - otp
  - webassembly
aliases:
  - "Erlang OTP Wasm escript demo"
---

# Erlang/OTP WebAssembly demonstration

## Reference

Anton Vasetenkov. [“Erlang/OTP WebAssembly”](https://www.antvaset.com/erlang-otp-wasm).
Undated public interactive page, accessed 2026-09-14.

## Research question or contribution

Does public evidence exist of official Erlang/OTP, rather than a separate
BEAM-family virtual machine, executing in a browser WebAssembly environment?

## Method

The public page was inspected as an interactive artifact. The review recorded
only claims and behavior visible on the page and looked for source revision,
toolchain, patch, build, packaging, test, and lifecycle information. Search
snippets were not treated as evidence.

## Findings

- The page identifies itself as Erlang/OTP compiled to WebAssembly with
  Emscripten and presents an in-browser `escript` demonstration.
- This is an independent feasibility signal that some upstream-derived runtime
  path has executed in a browser. It is stronger than a statement that such a
  port should be possible, but much weaker than a reproducible build record.
- The page does not expose the exact OTP revision, Emscripten revision, patch
  stack, configure commands, complete artifact inventory, Worker topology,
  supported OTP profile, semantic test results, import policy, or teardown
  measurements needed by this project.

## Relevance

The demonstration is a useful discovery lead and lowers uncertainty about the
bare possibility of compiling some Erlang/OTP configuration with Emscripten.
It does not answer which upstream components were preserved, stubbed, or
disabled. It therefore cannot define the minimal implementation set, estimate
the maintenance cost, or satisfy any compatibility or security gate.

## Limits

This is an undated demonstration page, not a scientific paper, source release,
or reproducibility package. The archive did not receive build artifacts or a
patch set and did not independently verify its runtime identity. No conclusion
about current OTP, browser interoperability, lifecycle cleanup, performance,
or production suitability should be inferred from it.

## Derived work

- [ERTS architecture and the minimum browser WebAssembly port](../90-archive/erts-architecture-and-minimal-browser-webassembly-port.md)
- [ERTS WebAssembly runtime architecture and milestones](../20-notes/erts-webassembly-runtime-architecture-and-milestones.md)
- [2026-09-14 ERTS architecture deep dive](../50-journal/2026-09-14-erts-architecture-and-minimal-webassembly-port-deep-dive.md)
