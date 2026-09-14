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

- [ERTS WebAssembly runtime architecture and
  milestones](../20-notes/erts-webassembly-runtime-architecture-and-milestones.md)
  is the canonical synthesis of ERTS components, the browser architecture,
  runtime loading, the minimal proof, and later compatibility work.
- [Component implementation deep
  dive](../20-notes/erts-webassembly-component-implementation-deep-dive.md)
  translates that architecture into POC choices, later compatibility
  directions, risks, and falsifiable gates for all eleven components.
- [Component implementation map](erts-webassembly-component-implementation.md)
  connects each component deep dive to its primary, standards, and scientific
  evidence.
- [Minimum ERTS browser-port map](erts-architecture-and-minimal-browser-port.md)
  routes through the component evidence, comparative sources, and new
  repository-neutral inquiry.
- [ERTS WebAssembly runtime-stack map](erts-webassembly-runtime-stack.md)
  routes through the evidence by subsystem.
- [Feasibility inquiry](../40-inquiries/can-blazex-build-and-own-an-erts-webassembly-runtime-stack.md)
  defines falsifiable gates and blockers inherited from the original BlazeX
  framing; repository-neutral refinement is future work.
- [Research journal](../50-journal/2026-09-13-first-party-erts-webassembly-runtime-deep-dive.md)
  records source selection, local inspection, and evidence limits.
- [2026-09-14 component deep-dive
  journal](../50-journal/2026-09-14-erts-architecture-and-minimal-webassembly-port-deep-dive.md)
  records the pinned source audit and new negative findings.
- [2026-09-14 component implementation research
  journal](../50-journal/2026-09-14-erts-webassembly-component-implementation-research.md)
  records the per-component research method, decisions, and evidence limits.

## Trails

- [Sources](../30-sources/README.md) contains the complete ERTS, OTP,
  WebAssembly, browser, performance, and security evidence set.
- [Planning](../60-planning/README.md) contains the authorized but entirely
  unchecked P0–P6 proof-of-concept and C1–C10 compatibility gates.
- [Templates](../templates/README.md) and [tools](../70-tools/README.md) govern
  future corpus additions.

## Open questions

- What exact ERTS and Worker graph can satisfy the [minimum browser platform
  contract inquiry](../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md)?
- Which integration boundaries fail first under the [component-seam
  inquiry](../40-inquiries/which-component-seams-block-the-first-erts-wasm-proof.md)?
- Can the proposed runtime satisfy the [feasibility inquiry](../40-inquiries/can-blazex-build-and-own-an-erts-webassembly-runtime-stack.md)
  without broad POSIX emulation or an unmaintainable fork?
- Which findings should become repository-neutral ADRs before implementation?
