# Repository instructions

These instructions apply to the entire repository. This is a Markdown research
archive, not an implementation repository. Preserve exploratory work while
keeping provenance, navigation, security assumptions, and structure reliable.

## Project goal

Research a first-party WebAssembly port of upstream Erlang/OTP ERTS and a
version-matched OTP profile. Prefer a small, reviewable platform layer over a
new BEAM implementation or broad POSIX emulation. Treat browser deployment,
Worker topology, lifecycle, compatibility, supply-chain maintenance, and
security as equal parts of feasibility.

The Popcorn stack is explicitly outside scope: do not inspect, cite, compare,
or use it as evidence. This exclusion does not prevent studying upstream ERTS,
OTP, Elixir, WebAssembly standards, browser APIs, Emscripten, operating-system
interfaces, or relevant scientific literature.

Security is a day-one property. Keep host authority deny-by-default; distinguish
Wasm containment from memory safety; treat external data as hostile; preserve
loader, capability, quota, Worker isolation, teardown, update, reproducibility,
SBOM, provenance, and fuzzing requirements in every relevant proposal.

## Archive principles

- Folders describe document roles; maps, links, and tags describe subjects.
- Separate source claims, local evidence, synthesis, proposed architecture, and
  unresolved assumptions.
- Directory READMEs are exhaustive inventories; maps are selective.
- `frontmatter.schema.json` is the metadata authority.
- Change a document and every affected index, map, and local link together.
- Record exact versions, revisions, commands, dates, negative findings, and
  limitations for fast-moving software and standards.

## Canonical structure

```text
00-inbox/       Unprocessed captures
10-maps/        Curated conceptual navigation
20-notes/       Synthesis and architecture reasoning
30-sources/     Source and bibliographic notes
40-inquiries/   Open research questions
50-journal/     Dated research and experiment evidence
60-planning/    Phased implementation plans and gates
70-tools/       Corpus validators and tests
90-archive/     Superseded material retained for provenance
assets/         Attachments, datasets, and generated evidence
templates/      Document and directory scaffolds
```

Do not add or rename a top-level directory without a demonstrated need.

## Directory and metadata invariants

Every archive directory contains a `README.md` made from
`templates/directory-readme.md`. It uses `kind: map`, contains `Purpose`,
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

Implementation planning belongs in `60-planning/` and must retain unchecked
gates until executable evidence exists. A successful build, boot, or visual
demo alone does not establish semantic compatibility, security, lifecycle
cleanup, performance, or maintainability.

## Verification

Before reporting corpus work complete:

1. preserve unrelated changes;
2. run `python3 70-tools/validate_archive.py`;
3. run `python3 -m unittest discover -s 70-tools -p 'test_validate_archive.py'`;
4. verify new external citations against primary sources;
5. run `git diff --check` when a Git worktree exists; and
6. inspect the complete change for stale paths and accidental rewrites.
