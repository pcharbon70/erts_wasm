---
title: "OTP boot and BEAM code loading"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - beam
  - boot
  - code-loading
  - erlang
  - erts
  - otp
  - runtime-loading
aliases:
  - "ERTS-Wasm loader and boot spine"
---

# OTP boot and BEAM code loading

## Decision

Preserve upstream ERTS initialization, preloads, `init`, `erl_prim_loader`, BEAM
validation/transformation, module/export tables, literal areas, and atomic code
indexes. Boot one generated embedded release from a verified read-only virtual
root. Before `ready`, explicitly admit one prepackaged ordinary BEAM module
through the normal loader; then close code admission for the POC generation.

## Boot chain that must remain real

`erl_init()` initializes allocators, atoms, code indexes, modules/exports,
processes, signals, schedulers, time, timers, GC, binaries, ETS, tracing, I/O,
loader, BIF/NIF support, external terms, and other services. It loads the
upstream preload set through the normal BEAM loader, commits the initial code
index, creates the first `init:boot/1` process, and starts system services such
as the code purger and literal-area collector.[^erts-source]

`init` starts `erl_prim_loader`, reads the binary boot file, decodes its terms,
and executes path, `primLoad`, `kernelProcess`, and apply instructions. Embedded
mode preloads the declared modules rather than demand-loading them, but explicit
code-server load APIs still exist. A `.rel` fixes ERTS and application versions;
the documented minimal OTP release includes Kernel and STDLIB.[^otp-boot]

The current primitive loader selects native-style `efile` or `inet` backends.
The smallest POC seam is therefore a conventional release tree in verified
MEMFS plus a lower write-denial policy, not a new loader implementation. MEMFS
is writable by default; its name alone establishes no immutability. A direct
manifest-backed primitive loader is a later surface-reduction option after
actual boot I/O is traced.

## POC release construction

On the exact native build host, generate `.rel`, `.script`, and `.boot` files
with exact Kernel/STDLIB versions and one small boot-harness application named
`erts_wasm_poc`. Package a separate ordinary module named
`erts_wasm_loader_probe`, but omit it from `primLoad` and every startup import
or call path. Pack the boot file, `.app` metadata, all transitive BEAM files,
and admitted `priv` assets into a deterministic archive. Record uncompressed
size and digest for every entry; reject duplicate, absolute, parent-traversal,
case-colliding, symlink, device, and undeclared paths before mount.

Start ERTS with manifest-fixed `-root`, `-bindir`, `-boot`, `-mode embedded`,
cwd, code paths, argv, and environment. The virtual tree is not a claim of host
filesystem support. It contains only the release, is not populated from user
URLs, and is discarded with the generation. After population, the lower
filesystem/system adapter must deny write/create open flags, rename, unlink,
truncate, directory mutation, links, devices, and every undeclared path; it
must not depend on an advisory permission bit. Boot bytes must be authenticated
before `init` decodes them; the loader's structural checks are not a signature
mechanism.

Use the upstream preload list first. Inventory every preload `on_load`, static
NIF/BIF, file, port, and driver edge. Dynamic NIF loading stays prohibited, but
some core modules may invoke `erlang:load_nif` to bind code compiled statically
into ERTS; each such case requires an exact allowlisted implementation and
negative test. Do not remove a preload merely to pass a failing boot unless its
dependency and semantic effects are documented.

## Admission below the code server

The BEAM file parser reads IFF chunks and the loader validates opcode ranges,
applies generated transformations, allocates code/literals, resolves labels and
imports, and stages module/export/fun/catch/record metadata. This is a parser and
linker, not a package policy. OTP can accept some older bytecode versions; atom
names may be interned before a later failure; compressed literals expand inside
native C; imports can create unresolved export stubs.[^interpreter]

Place admission before the first irreversible parse/allocation step while
retaining the native loader as the semantic authority. The candidate record
must include generation, profile, normalized module name, exact digest, encoded
and expanded size, expected compiler/OTP generation, `on_load` policy, import
closure, and request phase. The lower boundary rechecks the identity even if a
higher JavaScript layer already verified the release.

To prove that boundary, `erts_wasm_poc` first attests that startup never loaded
or referenced `erts_wasm_loader_probe`. It then atomically consumes the probe's
exact single-use name/digest authorization, which permanently closes all
further admission before the native parser runs. The normal prepare/finish path
publishes the module and the harness calls its exported test. Any prepare,
publication, execution, or state-transition failure disposes the generation;
the gate cannot reopen. Direct `code:load_binary`/path/primitive-loader bypass
attempts fail, and only then may Tier-0 qualification publish `ready`. This is
a pre-ready loader proof, not supported dynamic loading.

## Code indexes, literals, and `on_load`

ERTS retains active, staging, and spare/previous code indexes so module sets
can become visible atomically after thread progress. Preserve this machinery
even with one normal scheduler because auxiliary runtime threads still exist.
The qualification load must use ordinary prepare/finish publication and prove
that concurrent callers never see a half-installed set.

Modules can have current, old, and pending-`on_load` instances. Literal areas
can outlive code until every process has copied references, and purge behavior
coordinates through thread progress. The POC rejects application `on_load`,
replacement, deletion, and purge, then reclaims everything through whole-
generation disposal. Boot-required static `on_load` behavior is a separately
enumerated exception.

## In-depth implementation

First decide whether product requirements need in-generation loading at all.
An immutable profile can retain the hardened parser/admission path and use
whole-generation replacement indefinitely. If loading is required, accept only
signed content-addressed bundles with complete module/native/capability closure
and atomic publication. Hot replacement adds old/current semantics, qualified
state migration, soft/hard purge behavior, literal and fun lifetime, failing or
hanging `on_load`, rollback, quota, tracing/breakpoint interaction, and repeated
reclamation tests. Never mix ERTS, Kernel, or STDLIB generations in place.

## Evidence gates

- Delete each transitive boot module or static native edge in turn and require
  a deterministic named failure with complete cleanup.
- Attempt write/create open modes, rename, unlink, truncate, directory
  mutation, links, devices, and undeclared-path access after mount; each must
  fail and the manifest-bound release bytes must remain unchanged.
- Reject missing, altered, truncated, oversized, future-opcode, wrong-name,
  wrong-generation, undeclared-import, compressed-expansion, `on_load`, and
  post-ready inputs before harmful allocation or publication.
- The admitted qualification module is ordinary output from the pinned compiler
  and becomes visible atomically; its exact digest appears in both load trace
  and runtime attestation.
- Rejection does not crash a Worker or create a positive atom, literal, code,
  export, memory, or resource slope.
- Native and Wasm loader corpora return the same success or declared rejection
  class; fuzz and sanitizer failures preserve minimized inputs.

## Principal risks

Many initializers are unconditional, so link success can hide boot-time
dependencies on files, drivers, NIFs, distribution, or polling. A write-denied
MEMFS facade is still a relatively broad internal API. Authenticating after
boot-file decode is too late. Restricting only the Kernel `code` server leaves
primitive or BIF paths that may bypass policy.

## Sources

[^erts-source]: Erlang/OTP Project, [ERTS startup and source architecture](../../30-sources/erlang-otp-project-2026-erts-build-runtime-and-source.md).
[^otp-boot]: Erlang/OTP Project, [boot, release, security, and compatibility](../../30-sources/erlang-otp-project-2026-otp-boot-security-and-compatibility.md).
[^interpreter]: Erlang/OTP maintainers, [BEAM loader and interpreter articles](../../30-sources/erlang-otp-project-erts-interpreter-and-message-passing-articles.md).
