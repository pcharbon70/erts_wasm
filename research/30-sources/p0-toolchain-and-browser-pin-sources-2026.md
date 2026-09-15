---
title: "P0 toolchain and browser pin sources"
kind: source
created: "2026-09-15"
authors:
  - "Emscripten contributors"
  - "Google Chrome for Testing team"
  - "Mozilla"
published: null
citation_key: "p0-toolchain-browser-pins-2026"
container: "Official release metadata and archives"
edition: "Records accessed 2026-09-15"
isbn: null
doi: null
url: "https://raw.githubusercontent.com/emscripten-core/emsdk/main/emscripten-releases-tags.json"
accessed: "2026-09-15"
tags:
  - browsers
  - emscripten
  - reproducibility
  - toolchain
aliases: []
---

# P0 toolchain and browser pin sources

## Reference

- Emscripten's official [release alias metadata](https://raw.githubusercontent.com/emscripten-core/emsdk/main/emscripten-releases-tags.json),
  the [emsdk repository](https://github.com/emscripten-core/emsdk), and the
  [emscripten-releases repository](https://chromium.googlesource.com/emscripten-releases),
  accessed 2026-09-15.
- Google's official [Chrome for Testing last-known-good metadata](https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json),
  accessed 2026-09-15.
- Mozilla's official [Firefox 155 archive](https://archive.mozilla.org/pub/firefox/releases/155.0/)
  and [Firefox 155 release notes](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/155),
  accessed 2026-09-15.

## Research question or contribution

Which exact toolchain and browser identities can P0 freeze without relying on
floating channel names or locally installed substitutions?

## Method

The emsdk selection was resolved through official release metadata and the
selected emscripten-releases `DEPS` file. Chrome was resolved through the
stable Chrome-for-Testing record. Firefox was resolved through the release
archive and its `SHA256SUMS` file. Locally installed tools were compared only
to detect mismatches; they were not promoted into qualification inputs.

## Findings

On 2026-09-15, the selected Emscripten release was 6.0.9, mapped to release
bundle `f04ea239d533260dd1db760dd2d668d5f9a88d6b`. Its dependency record pins
Emscripten, LLVM, and Binaryen separately. Chrome for Testing's stable record
selected 153.0.8010.36 revision 1681091. Mozilla's archive published Firefox
155.0 and an SHA-256 digest for the Linux x86_64 US-English archive.

## Relevance

These records provide the acquisition side of `p0-baseline`. They prevent a
later cross-compile or browser result from silently choosing a newer compiler,
optimizer, generated runtime, or browser.

## Limits

The upstream Chrome metadata does not publish an archive digest. The selected
archive must therefore be materialized and hashed before a clean environment
is reproducible. The toolchain components and browser binaries have not been
installed or executed in this phase. Release metadata can change; this note
records the observed selection and the baseline JSON freezes exact values.

## Derived work

- [P0 Phase 1 baseline artifact index](../assets/p0-governed-baseline/phase-01/README.md)
- [P0 Phase 1 plan](../60-planning/01-proof-of-concept/p0-governed-baseline-and-proof-contract/phase-01-baseline-authority-and-runtime-inventory.md)
