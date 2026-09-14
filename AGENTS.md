# Repository instructions

These instructions apply to the entire repository. This is a Markdown research
archive, not an implementation repository. Preserve exploratory work while
keeping provenance, navigation, security assumptions, and structure reliable.

## Markdown viewing

Always use the MarkText tool when opening Markdown (`.md`) documents. Do not
substitute a generic editor, browser preview, or another document viewer. If
MarkText is unavailable, state that limitation explicitly instead of silently
opening the document with a different tool. Read-only command-line inspection
for search, validation, and repository maintenance is still permitted.

## Project mission

Determine whether the official upstream Erlang Runtime System (ERTS) can be
cross-built into a secure, maintainable browser WebAssembly runtime that boots
a version-matched OTP profile and executes ordinary admitted BEAM modules.
This is a runtime-porting and product-feasibility program, not merely an
exercise in producing a `.wasm` binary.

The intended result preserves Erlang/OTP process, mailbox, scheduling, timer,
garbage-collection, ETS, link, monitor, application, and supervision semantics
closely enough to support a useful pinned OTP and Elixir subset. It must also
fit the browser's asynchronous execution model, stay off the page UI thread,
grant no ambient host authority, terminate cleanly, meet explicit product
budgets, and remain practical to update when ERTS or the toolchain changes.

Prefer a small, reviewable platform layer over a new BEAM implementation or
broad POSIX emulation. Treat semantic compatibility, browser deployment,
Worker topology, lifecycle, resource limits, supply-chain maintenance, and
security as independent requirements. A build, boot, or visual demonstration
does not by itself establish feasibility.

## Major goals

1. **Preserve upstream semantics.** Start from a pinned upstream ERTS and run
   matching official OTP BEAM modules. Do not casually replace the scheduler,
   process model, garbage collector, loader, or OTP behaviours.
2. **Create the smallest browser platform port.** Identify every ERTS
   dependency on threads, atomics, polling, timers, allocators, files, signals,
   dynamic loading, ports, and other OS facilities. Adapt only the facilities
   the supported profile needs; reject unsupported operations predictably.
3. **Keep ERTS off the UI thread.** Run the interpreter in a directly
   supervised Worker group. Compare candidate Emscripten Worker/pthread
   topologies using boot, responsiveness, ownership, and teardown evidence.
4. **Define a version-locked runtime profile.** Ship an immutable release with
   matching ERTS, `kernel`, and `stdlib`, followed only by explicitly qualified
   OTP and Elixir modules. Compatibility is a tested allowlist, not a claim of
   general BEAM forward compatibility.
5. **Make host authority explicit.** Expose browser services through a
   versioned, typed, bounded, deny-by-default capability broker. Rendering is
   a declarative protocol to a separate DOM adapter; networking, persistence,
   and cryptography are separately admitted capabilities.
6. **Prove lifecycle and resource control.** Account for every Worker,
   MessagePort, timer, listener, request, renderer handle, shared-memory
   buffer, and pthread registry entry. Forced termination must reject stale
   completions and repeated boot/dispose cycles must settle without a positive
   resource slope.
7. **Establish reproducible ownership.** Keep the upstream patch stack small;
   pin sources and toolchains; produce hashes, manifests, SBOMs, provenance,
   compatibility reports, and reproducible artifacts; rehearse security
   updates and upstream rebases.
8. **Use falsifiable gates.** Compare observable native and Wasm behavior in
   Chrome and Firefox, measure size/startup/memory/latency/cleanup, fuzz trust
   boundaries, and retain negative results. Product budgets must be approved
   rather than invented by research authors.

## Target architecture under investigation

- Upstream ERTS compiled for `wasm32-unknown-emscripten`.
- The portable BEAM interpreter, with BeamAsm/JIT disabled initially.
- Emscripten pthreads, shared WebAssembly memory, and cross-origin isolation as
  the first threading hypothesis; a threadless ERTS is a separate research
  program, not a build flag.
- Fixed initial/maximum shared memory for the first proof, with bounded growth
  deferred until correctness and JavaScript-view lifetime are qualified.
- A directly supervised browser Worker group with an independently schedulable
  watchdog capable of terminating the complete runtime generation.
