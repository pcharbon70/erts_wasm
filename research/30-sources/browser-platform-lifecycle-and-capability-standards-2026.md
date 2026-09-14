---
title: "Browser platform lifecycle, time, and capability standards"
kind: source
created: "2026-09-14"
authors:
  - "WHATWG"
  - "World Wide Web Consortium"
  - "Web Platform Incubator Community Group"
published: null
citation_key: "browser-platform-standards-2026"
container: "HTML, Fetch, WebSockets, Storage, IndexedDB, High Resolution Time, and Page Lifecycle specifications"
edition: "Living standards and drafts accessed 2026-09-14"
isbn: null
doi: null
url: "https://html.spec.whatwg.org/multipage/workers.html"
accessed: "2026-09-14"
tags:
  - browser
  - capabilities
  - lifecycle
  - networking
  - storage
  - time
  - web-workers
aliases:
  - "Browser host API standards"
---

# Browser platform lifecycle, time, and capability standards

## Reference

Primary browser-platform specifications and implementation guidance, accessed
2026-09-14:

- WHATWG [Web workers](https://html.spec.whatwg.org/multipage/workers.html),
  [document lifecycle](https://html.spec.whatwg.org/multipage/document-lifecycle.html),
  [Fetch](https://fetch.spec.whatwg.org/),
  [WebSockets](https://websockets.spec.whatwg.org/), and
  [Storage](https://storage.spec.whatwg.org/) living standards;
- W3C [High Resolution Time Level 3](https://www.w3.org/TR/hr-time-3/),
  [Indexed Database API 3.0](https://www.w3.org/TR/IndexedDB/), and
  [Web Cryptography API Level 2](https://w3c.github.io/webcrypto/); and
- WICG [Page Lifecycle](https://wicg.github.io/page-lifecycle/) plus the
  Chromium team's [Page Lifecycle API guidance](https://developer.chrome.com/docs/web-platform/page-lifecycle-api).

## Research question or contribution

Which browser primitives can implement time, wakeup, networking, persistence,
cryptography, and forced teardown for an ERTS generation, and where do their
semantics differ from an operating system?

## Method

The specifications were read as host contracts, with special attention to
asynchrony, cancellation, buffering, quotas, lifecycle, and clock semantics.
They were not treated as evidence that ERTS already maps to these APIs. The
Page Lifecycle guidance is implementation-specific and is used only to expose
conditions that the Chrome/Firefox qualification matrix must test.

## Findings

### Workers and lifecycle

- A dedicated Worker's creator can invoke the normative terminate algorithm.
  Termination sets the closing flag, discards queued tasks, aborts the script
  currently running, and empties the implicit port queue. It does not run
  cooperative cleanup inside the Worker.
- Once a Worker is closing, new timer and background-operation tasks are
  dropped. A completion that was valid when issued can therefore disappear,
  which requires host requests to have cancellation and generation identity
  rather than an assumed final callback.
- A document can become hidden, frozen, terminated, or discarded. Discard can
  happen without a final application callback. Frozen task queues do not make
  progress until resume, and browser guidance recommends closing IndexedDB,
  WebSocket, and similar connections before freeze.
- Back/forward-cache restoration resumes a prior JavaScript heap. It is not a
  new page load, so stale runtime handles remain reachable unless the outer
  supervisor explicitly invalidates or reconciles them.

### Time

- `performance.now()` is exposed in Workers and is based on a monotonic clock;
  `Date.now()` is wall-clock time and can move when the system clock changes.
- Each global context has a time origin. Cross-Worker comparisons therefore
  need a documented common provider or normalization using the context's
  `performance.timeOrigin` plus its monotonic `performance.now()` value; raw
  `performance.now()` readings are not a shared zero-based clock.
- Timer precision can be coarsened or jittered for security. Cross-origin
  isolation permits a finer target resolution but does not guarantee a
  particular implementation resolution.
- Browser task throttling or freezing changes when callbacks run, even if the
  monotonic clock continues to advance. Therefore a late callback is normal
  browser behavior and must not be translated into an early ERTS timer.
- The standards do not by themselves establish identical behavior across
  machine sleep, browser suspension, mobile backgrounding, and bfcache. Those
  cases need a declared runtime policy and conformance tests.

### Network, storage, and crypto capabilities

- Fetch exposes method, headers, credentials, redirects, cache mode, response
  streaming, integrity metadata, and an `AbortSignal`. A generic Fetch import
  would therefore carry far more authority than most application operations
  require.
- The classic WebSocket API reports queued outbound bytes through
  `bufferedAmount`, but does not make admission wait for available capacity.
  If the user agent cannot buffer a send it closes the connection. A runtime
  bridge must add an explicit high-water mark and bounded receive queue.
- IndexedDB transactions have fixed store scope and mode, commit or abort
  atomically, and are intended to be short-lived. Upgrade transactions are
  exclusive. Quota exhaustion and abnormal connection closure are ordinary
  failure outcomes.
- Browser storage is origin-scoped and best-effort by default. Persistence can
  be requested but remains user-agent and user controlled; the runtime cannot
  promise filesystem-style durability or immunity from user deletion.
- WebCrypto operations are asynchronous. `CryptoKey` uses an opaque internal
  handle and declares permitted usages and extractability, providing a useful
  model for purpose-bound runtime capability handles without exposing secret
  key bytes to Wasm.

## Relevance

The browser platform should be represented as a typed broker rather than a
POSIX facade. The proof of concept needs only clocks, bounded wakeups, entropy,
release bytes, diagnostics, and lifecycle control. Fetch, WebSocket, IndexedDB,
and general cryptography should arrive later as independent removable
capabilities with operation-specific handles, quotas, cancellation, and
failure mappings.

The conservative first lifecycle policy is generation replacement on
navigation, discard detection, and unproven bfcache restoration. A mature
profile can preserve a live generation across freeze only after it proves
clock, timer, open-connection, queued-completion, and Worker ownership
semantics in every supported browser.

## Limits

Living standards change and leave resource limits, throttling policy, process
placement, and some clock behavior implementation-defined. The presence of an
API in a Worker does not establish acceptable throughput or cleanup. No
Chrome, Firefox, sleep, freeze, bfcache, quota, or network experiment was run
for this note.

## Derived work

- [Component implementation deep dive](../20-notes/erts-webassembly-component-implementation-deep-dive.md)
- [Browser platform and progress component](../20-notes/components/browser-platform-time-poll-and-progress.md)
- [Capability broker component](../20-notes/components/capability-broker-and-browser-services.md)
- [Renderer and lifecycle component](../20-notes/components/renderer-accessibility-and-page-lifecycle.md)
