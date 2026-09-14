---
title: "Capsicum: practical capabilities for UNIX"
kind: source
created: "2026-09-14"
authors:
  - "Robert N. M. Watson"
  - "Jonathan Anderson"
  - "Ben Laurie"
  - "Kris Kennaway"
published: 2010
citation_key: "watson-et-al-2010-capsicum"
container: "19th USENIX Security Symposium"
edition: null
isbn: null
doi: null
url: "https://www.usenix.org/legacy/events/sec10/tech/full_papers/Watson.pdf"
accessed: "2026-09-14"
tags:
  - capabilities
  - compartmentalization
  - least-authority
  - security
aliases:
  - "Capsicum"
---

# Capsicum: practical capabilities for UNIX

## Reference

Robert N. M. Watson, Jonathan Anderson, Ben Laurie, and Kris Kennaway.
[“Capsicum: Practical Capabilities for UNIX”](https://research.google/pubs/capsicum-practical-capabilities-for-unix/).
Proceedings of the 19th USENIX Security Symposium, 2010, pp. 29–46.
[Open paper](https://www.usenix.org/legacy/events/sec10/tech/full_papers/Watson.pdf).

## Research question or contribution

Can capability primitives compartmentalize existing, large, security-sensitive
applications without replacing their entire programming or operating-system
model?

## Method

Capsicum adds kernel capability mode and rights-limited object handles, then
adapts existing utilities and parts of Chromium. The paper evaluates code
changes and security properties against more ambient sandbox techniques.

## Findings

- Ambient global namespaces make it difficult to know or reduce a component's
  authority. Entering capability mode prevents opening new ambient resources;
  work continues through explicit handles already delegated to the process.
- A handle can be rights-limited so a recipient receives less authority than
  the delegator. The handle identifies both the resource and the allowed
  operations.
- Useful compartmentalization does not require rewriting every internal
  operation. A narrow adaptation layer can preserve a large existing program
  while relocating resource acquisition and delegation to a broker.
- Compatibility wrappers can accidentally reintroduce ambient authority; the
  security property depends on enforcing the restriction below those wrappers.

## Relevance

Capsicum is not a browser or ERTS ABI. Its relevant design lesson is to give an
ERTS generation opaque, operation-scoped handles from an outer broker and no
API that resolves arbitrary URLs, names, files, keys, or DOM objects. Rights
attenuation maps to narrower child handles, fixed origins and methods, bounded
object-store scopes, non-extractable key usages, and renderer subtrees.

Because admitted BEAM code shares one ERTS memory and process namespace, these
handles grant authority to the whole generation, not securely to one Erlang
process. Separate distrust domains need separate Worker-plus-Wasm generations.

## Limits

Capsicum's evidence is for a FreeBSD kernel and native applications. Browser
objects, asynchronous APIs, origin policy, Worker termination, and ERTS port
semantics need their own design and tests. The paper does not prove that an
integer stored in mutable Wasm memory is unforgeable; the broker must validate
the generation, table slot, nonce or epoch, operation, and rights on every use.

## Derived work

- [Capability broker and browser services](../20-notes/components/capability-broker-and-browser-services.md)
- [Security, observability, and supply chain](../20-notes/components/security-observability-and-supply-chain.md)
