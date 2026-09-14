---
title: "Browser executable integrity, content security, and rendering standards"
kind: source
created: "2026-09-14"
authors:
  - "World Wide Web Consortium"
  - "WHATWG"
  - "WebAssembly Community Group"
published: null
citation_key: "browser-integrity-rendering-standards-2026"
container: "SRI, CSP, Trusted Types, WAI-ARIA, HTML, and WebAssembly Web API specifications"
edition: "Standards and drafts accessed 2026-09-14"
isbn: null
doi: null
url: "https://www.w3.org/TR/SRI/"
accessed: "2026-09-14"
tags:
  - accessibility
  - browser-security
  - content-security-policy
  - rendering
  - runtime-loading
  - webassembly
aliases:
  - "Browser bootstrap and renderer security standards"
---

# Browser executable integrity, content security, and rendering standards

## Reference

W3C, WHATWG, and WebAssembly Community Group specifications, accessed
2026-09-14:

- [Subresource Integrity](https://www.w3.org/TR/SRI/);
- [Content Security Policy Level 3](https://www.w3.org/TR/CSP3/);
- WHATWG [script fetching and Worker processing](https://html.spec.whatwg.org/multipage/webappapis.html);
- [WebAssembly Web API Level 2](https://www.w3.org/TR/wasm-web-api-2/);
- [Trusted Types](https://www.w3.org/TR/trusted-types/); and
- [WAI-ARIA 1.2](https://www.w3.org/TR/wai-aria-1.2/).

## Research question or contribution

What can the browser verify before an ERTS generation executes, and how can a
later renderer avoid turning BEAM messages into script or markup authority?

## Method

The specifications were compared at the exact execution boundaries in the
proposed architecture: root page script, Worker script graph, Wasm bytes,
generated loader, and DOM mutation. Normative coverage was distinguished from
project controls that must be implemented by the generation supervisor.

## Findings

### Executable integrity

- SRI lets an HTML `script` or supported `link` declare expected response
  hashes. A mismatch becomes a network error. Cross-origin integrity-protected
  loads require CORS.
- SRI metadata is only as trustworthy as the context that supplies it. If the
  root HTML and its hash are replaced together, content hashes provide
  consistency rather than an independent authenticity root.
- Current integrity policy covers script and style destinations. It is not a
  complete manifest or generation-coherence mechanism for Wasm, release data,
  and all Worker descendants.
- The Worker constructor's standard fetch options carry empty integrity
  metadata, and descendant module-script fetches do not inherit an initial
  resource's integrity metadata. A project must therefore select a trusted
  immutable URL policy or verify bytes and create executable Workers through a
  separately reviewed CSP-compatible mechanism.
- Fetch requests can carry integrity metadata, and WebAssembly can be compiled
  from fetched bytes. Streaming compilation requires the correct
  `application/wasm` MIME type. If authenticity requires a signature or digest
  over the complete representation, instantiation must remain barred until
  that check succeeds.
- CSP's `worker-src` restricts Worker URLs. `wasm-unsafe-eval` can permit Wasm
  compilation without granting JavaScript `eval`; broad `unsafe-eval`, generic
  blob/data execution, and unrestricted origins expand the bootstrap attack
  surface.

### Rendering

- Trusted Types narrows selected DOM injection sinks to typed values and
  central policies. It does not confine network authority, prevent unsafe
  policy implementations, or replace safe DOM construction.
- A renderer can avoid the relevant sink class by using semantic DOM methods,
  text nodes, allowlisted attributes, and fixed event names instead of HTML or
  script strings. Trusted Types then becomes an enforcement and regression
  control rather than the primary sanitizer.
- WAI-ARIA defines roles, states, properties, names, relationships, focus, and
  live-region semantics. Native HTML semantics remain preferable where they
  exist. A renderer protocol that carries only pixels or arbitrary attributes
  cannot preserve this contract.

## Relevance

The root bootstrap and the manifest are distinct trust problems. The POC must
document which bytes are trusted by origin/TLS/CSP, which are authenticated by
an embedded digest or public key, how Worker scripts become executable, and
when Wasm may instantiate. It must test wrong hashes, redirects, cache mixing,
service-worker interference, MIME failure, and a partially created Worker
graph.

The later renderer should accept a small semantic operation algebra—not HTML,
CSS, JavaScript, selectors, or arbitrary property paths. Handles and batches
belong to one runtime generation. The page adapter validates bounds and
allowlists, mutates detached or staged nodes, commits atomically, reports an
acknowledgement, and preserves focus, selection, native element semantics, and
accessible names.

## Limits

These standards do not select the project's trust root, signature format,
deployment server, renderer protocol, or supported accessibility matrix. Blob
Worker and module-graph behavior is sensitive to CSP and browser versions and
must be tested using the production delivery path. Trusted Types does not make
an unsafe renderer policy safe.

## Derived work

- [Component implementation deep dive](../20-notes/erts-webassembly-component-implementation-deep-dive.md)
- [Artifact loader component](../20-notes/components/artifact-loader-and-runtime-generations.md)
- [Renderer and lifecycle component](../20-notes/components/renderer-accessibility-and-page-lifecycle.md)
- [Security and supply-chain component](../20-notes/components/security-observability-and-supply-chain.md)
