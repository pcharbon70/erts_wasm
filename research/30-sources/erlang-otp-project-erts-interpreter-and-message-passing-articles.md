---
title: "ERTS interpreter and message-passing engineering articles"
kind: source
created: "2026-09-14"
authors:
  - "John Högberg"
  - "Erlang/OTP Project"
published: null
citation_key: "hogberg-erts-interpreter-message-passing-articles"
container: "Erlang/OTP blog"
edition: null
isbn: null
doi: null
url: "https://www.erlang.org/blog/a-brief-beam-primer/"
accessed: "2026-09-14"
tags:
  - beam
  - erlang
  - erts
  - interpreter
  - message-passing
  - runtime
aliases:
  - "Official BEAM interpreter articles"
---

# ERTS interpreter and message-passing engineering articles

## Reference

John Högberg and the Erlang/OTP Project:

- [“A brief introduction to BEAM”](https://www.erlang.org/blog/a-brief-beam-primer/)
- [“A closer look at the interpreter”](https://www.erlang.org/blog/a-closer-look-at-the-interpreter/)
- [“A few notes on message passing”](https://www.erlang.org/blog/message-passing/)

Official Erlang/OTP engineering articles, accessed 2026-09-14.

## Research question or contribution

How does upstream ERTS turn BEAM files into executable interpreter operations,
and how do user messages relate to the broader process-signal machinery?

## Method

The articles were read as explanatory accounts by an upstream ERTS developer
and checked against the pinned OTP 29.0.6 source where the deep dive depends on
current implementation detail. They explain design; they are not a normative
compatibility specification.

## Findings

- BEAM files contain generic instructions that the loader validates,
  transforms, and specializes into emulator-specific instructions. Loading is
  therefore part of the execution architecture rather than passive byte
  copying.
- The portable interpreter and architecture-specific native-code paths share
  generated instruction definitions but have different execution mechanisms.
  Retaining the interpreter avoids creating a new Wasm code generator, while
  still requiring validation of its dispatch strategy under the target C
  compiler.
- Erlang processes use a general signal mechanism for messages and other
  process-to-process operations. Message delivery, links, monitors, exits, and
  process state interact with queues and scheduling; a browser port cannot
  preserve these semantics by replacing only the visible mailbox API.
- Queue placement and handling include important concurrency and ordering
  behavior. A JavaScript host bridge should inject bounded completions through
  an audited ERTS mechanism rather than mutate process state from arbitrary
  callbacks.

## Relevance

These articles support preserving the upstream loader, generated interpreter,
process signal queues, and scheduler integration. They also support one of the
deep dive's central boundaries: browser events should become ordinary
runtime-visible messages only after capability and length validation, while
the JavaScript host remains outside ERTS process internals.

## Limits

The articles describe selected internals and may reflect the implementation at
their publication dates. They do not enumerate the full startup graph, define
browser behavior, or prove that ERTS builds with Emscripten. The pinned source
and differential tests remain authoritative for the chosen release.

## Derived work

- [ERTS architecture and the minimum browser WebAssembly port](../90-archive/erts-architecture-and-minimal-browser-webassembly-port.md)
- [ERTS WebAssembly runtime architecture and milestones](../20-notes/erts-webassembly-runtime-architecture-and-milestones.md)
- [Minimum ERTS browser-port map](../10-maps/erts-architecture-and-minimal-browser-port.md)
