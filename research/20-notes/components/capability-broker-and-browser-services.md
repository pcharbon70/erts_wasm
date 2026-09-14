---
title: "Capability broker and browser services"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - browser
  - capabilities
  - cryptography
  - networking
  - ports
  - security
  - storage
aliases:
  - "ERTS-Wasm host broker"
---

# Capability broker and browser services

## Decision

Expose browser authority through a versioned, typed, bounded, deny-by-default
broker outside ERTS. Preserve the ERTS port abstraction at the language edge,
but do not expose arbitrary JavaScript calls, property traversal, URLs,
filesystem paths, raw ETF, POSIX sockets, or native-library loading.

## Trust and authority model

Core Wasm imports are the module's host authority. An import named `fetch` or
`call_js` is therefore not harmless plumbing; it can grant ambient origin and
page authority to any code that reaches it. Capability systems instead begin
with explicit resource handles and allow rights to be attenuated.[^capsicum]
WASI's related design principles distinguish resource handles from sparse
link-time capabilities and avoid ambient global namespaces; this is useful as
a design model even though browser ERTS is not initially a WASI component.[^wasi]

An ERTS instance is one trust and failure domain. A handle presented to one
BEAM process cannot be protected from all other admitted code inside the same
VM solely by the host broker. Separate mutually untrusted programs need
separate generations. Within one same-trust generation, application-level
ownership remains useful for lifecycle and accounting, not a hard isolation
claim.

## Broker protocol

Use one statically linked ERTS port driver or equally narrow upstream-facing
adapter. A request contains fixed-width header fields:

```text
protocol-version | generation | request-id | capability-slot | capability-epoch
operation | flags | deadline | payload-length | response-ceiling
```

The capability table lives in broker-owned JavaScript state. A slot resolves
only when generation, epoch, operation, and rights match. Closing or attenuating
a handle increments its epoch or removes it; integer guessing in Wasm cannot
recover a revoked resource.

Before semantic parsing or allocation, validate header availability, protocol,
state, generation, operation, handle, encoded length, expanded length,
concurrency quota, total bytes, and deadline. Snapshot Wasm-to-JS payload bytes
into broker-owned storage before releasing the request slot. For responses,
build and validate in broker memory, copy into a reserved completion slot,
publish immutably with atomics, wake ERTS, then have the driver copy into an
ERTS-owned binary before releasing the slot. A completion for a cancelled or
old generation is consumed only to release resources and is never delivered.

Queues are bounded. Saturation returns a typed `busy`/quota result or applies a
declared coalescing rule; it never allocates an overflow list or silently drops
state-changing operations. Every operation is cancellable where the browser API
permits it, and generation teardown revokes the handle regardless of whether a
final callback arrives.

The protocol uses a small fixed schema or length-delimited typed encoding. Do
not accept ETF at this boundary: a recent ERTS advisory demonstrated that a
tiny malformed external term could crash the emulator below Erlang exception
handling and the `safe` option.[^otp-security]

## POC implementation

Do not implement general application capabilities. The cold-boot profile has
only internal handles for:

- fixed-size cryptographic entropy seeding;
- verified release bytes supplied before boot for the write-denied mount;
- monotonic/wall clock sampling and timer/poll wake;
- bounded structured diagnostics and fatal status; and
- cooperative start, cancellation, identity attestation, and exit reporting.

Hard termination is deliberately not an ERTS import or forgeable broker
handle. It remains out-of-band authority held by the generation supervisor,
which can terminate the complete Worker graph without VM cooperation.

These functions should be individual reviewed imports or an equally small
control channel. Import inspection must prove that DOM, Fetch, WebSocket,
IndexedDB, eval, generic object access, and arbitrary URL construction are
absent from the POC artifact.

## In-depth capability sequence

Add capabilities only after the generic frame, queue, cancellation, mutation,
and teardown gate passes:

1. **Fetch handle.** Bind allowed origin/path template, methods, request/response
   headers, credential and redirect mode, body and decompression ceilings,
   concurrency, deadline, and response-stream policy. Use `AbortSignal`; never
   pass a raw URL supplied by BEAM directly to `fetch`.[^browser]
2. **WebSocket handle.** Bind exact secure URL and subprotocol, frame kind and
   size, inbound/outbound queue limits, reconnect authority, idle/lifetime
   policy, and close behavior. Add a broker high-water mark because classic
   WebSocket `send()` only exposes queued bytes after enqueue and can close when
   its internal buffer is full.
3. **Storage handle.** Bind origin-local namespace, schema version, object-store
   set, operation mode, key/value and transaction limits, durability hint,
   migration procedure, and deletion/export policy. Treat quota, eviction,
   blocked upgrades, abort, and forced connection close as normal outcomes.
4. **Crypto handle.** Keep `CryptoKey` in broker state, constrain algorithms,
   usages, extractability, input/output sizes, and rate. Return operation
   results, not raw secret-key material. Browser algorithm availability remains
   part of the profile.
5. **Other APIs.** Clipboard, media, sensors, notifications, files, and similar
   user-mediated authority each require their own capability and consent/
   lifecycle analysis; they never arrive through a generic extension opcode.

Browser networking is not Erlang distribution or raw TCP/UDP. A WebSocket port
may support an application protocol later, but `net_kernel`, epmd, distributed
node security, and POSIX socket semantics remain unsupported until separately
designed and tested.

## Evidence gates

- Fuzz frame headers, lengths, wraparound, opcodes, handles, states, mutation
  during validation, queue indices, cancellation, duplicates, and stale
  generations in native sanitizers and both browsers.
- At `+S 1:1`, a full request queue or slow broker cannot block scheduler
  progress, timers, or teardown.
- Capability removal removes its imports, modules, JavaScript implementation,
  manifest grants, and tests; a no-capability profile has no residual authority.
- Per-capability matrices cover permission/CORS failures, redirects, streaming,
  quota, network loss, close, freeze, cancellation, and generation replacement.
- Logs and error terms do not echo secrets, credentials, arbitrary bodies, or
  sensitive URLs.

## Principal risks

A flexible broker can become a syscall ABI in disguise. Mutable shared buffers
create time-of-check/time-of-use bugs. Host APIs may keep data or callbacks
alive after cancellation. Browser origin policy is not application-level least
authority. Granting a capability to one process can be mistaken for intra-VM
security that ERTS does not provide.

## Sources

[^capsicum]: Robert Watson et al., [Capsicum capability research](../../30-sources/watson-et-al-2010-capsicum.md).
[^wasi]: WebAssembly and WASI contributors, [WASI and threading status](../../30-sources/webassembly-project-2026-wasi-and-threading-status.md).
[^otp-security]: Erlang/OTP Project, [boot and hostile-input security evidence](../../30-sources/erlang-otp-project-2026-otp-boot-security-and-compatibility.md).
[^browser]: WHATWG and W3C, [Fetch, WebSocket, IndexedDB, Storage, and WebCrypto standards](../../30-sources/browser-platform-lifecycle-and-capability-standards-2026.md).
