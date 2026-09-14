---
title: "2026-09-14 ERTS architecture and minimum WebAssembly-port deep dive"
kind: journal
created: "2026-09-14"
tags:
  - architecture
  - browser
  - emscripten
  - erlang
  - erts
  - evidence
  - otp
  - webassembly
aliases:
  - "ERTS component deep-dive journal"
---

# 2026-09-14 ERTS architecture and minimum WebAssembly-port deep dive

## Objective

Expand the existing feasibility corpus into a component-level account of ERTS
and identify the minimum pieces to preserve, adapt, or prohibit for a
browser-compatible upstream ERTS build.

## Baselines

- Archive worktree: `/home/ducky/code/erts_wasm`
- Erlang/OTP checkout: `/tmp/erts-wasm-otp-29.0.6`
- Erlang/OTP revision:
  `e07fd07837e5aa845657f5fa340637121e451d47` (`OTP-29.0.6`, ERTS 17.0.6)
- AtomVM checkout: `/tmp/erts-wasm-atomvm`
- AtomVM revision: `0220c78ee9e7cf6c763a278b44d81ce309fcf1ab`
- Research date: 2026-09-14, America/Toronto

The OTP and AtomVM repositories were checked out only for read-only source
inspection. One repository explicitly excluded by the archive policy was not
checked out or used as evidence.

## Evidence gathered

### Upstream ERTS architecture

Official OTP documentation, source, and Erlang/OTP engineering articles were
used to trace:

- loader-time BEAM instruction transformation and interpreter dispatch;
- process signal queues, mailboxes, links, and monitors;
- process-local memory, binaries, garbage collection, and allocator families;
- schedulers, dirty schedulers, async work, thread progress, timers, and I/O
  polling;
- boot scripts, preloaded modules, module/export/code indices, and ERTS system
  processes; and
- the system interface for time, environment, preload I/O, dynamic loading,
  thread integration, allocation, and program lifecycle.

Representative commands included:

```sh
git -C /tmp/erts-wasm-otp-29.0.6 rev-parse HEAD
rg -n "erts_code_purger|erts_literal_area_collector|erts_dirty_process_signal_handler|erts_trace_cleaner|erts_start_schedulers|erts_sys_main_thread" /tmp/erts-wasm-otp-29.0.6/erts/emulator/beam/erl_init.c
rg -n "prim_file|erl_prim_loader|kernelProcess|primLoad" /tmp/erts-wasm-otp-29.0.6/erts/preloaded/src/init.erl /tmp/erts-wasm-otp-29.0.6/erts/preloaded/src/Makefile
```

The startup inspection confirmed creation of the code purger, literal-area
collector, three dirty process-signal handlers, and trace cleaner before
`erts_start_schedulers()`, followed by `erts_sys_main_thread()`. The boot
inspection confirmed that `init.erl` starts `erl_prim_loader`, retrieves the
boot file, processes `primLoad` and `kernelProcess` instructions, and consults
`prim_file:get_cwd()` in the boot path. This raises the floor for a supposedly
file-free immutable release: a virtual release path and loader contract remain
necessary.

### Browser and WebAssembly constraints

Official Emscripten material was reviewed for pthread Workers,
`SharedArrayBuffer`, `PROXY_TO_PTHREAD`, pool precreation and exhaustion,
main-agent waits, memory growth, virtual files, networking, Asyncify, JSPI,
dynamic linking, and sanitizers. WebAssembly and browser standards were checked
for threads, atomics, proposal status, cross-origin isolation, and containment.

The central constraint is that browser pthreads are not a transparent POSIX
process. Worker startup is asynchronous, blocking the main agent is unsafe,
and all participating assets and deployment headers must support shared
memory. The Emscripten network and file layers are mechanisms, not reasons to
grant the initial runtime broad ambient authority.

### Scientific literature

The existing corpus source notes were re-read for:

- Sagonas and Wilhelmsson on local heaps, message-copy costs, shared memory,
  and collector tradeoffs;
- Trinder et al. on scheduler, time, timer, ETS, and shared-state interactions;
- Powers, Vilk, and Berger on the scope of Unix emulation in a browser;
- Jangda et al. on subsystem-level Wasm/native performance attribution;
- Lehmann, Kinder, and Pradel on unsafe source bugs surviving into Wasm; and
- Narayan et al. on speculative-execution risk beyond Wasm's architectural
  isolation.

No numerical result from an older engine, OTP release, or server workload was
treated as a browser-ERTS forecast.

### Comparative browser runtimes

AtomVM's official documentation and pinned Emscripten source were examined as
comparative evidence. Representative commands included:

```sh
git -C /tmp/erts-wasm-atomvm rev-parse HEAD
rg -n "PROXY_TO_PTHREAD|ENVIRONMENT=web,worker|smp_scheduler_join_all|sys_poll_events" /tmp/erts-wasm-atomvm/src/platforms/emscripten /tmp/erts-wasm-atomvm/src
```

The port uses a pthread-based off-main-thread topology and a condition-backed
event queue. Its platform scheduler threads are detached and its join-all hook
does not join them. This is evidence for the broad topology and wakeup pattern,
not for strict teardown. The project's documented BEAM/OTP differences prevent
using its small implementation surface as an estimate for upstream ERTS.

An undated public page presenting Erlang/OTP compiled with Emscripten was also
inspected. It exposed no pinned source, patch, build, conformance, security, or
lifecycle record and was retained only as a weak feasibility signal.

## Synthesis reached

The work produced three implementation buckets:

1. preserve ERTS's interpreter, loader/code data, processes, signals,
   scheduling/thread progress, terms, GC/allocators, atoms, binaries, timers,
   ETS, core BIFs, preloads, and the matching OTP boot spine;
2. adapt the build target, thread/Worker substrate, clocks, wakeup/polling,
   entropy, immutable release loading, diagnostics, lifecycle, and typed host
   broker; and
3. initially prohibit JIT, distribution, dynamic native loading, raw sockets,
   OS processes, shell/terminal, arbitrary files/environment, mutable code, and
   optional host capabilities.

The term “minimum port” is now split into compile/link, cold boot, semantic
core, safe/disposable host boundary, and qualified OTP/Elixir profile. This
prevents a browser demo from being mistaken for semantic or product
feasibility.

## Negative findings and limitations

- No upstream-supported ERTS Emscripten target was found in the pinned release.
- No compile, link, boot, browser run, semantic test, benchmark, or teardown
  cycle was performed.
- The exact ERTS-to-Worker mapping and minimum Worker pool remain unknown.
- The exact minimal `kernel`/`stdlib` module closure remains unknown.
- JSPI proposal maturity does not establish stable Emscripten support; the
  toolchain documentation still labels it experimental.
- Comparative runtime and demo evidence cannot establish upstream ERTS
  compatibility, patch size, security, or lifecycle behavior.

## Outputs

- [ERTS architecture and the minimum browser WebAssembly port](../20-notes/erts-architecture-and-minimal-browser-webassembly-port.md)
- [ERTS architecture and minimum browser-port map](../10-maps/erts-architecture-and-minimal-browser-port.md)
- [Minimum browser platform-contract inquiry](../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md)
- [AtomVM runtime and WebAssembly-port source note](../30-sources/atomvm-project-2026-runtime-and-webassembly-port.md)
- [Erlang/OTP WebAssembly demonstration source note](../30-sources/vasetenkov-erlang-otp-webassembly-demo.md)
