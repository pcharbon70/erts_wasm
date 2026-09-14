---
title: "Memory, garbage collection, and shared state"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - allocators
  - ets
  - garbage-collection
  - memory
  - wasm32
  - webassembly
aliases:
  - "ERTS-Wasm memory component"
---

# Memory, garbage collection, and shared state

## Decision

Preserve ERTS terms, process heaps/stacks, generational GC, binaries, allocator
families, atoms, literal areas, ETS, and boot-required persistent terms. Begin
with fixed shared linear memory and malloc-backed carriers rather than faking a
general `mmap`. Treat out-of-memory or memory corruption as generation-fatal.

## Memory model that must remain intact

ERTS normally gives each process a combined heap/stack block and a local
generational semi-space copying collector. Ordinary messages follow ownership
and copying rules; larger binaries are reference-counted outside process heaps
and can be shared. This design limits pause scope but does not make node-wide
memory the sum of independent process limits.[^memory]

Specialized allocator families serve process heaps, binaries, ETS, literals,
drivers, temporary data, and different lifetimes. Scheduler-specific instances
and delayed deallocation depend on thread progress. Atoms are global and are
not garbage-collected. Literal areas and code can remain referenced by
processes. ETS tables are shared runtime objects governed by owner and table
semantics, not reachability from an application variable.[^erts-source]

On 32-bit targets ERTS uses a distinct literal strategy with smaller aligned
regions and a card map rather than a typical 64-bit large reserved literal
range. That makes `wasm32` a plausible route, but it does not prove every
pointer/tag conversion, alignment, binary limit, allocator carrier, or
fragmentation path correct.

## POC implementation

Set shared `INITIAL_MEMORY == MAXIMUM_MEMORY`. Memory growth changes buffer/view
behavior across JavaScript and Workers and can add stop-the-world or allocation
latency. Removing it from the first proof makes the memory ceiling explicit and
prevents stale external typed-array views. The manifest budgets, before
instantiation:

- Wasm static data, ERTS runtime tables, every pthread stack, and allocator
  metadata;
- mounted release bytes, loaded code, literals, atoms, exports, and funs;
- expected process heaps/stacks, mailboxes, binaries, ETS, persistent terms,
  tracing, and temporary loader/GC peaks; and
- broker request/completion rings, host copies, diagnostics, and operating
  headroom.

Configure the target as lacking genuine OS reserve/commit/unmap semantics until
an Emscripten probe proves the exact behavior ERTS expects. Prefer the upstream
`sys_alloc`/libc-malloc carrier fallback while retaining allocator identities
and statistics. Do not implement `mmap` as a success-returning wrapper that
cannot independently release or protect ranges. Exercise the actual 32-bit
literal alignment/card-map path.

Use `max_heap_size` with kill behavior and shared-binary accounting for admitted
application processes, but document its limits: checks occur around GC and do
not cover atoms, ETS, persistent terms, runtime tables, all fragmentation, or
every shared object. Add independent generation ceilings for processes, atoms
created after boot, ETS tables/objects/bytes, timers, outstanding host bytes,
mailbox high-water marks, code/literals, and diagnostic output. The hard final
boundary remains the Wasm maximum plus Worker termination.

Ingress bytes are length-checked before allocation, copied from broker storage
into ERTS-owned binaries/terms, and never decoded as arbitrary ETF. Egress is
snapshotted before the ERTS buffer or ring slot can be reused. “Zero copy” is
not a POC goal because lifetime and mutation ambiguity would cross the trust
boundary.

Support ETS operations needed by boot plus basic private/protected `set`
create, insert, lookup, delete, and owner-exit cleanup. Exclude file-backed
operations. Permit exact boot-required `persistent_term` setup; tightly bound
or deny application update/delete until the table-copy and global process-scan
effects are measured.

## In-depth implementation

Qualify bounded shared-memory growth as a separate profile. Reacquire every
JavaScript view after a potentially growing call and test concurrent Workers,
allocation failure, and latency cliffs. Do not silently switch the POC
generation between fixed and growing memory. Treat memory64 as a distinct
build/browser/profile decision.

Measure and then tune carrier strategy, allocator instances, contention,
fragmentation, thread stacks, GC generations, binary allocation, and mailbox
data placement. Expand ETS through all table kinds, concurrency options,
ordered-set contention-adapting trees, fixation/traversal, heirs, large-table
deletion, concurrent owner death, and accurate ownership/accounting. Expand
`persistent_term` only with explicit update-rate and latency budgets.

## Evidence gates

- Audit every term word, pointer/integer cast, alignment, size multiplication,
  max-object check, memory primitive, and literal path under `wasm32`; sanitizer
  and fuzz builds retain minimized failures.
- Report initial, steady, peak, post-GC, post-process-exit, post-table-delete,
  and post-generation-disposal memory across at least logarithmically scaled
  workloads.
- Compare native/Wasm GC results, live/copied words, pause distributions,
  binary/sub-binary retention, message reclamation, atom growth, code/literals,
  allocator committed/used bytes, ETS owner cleanup, and persistent-term stalls.
- Allocation just below and above every configured ceiling has a deterministic
  result; OOM never leaves a generation advertised as ready.
- Repeated failed loads, rejected BEAM files, process churn, table churn, and
  start/dispose cycles have no unexplained positive slope.

## Principal risks

The theoretical `wasm32` address space overstates practical contiguous shared
memory available in browsers. Global resources defeat naive per-process
quotas. Reference-counted binaries can retain large buffers through tiny
sub-binaries. Fragmentation can exhaust a fixed heap before live-byte budgets.
Browser OOM behavior may be a trap or Worker loss rather than a recoverable
allocation result.

## Sources

[^memory]: Konstantinos Sagonas and Jesper Wilhelmsson, [efficient Erlang memory management](../../30-sources/sagonas-wilhelmsson-2006-erlang-memory-management.md).
[^erts-source]: Erlang/OTP Project, [ERTS allocators, GC, source, and runtime architecture](../../30-sources/erlang-otp-project-2026-erts-build-runtime-and-source.md).
