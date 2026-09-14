---
title: "Renderer, accessibility, and page lifecycle"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - accessibility
  - browser
  - lifecycle
  - rendering
  - security
  - user-interface
aliases:
  - "ERTS-Wasm renderer component"
---

# Renderer, accessibility, and page lifecycle

## Decision

Keep the DOM entirely outside ERTS and outside the POC. A later page adapter
accepts a bounded semantic operation protocol from one generation, applies it
to an owned subtree, and returns typed user events through the capability
broker. It never accepts HTML, JavaScript, selectors, arbitrary DOM properties,
or unrestricted CSS strings.

## Component boundary

The renderer owns DOM node handles, subtree ownership, event listeners,
staging/commit, focus and selection reconciliation, accessibility state,
paint-facing scheduling, and teardown. ERTS owns component/application state
and produces declarative operations. The broker owns frame validation, queue
limits, generation checks, and event delivery. Neither side passes live DOM
objects or Wasm pointers.

Start with a small algebra such as:

```text
create(native-element-kind, local-handle)
text(local-handle, bounded-utf8)
set-attribute(local-handle, allowlisted-name, typed-value)
append(parent-handle, child-handle)
remove(local-handle)
listen(local-handle, allowlisted-event, event-options)
focus(local-handle, focus-token)
commit(batch-id, expected-tree-version)
```

Allow native semantic elements first. Attribute policy is element-specific;
URL-bearing attributes use separately granted URL capabilities, not arbitrary
strings. Style uses a typed allowlist with value grammars and budgets. Text is
always a text node/`textContent`. There is no `innerHTML`, script, event-handler
string, custom-element name, iframe, `javascript:` URL, raw SVG/MathML fragment,
or generic property setter.

Validate batch operation count, depth, text bytes, attribute/style bytes,
handles, parent ownership, tree version, event subscriptions, and projected
DOM-node budget before mutation. Apply to a detached/staged representation,
commit atomically enough for the chosen protocol, and acknowledge success or a
typed rejection. A failed batch must not leave a half-applied tree.

Trusted Types can help enforce that accidental injection sinks remain
unreachable, but an unsafe policy can still mint unsafe values. The primary
design is safe DOM construction plus a CSP; Trusted Types is defense in depth
and a regression signal.[^rendering]

## Accessibility and interaction semantics

Use native HTML roles and behavior before ARIA. The operation schema must carry
typed accessible name/description relationships, states, properties, live-
region intent, label association, tab/focus behavior, and disabled/expanded/
selected values where native semantics do not suffice. Prevent dangling ID
references and role/state combinations that violate the renderer profile.

Keyboard, pointer, input, composition, focus, blur, selection, and form events
are not interchangeable byte messages. The adapter snapshots a minimal typed
event at dispatch, strips ambient DOM references, enforces data/coordinate/text
limits, tags it with tree and runtime generation, and applies coalescing only to
declared high-rate event kinds. Input-method composition and selection require
acknowledgement/version rules so a late render does not overwrite current user
state.

Test keyboard-only navigation, focus visibility/order, accessible name and
state, live-region behavior, zoom/reflow, contrast where style is admitted, and
representative screen-reader/browser combinations. Automated tree checks do
not replace manual assistive-technology tests.

## Lifecycle implementation

The POC has no renderer, but the generation supervisor establishes the policy
the renderer will use. `visibilitychange` to hidden is treated as the last
reliably observable session event: stop unnecessary UI work and persist only
through an already granted bounded capability. `pagehide`, freeze, bfcache,
discard detection, and termination are generation transitions, not merely DOM
events.[^lifecycle]

On freeze preparation, stop event admission, cancel or settle renderer batches,
release page locks and optional open capabilities, and record view state. For
the first supported renderer profile, navigation or an unqualified bfcache
restore terminates the old runtime and creates a fresh generation. A later live
resume requires proof that Workers, ERTS clocks/timers, DOM handles, focus,
connections, requests, and tree versions remain coherent.

Hard disposal removes the owned subtree or returns it to a defined empty shell,
detaches every event listener and observer, rejects pending batches/events,
invalidates all handles, and drops state snapshots according to policy. An old
generation can never mutate the newly mounted subtree even if its completion
arrives after replacement.

## Performance and backpressure

Batch semantic operations to bound crossings, but cap batch size and main-agent
work. Schedule commits around rendering opportunities, measure event-to-paint
and long tasks, and chunk large trees without exposing partial application state
as a successful commit. Coalesce only events whose semantics allow it; clicks,
submits, focus transitions, and input commits generally require ordered
delivery. On saturation, signal backpressure or trigger a declared replace/
resync, never grow an unbounded mailbox.

## Evidence gates

- Fuzz every operation, handle, parent relation, version, typed value, batch
  boundary, event frame, and stale-generation route; no input reaches an HTML
  or script sink.
- A malicious or wedged ERTS generation cannot mutate outside its owned
  subtree, retain DOM objects, or continue after handle revocation.
- Failed/oversized/stale batches are atomic from the protocol perspective and
  bounded in main-agent time and memory.
- Functional and accessibility golden scenarios cover focus, selection,
  composition, keyboard interaction, native semantics, accessible names/states,
  live updates, and screen-reader checks.
- Repeated mount/update/crash/replace/unmount cycles return node, listener,
  observer, timer, buffer, and handle counts to baseline.

## Principal risks

A generic style or attribute escape recreates DOM authority. Asynchronous
rendering can corrupt focus and text input even when visual output looks right.
Large batches can freeze the page. Browser discard can prevent cleanup code.
Accessibility regressions may not appear in DOM snapshots or automated tests.

## Sources

[^rendering]: W3C, WHATWG, and WebAssembly Community Group, [Trusted Types, CSP, SRI, HTML, and WAI-ARIA evidence](../../30-sources/browser-executable-integrity-and-rendering-standards-2026.md).
[^lifecycle]: WHATWG, W3C, and WICG, [browser lifecycle standards](../../30-sources/browser-platform-lifecycle-and-capability-standards-2026.md).
