---
title: "2026-09-14 ERTS runtime architecture consolidation"
kind: journal
created: "2026-09-14"
tags:
  - architecture
  - consolidation
  - erts
  - milestones
  - proof-of-concept
  - runtime-loading
  - webassembly
aliases: []
---

# 2026-09-14 ERTS runtime architecture consolidation

## Observations

The two developing architecture notes overlapped substantially but emphasized
different layers. The component note had the stronger pinned-source model of
ERTS internals and minimum platform seams. The stack note had the fuller Worker,
security, lifecycle, release, compatibility, and maintenance design.

They are now superseded by one [canonical runtime architecture](../20-notes/erts-webassembly-runtime-architecture-and-milestones.md).
The original [component note](../90-archive/erts-architecture-and-minimal-browser-webassembly-port.md)
and [runtime-stack note](../90-archive/first-party-erlang-otp-erts-webassembly-runtime-stack.md)
remain intact in the archive with explicit successor notices.

The canonical note deliberately does not claim that a working runtime exists.
It defines the minimum evidence required before the pinned interpreter build
may be called a meaningful ERTS WebAssembly proof of concept.

## Environment

- Corpus root: `/home/ducky/code/erts_wasm/research`
- Pinned research baseline: Erlang/OTP 29.0.6, ERTS 17.0.6, commit
  `e07fd07837e5aa845657f5fa340637121e451d47`
- Date: 2026-09-14
- No ERTS compile, link, browser boot, semantic test, or lifecycle experiment
  was performed during this documentation consolidation.

## Evidence

The [planning roadmap](../60-planning/erts-webassembly-runtime-milestones.md)
and its numbered planning streams separate:

1. P0–P6, which must all pass before claiming a minimal proof of concept; and
2. C1–C10, which expand an accepted proof into an in-depth, maintained
   compatibility profile.

Runtime loading is an obligation at every gate. The plan distinguishes browser
artifact loading, ERTS/OTP release boot, and post-boot BEAM admission and code
lifecycle. It requires generation-scoped cancellation, failure cleanup,
integrity and version binding, immutable proof-of-concept code, loader-negative
tests, and complete teardown.

After the complete corpus update:

- `python3 research/70-tools/validate_archive.py` passed for 41 documents, 13
  directories, 280 local links, and 15 source notes;
- `python3 -m unittest discover -s research/70-tools -p
  'test_validate_archive.py'` passed all 11 tests; and
- `python3 research/70-tools/check_all.py` passed the combined checks.

## Threads

- The proof-of-concept claim remains narrower than product feasibility: it
  excludes broad OTP/Elixir support, browser capabilities, hot code loading,
  and long-term upgrade viability.
- Whole-generation replacement remains the default update model. In-place hot
  loading is an optional later branch with independent safety gates.
- Numeric product budgets and browser support claims still require measured,
  approved evidence.

## Follow-ups

- Execute P0 before beginning a cross-build.
- Keep every milestone checkbox open until its named artifact or test exists.
- Record failures and stop conditions as carefully as successful results.
