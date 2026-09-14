---
title: "OTP and Elixir compatibility profile"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - compatibility
  - elixir
  - erlang
  - otp
  - releases
  - testing
aliases:
  - "ERTS-Wasm language and library profile"
---

# OTP and Elixir compatibility profile

## Decision

Define compatibility as a versioned, machine-readable closure with executable
native/Wasm evidence, not as the presence of OTP or Elixir files. Prove a small
Kernel/STDLIB Erlang profile first, expand core OTP behaviours second, and pin
an exact Elixir patch only after those gates pass.

## What a profile records

For every release application and module, record exact version and digest,
load phase, BEAM imports/opcode range, application dependencies, preloads,
registered processes, environment/configuration input, files/`priv` assets,
ports, BIFs, NIFs, linked-in drivers, `on_load`, dynamic loading, distribution,
terminal/shell, network/storage/crypto capability, and tests. Each item has one
status:

- `supported` — required semantics pass on the pinned browser matrix;
- `partial` — named functions or environmental semantics are excluded and both
  positive and negative behavior is tested;
- `unsupported` — absent or deterministically rejected; or
- `unknown` — not eligible for release admission.

A build-time static analysis is necessary but incomplete. BEAM imports can
resolve dynamically, application configuration changes reachability, and an
import stub does not prove the target module is present. Combine `.rel`/`.app`
metadata, BEAM chunk/import inspection, native artifact and `on_load`
inventory, native-oracle tracing, browser tracing, broker requests, and
loader-negative tests.[^otp-boot]

## Tier 0: POC semantic kernel

The POC release includes exact Kernel and STDLIB plus the ordinary Erlang
`erts_wasm_poc` harness application. It must demonstrate terms, exceptions,
processes, reductions, message order and selective receive, timers, GC, basic
ETS, names, links, monitors, application boot/stop, and one-for-one supervisor
restart. A separate `erts_wasm_loader_probe` module is packaged but unreachable
during boot; its single-use authorization closes admission before the real
loader publishes and executes it prior to readiness.

The POC does not claim every Kernel/STDLIB API. Files, raw sockets,
distribution, OS processes, environment, terminal, shell, compiler, runtime
eval, arbitrary code load, dynamic NIF/driver load, hot upgrades, network,
persistence, and rendering are either excluded from the closure or return a
declared result. Boot-required internals are distinguished from public support.

Run the same BEAM capsule on native OTP 29.0.6. Compare exact values and event
orders where specified and allowed outcome sets for races; declare clock and
browser-progress tolerances in advance. A browser-only rewritten test is not a
native oracle.

## Tier 1: core OTP behaviours

Add `gen_server`, `gen_statem`, supervisors and dynamic supervisors,
application lifecycle, selected `gen_event`/registry functionality, and
standard-library modules one closure at a time. Exercise startup, calls/casts,
timeouts, hibernation if admitted, crashes, restart intensity, shutdown,
code-change callbacks even if hot replacement is denied, and resource
settlement.

Use curated applicable upstream Common Test suites plus purpose-built
differential and property tests. An auto-skipped test is an unsupported/unknown
record, not evidence. Systematic interleaving tools improve the workload but do
not replace runtime atomic and lifecycle testing.[^testing]

## Tier 2: exact Elixir profile

The Elixir 1.20 series declares OTP 27–29 compatibility, but browser support
does not follow from that table.[^elixir] At C5, select one exact Elixir patch,
pin its source and compiler to the OTP generation, and compile everything on
the trusted build host. Treat a Mix release as packaging input: its Unix/Windows
scripts, remote commands, runtime environment, temporary files, distribution,
and config-provider assumptions are not the browser runtime contract.

The first profile excludes Mix, IEx, compiler applications, `Code.eval_*`,
source/file compilation, arbitrary `Code`/`:code` loading, runtime config
providers, and unsupported native libraries. Configuration is materialized at
build time or supplied through a small typed manifest schema. Qualify ordinary
Elixir modules using protocols, structs, exceptions, maps/binaries, processes,
`GenServer`, supervisors, and application lifecycle. Add Unicode, calendar,
I/O protocols, regex, crypto, and other modules only after their exact closure
passes.

## Tier 3: optional applications and capabilities

An OTP/Hex application is not accepted because it is “pure Elixir” or compiles
on native OTP. It receives a profile extension that identifies every module,
native artifact, code-loading behavior, asset, capability, quota, and lifecycle
rule. The bundle is content-addressed and generation-compatible. Removing it
removes its authority and tests.

Applications that fundamentally require native OS processes, raw sockets,
distribution, unrestricted files, unsupported NIFs, or unbounded runtime
compilation may remain unsupported. Compatibility is a product profile, not an
obligation to emulate all of Unix.

## Evidence gates

- The closure generator and runtime trace agree; every observed module/native
  edge is declared, and deliberately deleted edges produce named failures.
- Each supported/partial entry links exact positive, negative, browser, and
  native-oracle results plus manifest and artifact identity.
- Calls to excluded compiler/eval/load/environment/file/socket/distribution
  surfaces fail deterministically without broker or loader bypass.
- Representative applications survive repeated boot, crash/restart, cancel,
  and whole-generation replacement with stable resource slopes.
- No marketing-level OTP or Elixir claim exceeds the published machine-readable
  profile and browser matrix.

## Principal risks

Transitive native edges can hide in `on_load` or configuration. Static imports
over- and under-approximate dynamic behavior. Build-time closure can omit rare
error paths. Elixir's independent patch cadence can change OTP compatibility.
Broadening a profile can grant host authority to every admitted module in the
same ERTS instance.

## Sources

[^otp-boot]: Erlang/OTP Project, [OTP boot, releases, and compatibility](../../30-sources/erlang-otp-project-2026-otp-boot-security-and-compatibility.md).
[^testing]: Erlang/OTP Project and Maria Christakis et al., [OTP testing and observability](../../30-sources/erlang-otp-project-2026-testing-time-and-runtime-observability.md) and [systematic concurrency testing](../../30-sources/christakis-et-al-2013-concuerror.md).
[^elixir]: Elixir Project, [OTP 29 compatibility, code loading, and releases](../../30-sources/elixir-project-2026-otp-29-compatibility-and-releases.md).