- A content-addressed, immutable release containing matching boot files, `.app`
  metadata, BEAM modules, and approved assets.
- An Emscripten controlled-start seam that suppresses automatic `main`, mounts
  and seals the verified release, then permits one supervisor-owned ERTS entry.
- One manifest-listed ordinary qualification module loaded through the normal
  ERTS prepare/finish path after boot but before `ready`; its single-use exact
  authorization closes further code admission before native parsing begins.
- A small static browser system adapter and asynchronous capability broker;
  no generic JavaScript, DOM, socket, shell, or filesystem escape hatch.
- A separate renderer that consumes bounded semantic operations. Phoenix and
  Plug are independent server-adapter concerns; LiveView and LocalLiveView are
  deferred from this runtime investigation.
- One runtime may serve multiple components in the same trust domain. Mutually
  untrusted code requires separate Worker-plus-Wasm instances unless a future
  design proves stronger internal isolation.

The exact Worker topology, host-wakeup mechanism, supported OTP/Elixir surface,
numeric budgets, and long-term package ownership remain decisions to be made
from experiments rather than assumptions.

## Security model

Security is a day-one property. WebAssembly constrains linear-memory access and
host imports, but it does not make ERTS or statically linked C code memory-safe.
Treat one ERTS instance and its admitted code as a shared trusted failure
domain, with the browser engine, loader, broker, manifest verifier, page
bootstrap, delivery origin, and update path forming parts of the trusted base.

Keep host authority deny-by-default and treat browser events, network data,
stored bytes, decoded terms, URLs, and all other external data as hostile.
Preserve loader enforcement, capability checks, quota ownership, Worker
isolation, deterministic teardown, secret minimization, update response,
reproducibility, SBOM, provenance, sanitizers, and fuzzing in every relevant
proposal. Do not use untrusted Erlang External Term Format at a browser
boundary. Client-held data is neither server authorization nor confidential
from the browser user or a compromised origin.

## Current evidence boundary

- The pinned source-inspection baseline is Erlang/OTP 29.0.6, ERTS 17.0.6,
  commit `e07fd07837e5aa845657f5fa340637121e451d47`.
- The audit found no documented first-party ERTS browser target and confirmed
  that contemporary ERTS requires a thread implementation; `+S 1:1` is not a
  threadless build.
- `emcc` was not available during the recorded investigation. No ERTS/Wasm
  compile, OTP boot, browser conformance run, lifecycle test, benchmark, or
  support matrix has been produced by this corpus.
- The feasibility inquiry and canonical synthesis are developing. The
  authorized milestone plan in `research/60-planning/` has no completed gates
  and records no implementation evidence.
- Some documents retain BlazeX terminology because the research originated in
  that corpus. Historical framing does not establish current package ownership,
  roadmap authority, or adoption by another repository.

Never turn a research conclusion into an implementation or support claim.
Clearly label source facts, local observations, inferences, proposals, pass
criteria, and unresolved assumptions.

## Scope exclusions and stop conditions

Do not treat any of the following as the default solution:

- a new or clean-room BEAM implementation;
- direct native-Wasm compilation of each Elixir component as a substitute for
  ERTS semantics;
- ERTS execution or blocking waits on the browser UI thread;
- complete Unix/POSIX emulation, broad socket shims, or ambient filesystem
  access;
- dynamic NIFs/drivers, arbitrary code loading, shell/eval/compiler support,
  distribution, raw sockets, OS processes, or terminal facilities in the
  initial profile; or
- broad OTP or Elixir compatibility inferred from dependency lists or one
  successful component demo.

Stop or reassess the candidate if minimal boot requires broad POSIX emulation,
a pervasive unmergeable fork, UI-thread blocking, an unbounded import surface,
unsafe code loading, uncontrollable Worker groups, positive post-disposal
resource slopes, broken Tier 0 OTP semantics, or deployment headers that make
the intended product unusable.

The Popcorn stack is explicitly outside scope: do not inspect, cite, compare,
or use it as evidence. This exclusion does not prevent studying upstream ERTS,
OTP, Elixir, WebAssembly standards, browser APIs, Emscripten, operating-system
interfaces, or relevant scientific literature.

