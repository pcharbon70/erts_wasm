---
title: "ERTS WebAssembly research home"
kind: map
created: "2026-09-14"
tags:
  - archive-navigation
  - erlang
  - erts
  - otp
  - webassembly
aliases:
  - "Research home"
---

# ERTS WebAssembly research home

## Scope

This is the entry point for the standalone investigation into a first-party,
security-first port of upstream ERTS and matching OTP modules to WebAssembly.

## Start here

- [First-party ERTS WebAssembly runtime stack](../20-notes/first-party-erlang-otp-erts-webassembly-runtime-stack.md)
  is the complete synthesis and staged recommendation.
- [ERTS WebAssembly runtime-stack map](erts-webassembly-runtime-stack.md)
  routes through the evidence by subsystem.
- [Feasibility inquiry](../40-inquiries/can-blazex-build-and-own-an-erts-webassembly-runtime-stack.md)
  defines falsifiable gates and blockers inherited from the original BlazeX
  framing; repository-neutral refinement is future work.
- [Research journal](../50-journal/2026-09-13-first-party-erts-webassembly-runtime-deep-dive.md)
  records source selection, local inspection, and evidence limits.

## Trails

- [Sources](../30-sources/README.md) contains the complete ERTS, OTP,
  WebAssembly, browser, performance, and security evidence set.
- [Planning](../60-planning/README.md) is intentionally empty until a phased
  implementation program is explicitly authorized.
- [Templates](../templates/README.md) and [tools](../70-tools/README.md) govern
  future corpus additions.

## Open questions

- Can the proposed runtime satisfy the [feasibility inquiry](../40-inquiries/can-blazex-build-and-own-an-erts-webassembly-runtime-stack.md)
  without broad POSIX emulation or an unmaintainable fork?
- Which findings should become repository-neutral ADRs before implementation?
