---
title: "{YYYY-MM-DD} — {milestone} phase {NN} execution record"
kind: journal
created: "{YYYY-MM-DD}"
tags:
  - implementation-planning
aliases: []
---

# {YYYY-MM-DD} — {milestone} phase {NN} execution record

{Describe what was attempted and the bounded conclusion supported by this run.
Copy this template into `research/50-journal/` only when recording execution.}

## Plan and acceptance baseline

{Link the milestone and phase at exact revisions, stable task IDs, artifacts,
requirements, and acceptance cases. Record predeclared limits.}

## Environment and provenance

{Record the full tested source commit and dirty state; native bootstrap; C
compiler, emsdk/Clang/LLVM/Binaryen and flags; TypeScript/JavaScript toolchain
when involved; OTP/ERTS and browser versions; configuration, seeds, memory and
Worker limits; and whether evidence is native, browser, or synthetic. Redact
secrets and machine identifiers.}

## Execution and results

| Task / case IDs | Fixture and exact argv | Expected result | Actual observation | Result | Raw evidence / artifact identity |
| --- | --- | --- | --- | --- | --- |
| {stable task and case IDs} | {tokenized reproducible invocation} | {predeclared criterion} | {observation or why not run} | {pass / fail / blocked / not run} | {relative link, digest, or exact artifact reference} |

{Include assembled-phase tests, native/Wasm differentials, import/export and
generated-source checks, earlier regressions, negative cases, cleanup, and all
required blocked or unrun cases. Commands without observations are not
evidence.}

## Machine-readable evidence

{For any task whose checkbox may close, link a schema-valid companion named
`<descriptive-name>.planning-evidence.json` beneath `research/assets/`, outside
`planning-conformance/`. Select the honest evidence kind (`contract_research`,
`native_c`, `emscripten_wasm`, or `browser_runtime`), bind it to authoritative
task and gate IDs plus a digest-verified acceptance contract, and inventory it
in its directory README. Synthetic records and unreviewed, failed, blocked, or
not-run records cannot close work. Recorded argv is inert corpus data.}

## Review and handoff

{Record reviewer or review-pending state, proceed/revise/blocked decision,
unresolved failures, corrective work, next entry gate, and changes that reopen
acceptance. Keep the plan, tested, evidence-record, and later merge revisions
distinct.}

## Follow-ups

{Link unresolved decisions, corrective work, and prospective experiments.
Preserve failures when later evidence supersedes their outcome.}
