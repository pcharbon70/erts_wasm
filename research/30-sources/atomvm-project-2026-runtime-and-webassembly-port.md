---
title: "AtomVM runtime architecture and WebAssembly port"
kind: source
created: "2026-09-14"
authors:
  - "AtomVM contributors"
published: null
citation_key: "atomvm-project-2026-runtime-webassembly-port"
container: "AtomVM documentation and source"
edition: "commit 0220c78ee9e7cf6c763a278b44d81ce309fcf1ab"
isbn: null
doi: null
url: "https://github.com/atomvm/AtomVM"
accessed: "2026-09-14"
tags:
  - atomvm
  - beam
  - browser
  - emscripten
  - runtime
  - webassembly
  - web-workers
aliases:
  - "AtomVM browser port evidence"
---

# AtomVM runtime architecture and WebAssembly port

## Reference

AtomVM contributors. [AtomVM](https://github.com/atomvm/AtomVM),
[runtime internals](https://doc.atomvm.org/latest/atomvm-internals.html),
[build instructions](https://doc.atomvm.org/main/build-instructions.html), and
[known differences from BEAM](https://doc.atomvm.org/latest/known-differences.html).
Source inspected at commit
[`0220c78ee9e7cf6c763a278b44d81ce309fcf1ab`](https://github.com/atomvm/AtomVM/commit/0220c78ee9e7cf6c763a278b44d81ce309fcf1ab),
dated 2026-07-13. Accessed 2026-09-14.

## Research question or contribution

What does an independently implemented BEAM-family runtime have to provide,
and which browser-host adaptations did its Emscripten target require? The
source is used as a comparative architecture probe, not as a substitute for
upstream ERTS and not as proof of Erlang/OTP compatibility.

## Method

The official documentation was read alongside the Emscripten platform source,
build configuration, and browser-test configuration at the pinned commit. The
review focused on component categories, Worker topology, event polling,
clocks, module loading, and lifecycle behavior. Differences documented by the
project were retained because they limit how far the port can be generalized
to official ERTS.

## Findings

- AtomVM is a ground-up virtual machine implementation rather than a port of
  upstream ERTS. Its documentation notes that there is no independent abstract
  BEAM specification and treats the Erlang/OTP implementation as the definitive
  reference.
- Its runtime responsibilities still include BEAM opcode execution, calls and
  exceptions, lightweight processes, mailboxes, memory management, preemptive
  scheduling, NIFs or ports, and platform integration. This independently
  corroborates the component categories found in ERTS literature, without
  establishing equivalent semantics or implementation depth.
- The Emscripten build uses pthread support even when SMP is disabled so the
  runtime can wait efficiently. It selects the `web,worker` environments and
  uses `PROXY_TO_PTHREAD` so the VM scheduler does not run on the browser main
  thread.
- The Emscripten system layer owns a mutex, condition variable, and message
  queue. JavaScript-originated events enter that queue, wake the poller, and
  become runtime messages. Clocks use Emscripten or POSIX-compatible clock
  interfaces, while packages may be preloaded or fetched.
- The web link configuration includes Fetch and WebSocket support, Worker file
  support, an initial linear-memory size, and memory growth. These are explicit
  product choices rather than properties supplied by Core WebAssembly.
- Scheduler threads are detached on this platform and the platform's
  `join_all` operation is a no-op. That is an important limit: the port is an
  existence proof for Worker-based execution and event wakeup, not evidence
  that a strict external supervisor can account for and join every runtime
  thread during teardown.
- The project's documented semantic surface is intentionally smaller than
  Erlang/OTP. Differences include incomplete OTP libraries and behaviours,
  limited integer and bit-syntax cases, no hot code loading, incomplete
  distribution, no dirty schedulers, and statically registered native
  integrations that can block scheduling.
- The repository's web tests exercise a SharedArrayBuffer-capable configuration
  through a Chrome-oriented Cypress setup. That is useful automation evidence,
  but it is not cross-browser qualification of an upstream ERTS port.

## Relevance

AtomVM validates three design directions for this archive's upstream-ERTS
experiment: execute the runtime away from the page UI thread, retain a real
thread substrate even for minimal scheduling, and translate asynchronous host
events into a queue that the runtime poller can wake on. It also shows that a
browser target needs JavaScript bootstrap, Worker, asset-loading, memory, and
test infrastructure in addition to a `.wasm` file.

The comparison also sharpens the boundary. AtomVM can be small partly because
it deliberately implements a different and narrower semantic profile. Its C
platform files are therefore design evidence, not patches to transplant into
ERTS. Upstream ERTS has a broader startup graph, multiple scheduler classes,
its own allocator and signal machinery, and a version-matched OTP boot path.

## Limits

No AtomVM build or browser test was run in this archive. The inspected commit
postdates the existing 2026-09-13 source baseline, and the project's `main`
documentation is living material. Nothing here establishes parity with
Erlang/OTP, validates ERTS's thread topology, or satisfies this project's
teardown, security, compatibility, and supply-chain gates.

## Derived work

- [ERTS WebAssembly component implementation deep dive](../20-notes/erts-webassembly-component-implementation-deep-dive.md)
- [ERTS architecture and the minimum browser WebAssembly port](../90-archive/erts-architecture-and-minimal-browser-webassembly-port.md)
- [ERTS WebAssembly runtime architecture and milestones](../20-notes/erts-webassembly-runtime-architecture-and-milestones.md)
- [Minimum ERTS browser-port map](../10-maps/erts-architecture-and-minimal-browser-port.md)
- [Minimum browser platform-contract inquiry](../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md)
- [2026-09-14 ERTS architecture deep dive](../50-journal/2026-09-14-erts-architecture-and-minimal-webassembly-port-deep-dive.md)
