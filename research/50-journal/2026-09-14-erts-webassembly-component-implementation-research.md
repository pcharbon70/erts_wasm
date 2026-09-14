---
title: "2026-09-14 ERTS WebAssembly component implementation research"
kind: journal
created: "2026-09-14"
tags:
  - architecture
  - browser
  - components
  - deep-research
  - erlang
  - erts
  - otp
  - webassembly
aliases:
  - "ERTS-Wasm per-component deep-dive journal"
---

# 2026-09-14 ERTS WebAssembly component implementation research

## Objective

Research every component named or implied by the canonical architecture and
translate primary-source and scientific evidence into a POC implementation
choice, later compatibility direction, falsifiable gates, and explicit risks.

## Environment and scope

- Corpus: `/home/ducky/code/erts_wasm/research`
- Research date: 2026-09-14, America/Toronto
- Pinned source baseline: OTP 29.0.6 / ERTS 17.0.6, commit
  `e07fd07837e5aa845657f5fa340637121e451d47`
- Target: browser Core Wasm through a future pinned Emscripten SDK
- Browsers: Chrome and Firefox versions to be pinned during P0
- Excluded implementation stack: not searched, inspected, cited, or used

This session performed research and corpus editing only. It did not compile,
link, instantiate, boot, benchmark, fuzz, or run ERTS in a browser.

## Research method

The canonical architecture defined the component boundary. Evidence was sought
in this order:

1. exact tagged Erlang/OTP source and current official documentation;
2. official Emscripten and WebAssembly specifications;
3. WHATWG/W3C browser API, lifecycle, security, storage, crypto, and
   accessibility specifications;
4. original peer-reviewed work on Erlang memory/scalability, concurrency
   testing, WebAssembly concurrency/security/performance, capabilities, and
   supply-chain integrity; and
5. maintainer engineering articles for interpreter, loader, and message-passing
   design intent.

Search snippets were used only to locate the primary work. Source claims were
kept in `30-sources`; implementation choices were written in the archive's own
voice and labeled as proposals. No numerical result from an older runtime or
engine was treated as an ERTS-Wasm forecast.

## Material findings

- The architecture decomposes cleanly into eleven components, but loader,
  Worker, platform, ERTS, and lifecycle ownership remain one critical path.
- `+S 1:1` leaves at least seven candidate ERTS/POSIX roles, but roles, actual
  pthread Worker hosts/pool slots, and page/root supervisory agents are
  different censuses; target instrumentation must establish all three.
- The first semantic proof should use fixed shared memory and malloc-backed
  carriers, deferring growth and memory64.
- The generated interpreter has an existing switch-dispatch path that is the
  lowest-risk first build; computed-goto lowering remains an A/B experiment.
- A boot-only test does not exercise ordinary loader publication. The refined
  POC admits one manifest-listed module after boot but before `ready`, then
  permanently closes admission.
- A verified MEMFS release tree with write/create/mutation operations denied
  below callers is the shortest boot path; a custom manifest primitive loader
  is a later surface reduction, not a prerequisite.
- SRI does not authenticate the whole Worker/Wasm/data graph, and Worker script
  integrity needs an explicit trusted-origin or verified-byte execution design.
- Emscripten's normal run lifecycle can invoke `main` before an outer loader's
  assumed “start” point; the POC must pin and test automatic-main suppression,
  mount the verified release, and only then invoke ERTS exactly once.
- Page freeze/discard and bfcache can suspend or revive old state without a
  reliable final callback. Generation replacement is the conservative POC
  policy until live resume is qualified.
- Browser capabilities fit opaque, operation-scoped broker handles. Fetch,
  WebSocket, IndexedDB, and WebCrypto each need independent quota,
  cancellation, lifecycle, and error contracts.
- AtomVM corroborates the off-UI-thread, pthread, and queue-and-wakeup browser
  shape, but its distinct runtime, reduced semantics, and teardown behavior
  make it comparison evidence only; no code or compatibility claim transfers.
- Wasm containment does not make linked ERTS C code memory-safe or create hard
  isolation between BEAM programs in one VM.
- Reproducibility, SBOM, and provenance need to bind bootstrap OTP, emsdk,
  generated files, JavaScript/Worker assets, release BEAM files, manifest, and
  tests—not only `erts.wasm`.

## Outputs

- [Component implementation synthesis](../20-notes/erts-webassembly-component-implementation-deep-dive.md)
- [Component map](../10-maps/erts-webassembly-component-implementation.md)
- [Architecture component notes](../20-notes/components/README.md)
- [Component-seam inquiry](../40-inquiries/which-component-seams-block-the-first-erts-wasm-proof.md)
- New source notes for browser platform and integrity standards, capability
  security, supply-chain provenance, Elixir, Concuerror, WebAssembly relaxed
  memory, and OTP time/testing/observability in [Sources](../30-sources/README.md)

## Evidence limits

- Exact Worker/pthread count, stack footprint, pool size, and topology remain
  unmeasured.
- The first configure, interpreter compile, link, and boot failures remain
  unknown.
- The Kernel/STDLIB and application closure is proposed, not generated.
- Fixed memory, MEMFS, broker-ring, renderer, and hard-stop designs have no
  browser evidence yet.
- Browser implementation behavior and standards will move; all implementation
  work must pin versions and dates.

## Follow-ups

- Execute P0 and P1 without marking any implementation gate complete in
  advance.
- Update source notes with exact emsdk and browser revisions when selected.
- Turn accepted component choices into ADRs only after the corresponding probe
  closes the open inquiry.
- Keep the canonical architecture, component synthesis, map, inquiry, detailed
  plan, source derived-work links, and directory inventories synchronized.
