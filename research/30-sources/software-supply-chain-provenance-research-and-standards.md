---
title: "Software supply-chain provenance research and standards"
kind: source
created: "2026-09-14"
authors:
  - "Santiago Torres-Arias"
  - "Hammad Afzali"
  - "Trishank Karthik Kuppusamy"
  - "Reza Curtmola"
  - "Justin Cappos"
  - "SLSA contributors"
  - "SPDX contributors"
published: null
citation_key: "supply-chain-provenance-2019-2026"
container: "USENIX Security 2019, SLSA 1.2, and SPDX specifications"
edition: "SLSA 1.2; SPDX 3.0"
isbn: null
doi: null
url: "https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias"
accessed: "2026-09-14"
tags:
  - provenance
  - reproducible-builds
  - sbom
  - security
  - supply-chain
aliases:
  - "in-toto, SLSA, and SPDX"
---

# Software supply-chain provenance research and standards

## Reference

- Santiago Torres-Arias et al., [“in-toto: Providing farm-to-table guarantees
  for bits and bytes”](https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias),
  28th USENIX Security Symposium, 2019, pp. 1393–1410,
  ISBN 978-1-939133-06-9.
- SLSA contributors, [SLSA specification 1.2](https://slsa.dev/spec/v1.2/),
  including [build provenance](https://slsa.dev/spec/v1.2/build-provenance).
- SPDX contributors, [SPDX specifications](https://spdx.dev/use/specifications/),
  current version 3.0; SPDX 2.2.1 was published as ISO/IEC 5962:2021.

## Research question or contribution

How can consumers determine which source, dependencies, tools, build steps, and
actors produced a release artifact, rather than trusting only the final file's
hash?

## Method

The in-toto paper evaluates a signed supply-chain-layout model against 30
historical compromises. SLSA organizes incremental source and build controls
and defines provenance predicates. SPDX defines machine-readable software-bill-
of-materials and provenance data. This note extracts the parts applicable to a
multi-artifact ERTS browser generation.

## Findings

- A final artifact digest detects substitution only when the expected digest
  itself has a trusted origin. It does not say which sources, patches,
  dependencies, or build environment produced those bytes.
- in-toto links authenticated step metadata into a layout so an expected chain
  can be checked, addressing compromise between source, build, test, and
  packaging stages.
- SLSA separates provenance availability from stronger guarantees about who
  produced it and whether the builder is isolated from influence. Its levels
  are incremental rather than a binary certification.
- SPDX can inventory source packages, generated assets, toolchain components,
  licenses, relationships, and checksums. An SBOM is evidence about contents;
  it is not proof of build integrity or vulnerability absence.

## Relevance

An ERTS browser generation is unusually easy to skew: upstream OTP, bootstrap
OTP, emsdk, C dependencies, patches, generated interpreter source, Wasm,
JavaScript glue, pthread Worker scripts, release BEAM files, manifest, and test
capsules must agree. The build should emit one generation manifest plus
provenance and an SPDX SBOM that names every input and output digest.

The POC can begin with reproducible commands, a clean builder identity,
unsigned provenance retained beside the artifacts, and independent hash
comparison. Production hardening should use signed provenance from a hosted,
isolated builder, policy verification before release, key rotation, revocation,
anti-downgrade rules, and rehearsed upstream/toolchain security updates.

## Limits

These sources do not make a build reproducible, select a signing system, or
secure browser delivery. SLSA conformance is scoped to declared tracks and
levels. An authenticated malicious build and an accurately documented
vulnerable dependency remain possible. Runtime qualification and deployment
integrity are separate gates.

## Derived work

- [Artifact loader and runtime generations](../20-notes/components/artifact-loader-and-runtime-generations.md)
- [Security, observability, and supply chain](../20-notes/components/security-observability-and-supply-chain.md)
