---
title: "ERTS build and BEAM interpreter"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - beam
  - build-systems
  - emscripten
  - erlang
  - erts
  - interpreter
  - webassembly
aliases:
  - "ERTS-Wasm cross-build and interpreter"
---

# ERTS build and BEAM interpreter

## Decision

Cross-build the complete upstream OTP 29.0.6 generated BEAM interpreter for
`wasm32-unknown-emscripten`; do not define a smaller bytecode VM. Run all
generators on a same-release native build host, disable BeamAsm/JIT, and test
the existing numeric-opcode switch path before optimizing dispatch.

## What must remain upstream

`beam_makeops` generates interpreter and loader tables from the instruction
descriptions. The interpreter's `process_main()` restores scheduler-local
registers, executes BEAM instructions until reductions expire, saves state, and
returns to the normal ERTS scheduler. The loader repeatedly transforms generic
instructions into typed, emulator-specific forms and stores the selected
dispatch representation in code.[^erts-source][^interpreter]

These mechanisms cover the complete instruction set, exceptions, calls and
tail calls, matching, binaries, maps, funs, BIF entry, reductions, and loader
specialization. Removing unfamiliar instructions would create a new BEAM
dialect and make matching OTP modules accidental.

BeamAsm is a separate x86-64/AArch64 native JIT with executable-code and
architecture-specific assumptions. Disabling it selects a maintained upstream
execution mode; compiling it to Wasm is not required for ERTS validity.

## POC implementation

Create separate build and target stages:

1. check out the exact OTP tag and commit and verify the source archive;
2. build the release's native bootstrap Erlang and every required generator;
3. pin emsdk/Clang/LLVM, C library, linker, build image, Python/Perl/autotools,
   and generated-source outputs;
4. add one named `wasm32-unknown-emscripten` platform configuration behind
   existing `sys` and build seams, with explicit configure-cache answers
   rather than allowing run probes to guess;
5. compile and link every target object with consistent `-pthread`, shared
   memory, exception/longjmp, function-table, stack, and memory settings; and
6. inspect imports, exports, custom/name/debug sections, native archive closure,
   JavaScript glue, Worker program, and dead-code report before packaging.

Link the first loader-controlled candidate with automatic `main()` invocation
suppressed—initially test `-sINVOKE_RUN=0` in modularized output, with only the
needed explicit entry mechanism exported. Compare that with the documented
`noInitialRun`/factory path under both Worker topologies. The pinned build must
prove that Wasm/runtime initialization cannot enter `erl_init` before the
verified release tree is mounted, and that exactly one supervisor-owned start
call can cross that boundary.[^emscripten]

Begin with the existing `NO_JUMP_TABLE` numeric-opcode path. C labels-as-values
normally implement direct threading, but LLVM may lower `indirectbr` into a
switch for Wasm. That compiler behavior must not be assumed stable or cheap for
the very large generated dispatch function. Build a second computed-goto
variant from the same source and compare correctness, Wasm size, browser
compile/tier-up time, and instruction throughput before choosing a release
profile.

Retain the full interpreter and loader transformation tables in both variants.
Use a fixed shared-memory ceiling initially. Exclude BeamAsm, dynamic native
loading, distribution, epmd, wx, observer GUI, shell/terminal integration, and
OTP applications outside the boot closure. Exclusion happens in the release
profile and platform boundary, not by weakening term, process, scheduler, GC,
or loader semantics.

Every configure answer needs one of three proven states: native semantics
exist, a browser adapter implements them, or the caller is unreachable and a
negative test proves deterministic failure. Pay particular attention to
`mmap`, atomics, TLS, pthread attributes, signals, priorities, clocks, poll,
dynamic loading, executable paths, environment, `setjmp`/`longjmp`, computed
goto, and 32-bit conversions.

## In-depth implementation

Once semantics pass, profile browser compilation and interpreter execution by
opcode family and workload. Keep switch and compiler-lowered computed-goto
builds reproducible. A Wasm-specific dispatch patch is acceptable only if it is
small, localized, upstream-reviewable, measurably useful, and preserves the
same generated instruction/loader definitions.

Maintain a patch ledger by upstream subsystem and rebase it on every OTP and
emsdk update. Generated files must be reproducible from recorded tools. Two
successive update rehearsals, including a security fix, are required before a
maintained release profile claim.

WebAssembly tail calls, exceptions, function references, and memory64 may
improve future compiler output, but the POC relies only on the feature set
proven in the selected browsers and emsdk. They do not justify replacing the
upstream interpreter with a new Wasm code generator.

## Evidence gates

- A clean, offline-replayable build produces identical or explained artifact
  digests from the pinned inputs.
- The complete generated instruction set compiles and links without hand-
  deleted opcode families; unexpected imports and native artifacts fail CI.
- Native and Wasm capsules agree for instruction decoding, calls/tail calls,
  exceptions, arithmetic, maps, binaries, matching, receive, funs, and
  reductions-based preemption.
- Switch and computed-goto builds produce the same observations; browser build,
  fetch, compile, instantiate, tiering, and steady-state costs are reported
  separately.[^performance]
- Sanitizer/debug builds preserve symbolication from browser failure back to
  the pinned C/generated source.

## Principal risks

The generated interpreter may create a browser compile/tiering or code-size
cliff even when it is semantically correct. Configure can silently select Unix
paths whose functions exist in libc but have weaker browser semantics. The
same-release native-bootstrap requirement means build provenance includes a
host ERTS, not only emcc. `wasm32` conversions and practical shared-memory
limits can fail far below the nominal address-space maximum.

## Sources

[^erts-source]: Erlang/OTP Project, [ERTS build, runtime, and source architecture](../../30-sources/erlang-otp-project-2026-erts-build-runtime-and-source.md).
[^interpreter]: Erlang/OTP maintainers, [interpreter, loader, and message-passing articles](../../30-sources/erlang-otp-project-erts-interpreter-and-message-passing-articles.md).
[^performance]: Abhinav Jangda et al., [Not So Fast](../../30-sources/jangda-et-al-2019-webassembly-performance.md).
[^emscripten]: Emscripten contributors, [browser porting runtime and controlled-start APIs](../../30-sources/emscripten-project-2026-browser-porting-runtime.md).
