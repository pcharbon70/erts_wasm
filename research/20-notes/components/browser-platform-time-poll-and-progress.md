---
title: "Browser platform time, poll, and progress"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - browser
  - entropy
  - filesystems
  - polling
  - time
  - timers
  - webassembly
aliases:
  - "ERTS browser system layer"
---

# Browser platform time, poll, and progress

## Decision

Add a named browser system layer behind ERTS's existing `sys`, `ethread`, time,
and check-I/O seams. It implements only runtime progress and immutable boot
needs. It must not grow into a generic POSIX emulator.

## Required POC contract

| Service | Browser implementation | Declared failure |
| --- | --- | --- |
| Monotonic time | One shared clock provider, a qualified `performance.timeOrigin + performance.now()` normalization, or a proven Emscripten `clock_gettime(CLOCK_MONOTONIC)` mapping | Abort before boot if it decreases, disagrees across Workers, or lacks declared behavior |
| Wall time | `Date.now()` sampled separately | Available for language display; never an authorization or expiry oracle |
| Timer/poll wake | Earliest ERTS deadline plus bounded completion ring and atomic wake word | Late is observable; never report an early timer; overflow follows policy |
| Entropy | Fixed-size `crypto.getRandomValues` seed copied into ERTS-owned memory | Fatal startup failure; never substitute time or weak PRNG |
| Boot files | Verified release mounted at one fixed virtual root | No paths outside root; writes and undeclared members fail |
| Startup/environment | Manifest-fixed argv, root, cwd, code paths, locale/timezone policy | Unknown flag or lookup fails deterministically |
| Diagnostics/exit | Bounded records and host-visible fatal status | Rate-limit/drop by declared severity; exit enters generation cleanup |

The browser monotonic and wall clocks match ERTS's conceptual split: ERTS
timers are relative to Erlang monotonic time, and system time is derived through
an offset. The port should report its actual source, resolution, correction,
and suspension properties through `system_info`; it must not claim native
clock capabilities it has not measured. Raw `performance.now()` values from
different Worker globals are not directly comparable because each global has a
time origin; use an explicitly normalized common base or sample one clock
provider through shared state.[^otp-time][^browser]

Browser callback scheduling is not the clock. Hidden or frozen contexts can
delay tasks even when monotonic time advances. ERTS may therefore observe a set
of overdue timers on the next progress opportunity. Preserve timer-wheel
ordering and native cancellation races; do not “smooth” the pause in
JavaScript. For the POC, an unqualified page freeze or bfcache restoration
causes generation replacement rather than transparent continuation.[^browser]

## Poll and completion design

Retain ERTS timer wheels, `erl_check_io`, scheduler sleep, and event-wakeup
logic. Add a browser `erts_poll` backend with a small set of pseudo-sources:
host-completion queue, lifecycle/fatal control, and any statically admitted
port. It has no arbitrary file descriptors and does not report unsupported
sockets or files as ready.

Use bounded shared-memory rings with cache-line/alignment properties proven by
target probes. A producer reserves a slot, checks header and payload bounds,
writes the payload, publishes state with an atomic release operation, then
increments/notifies a wake word. The runtime observes with acquire ordering,
copies the completion into ERTS-owned storage, releases the slot, and recomputes
the nearest timer deadline. A MessagePort wake token may supplement browser
event-loop integration, but a token never carries trusted payload or replaces
the ring's sequence/generation check.

Do not park a scheduler waiting for a browser Promise. Do not apply Asyncify or
JSPI to the scheduler loop. A tightly bounded proof may test those mechanisms
at a leaf adapter, but Emscripten documents Asyncify's transformation and size
cost and still treats its JSPI path as evolving.[^emscripten]

The POC release can use ephemeral MEMFS without granting host filesystem
authority, but MEMFS is writable by default. Populate only verified bytes
before `erl_init`, then have the lower system/filesystem adapter deny
write/create flags, rename, unlink, truncate, directory mutation, links,
devices, and paths outside the manifest. Negative mutation tests establish the
write-denied claim. A later manifest-backed primitive loader can reduce the
generic virtual-filesystem surface after the boot trace identifies the exact
operations actually needed.

Unix signals, process IDs, terminal modes, child processes, dynamic-library
paths, arbitrary environment variables, raw sockets, and host filesystem paths
are absent. Callers either remain outside the admitted closure or receive a
stable `enotsup`/profile-specific failure; synthetic success is forbidden.

## In-depth implementation

Qualify hidden-tab throttling, machine sleep, freeze/resume, bfcache, time-zone
changes, wall-clock jumps, timer storms, and capability completion races. If a
runtime can safely suspend, define a handshake that stops new broker requests,
drains or cancels work, records the time policy, and acknowledges quiescence
before freeze. Resume validates generation and browser state before releasing
completions. Otherwise replacement remains the supported policy.

Bounded scratch files, persistence, network sockets-as-ports, and additional
clock sources are optional capabilities layered above this substrate. They do
not alter the bootstrap contract and must be removable from profiles that do
not use them.

## Evidence gates

- Cross-Worker monotonic samples never decrease and agree within a declared
  observation method; resolution and sleep/background behavior are recorded.
- Native/Wasm timers never fire early; exact cancel/read/expiry race outcomes
  fall within the native-allowed set.
- Queue full, wraparound, malformed headers, oversized payloads, stale
  generation, duplicate completion, cancellation, and wake-before-publish all
  produce specified results without corrupting ERTS.
- Idle CPU, wake latency, timer drift, and UI long tasks are measured with the
  complete runtime, not a toy Worker.
- Every unsupported OS path fails without adding an undeclared import or
  browser request.

## Principal risks

Emscripten libc functions can exist while differing in suspension, signal,
filesystem, or polling semantics. Browser timing privacy can coarsen clocks.
Queue wakeups can be lost if publication ordering is wrong. Page freeze can
suspend both runtime and supervisor, so lifecycle claims must distinguish
logical policy from wall-clock promptness.

## Sources

[^otp-time]: Erlang/OTP Project, [testing, time, and runtime observability](../../30-sources/erlang-otp-project-2026-testing-time-and-runtime-observability.md).
[^browser]: WHATWG, W3C, and WICG, [browser lifecycle, time, and capability standards](../../30-sources/browser-platform-lifecycle-and-capability-standards-2026.md).
[^emscripten]: Emscripten contributors, [browser porting runtime](../../30-sources/emscripten-project-2026-browser-porting-runtime.md).