## Read these first

1. `research/10-maps/home.md` for corpus navigation and status.
2. `research/20-notes/erts-webassembly-runtime-architecture-and-milestones.md`
   for the canonical component model, runtime-loading contract, security
   architecture, and the two-stage proof and compatibility program.
3. `research/20-notes/erts-webassembly-component-implementation-deep-dive.md`
   and its linked `components/` notes for implementation decisions, seams,
   risks, and falsifiable gates for each architectural component.
4. `research/40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md`
   for the repository-neutral compile, boot, semantics, lifecycle, and
   qualification gates.
5. `research/60-planning/erts-webassembly-runtime-milestones.md` for the
   unchecked P0–P6 proof-of-concept gates and C1–C10 in-depth compatibility
   gates.
6. `research/40-inquiries/can-blazex-build-and-own-an-erts-webassembly-runtime-stack.md`
   for the falsifiable operational question, experiment gates, blockers, and
   resolution criteria.
7. `research/50-journal/2026-09-14-erts-architecture-and-minimal-webassembly-port-deep-dive.md`
   for the current component audit, comparative evidence, and negative
   findings.
8. `research/50-journal/2026-09-13-first-party-erts-webassembly-runtime-deep-dive.md`
   for pinned commands, observations, negative findings, and evidence limits.
9. `research/10-maps/erts-webassembly-runtime-stack.md` and
   `research/30-sources/README.md` for
   subsystem-specific trails into the primary and peer-reviewed evidence.

## Archive principles

- Folders describe document roles; maps, links, and tags describe subjects.
- Separate source claims, local evidence, synthesis, proposed architecture, and
  unresolved assumptions.
- Directory READMEs are exhaustive inventories; maps are selective.
- `research/frontmatter.schema.json` is the metadata authority.
- Change a document and every affected index, map, and local link together.
- Record exact versions, revisions, commands, dates, negative findings, and
  limitations for fast-moving software and standards.

## Canonical structure

```text
research/           Self-contained research corpus root
  00-inbox/         Unprocessed captures
  10-maps/          Curated conceptual navigation
  20-notes/         Synthesis and architecture reasoning
  30-sources/       Source and bibliographic notes
  40-inquiries/     Open research questions
  50-journal/       Dated research and experiment evidence
  60-planning/      Phased implementation plans and gates
  70-tools/         Corpus validators and tests
  90-archive/       Superseded material retained for provenance
  assets/           Attachments, datasets, and generated evidence
  templates/        Document and directory scaffolds
```

Keep the archive below `research/`. Do not add or rename another repository
top-level directory without a demonstrated need.

## Directory and metadata invariants

Every archive directory contains a `README.md` made from
`research/templates/directory-readme.md`. It uses `kind: map`, contains `Purpose`,
`What belongs here`, `Index`, and `Maintaining this index`, and inventories
every direct child except itself.

Every durable knowledge document begins with valid YAML frontmatter. Use
lowercase kebab-case filenames and tags, quoted ISO dates, YAML lists, `[]` for
intentional empty lists, and `null` for unknown source metadata. Notes require
`maturity`; inquiries require `status`. Do not invent bibliographic values.

## Research bundles

A deep dive normally contains a connected synthesis note, one source note for
each substantively used work, an open inquiry, a topic map, a dated journal,
and all affected indexes. Prefer primary specifications, source trees, official
documentation, and peer-reviewed work. Search snippets are discovery aids, not
evidence.

Implementation planning belongs in `research/60-planning/` and must retain unchecked
gates until executable evidence exists. A successful build, boot, or visual
demo alone does not establish semantic compatibility, security, lifecycle
cleanup, performance, or maintainability.

## Verification

Before reporting corpus work complete:

1. preserve unrelated changes;
2. run `python3 research/70-tools/validate_archive.py`;
3. run `python3 -m unittest discover -s research/70-tools -p 'test_validate_archive.py'`;
4. verify new external citations against primary sources;
5. run `git diff --check` when a Git worktree exists; and
6. inspect the complete change for stale paths and accidental rewrites.
