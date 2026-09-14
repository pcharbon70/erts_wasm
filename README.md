# ERTS WebAssembly Research Archive

This standalone archive researches a first-party port of the official Erlang
Runtime System (ERTS) and a version-matched OTP subset to WebAssembly, with the
browser as the first execution host and security treated as a design input from
the first experiment.

The archive preserves the research originally developed in BlazeX while giving
the runtime investigation its own ownership, history, planning space, and
validation boundary. The excluded Popcorn stack is not part of this research
program or its evidence base.

Start at the [home map](10-maps/home.md). Repository-wide authoring and
maintenance conventions are defined in [AGENTS.md](AGENTS.md).

## Structure

- [00-inbox](00-inbox/README.md) — unprocessed captures.
- [10-maps](10-maps/README.md) — curated paths through the research.
- [20-notes](20-notes/README.md) — synthesis and architecture reasoning.
- [30-sources](30-sources/README.md) — bibliographic and evidence notes.
- [40-inquiries](40-inquiries/README.md) — open, falsifiable questions.
- [50-journal](50-journal/README.md) — dated research and experiment records.
- [60-planning](60-planning/README.md) — implementation plans and gates.
- [70-tools](70-tools/README.md) — corpus validators and tests.
- [90-archive](90-archive/README.md) — superseded material retained for provenance.
- [assets](assets/README.md) — durable attachments and generated evidence.
- [templates](templates/README.md) — document scaffolds.

## Research boundary

The central question is whether upstream ERTS can be cross-built as a secure,
maintainable browser WebAssembly runtime that boots matching OTP BEAM modules,
keeps execution off the UI thread, exposes only explicitly brokered browser
capabilities, and demonstrates bounded lifecycle and resource behavior.

Research conclusions are not implementation evidence. Cross-build, OTP boot,
browser conformance, teardown, performance, compatibility, and security claims
remain open until their defined experiments produce reproducible artifacts.

## Validation

Install the pinned dependencies and run:

```bash
python3 -m pip install -r requirements-validation.txt
python3 70-tools/check_all.py
```

The focused commands are:

```bash
python3 70-tools/validate_archive.py
python3 -m unittest discover -s 70-tools -p 'test_validate_archive.py'
```

## Archive files

- [AGENTS.md](AGENTS.md) — authoring, provenance, security, and maintenance rules.
- [frontmatter.schema.json](frontmatter.schema.json) — metadata schema.
- [requirements-validation.txt](requirements-validation.txt) — pinned validation dependencies.
