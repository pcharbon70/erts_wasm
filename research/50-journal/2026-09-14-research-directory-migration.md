---
title: "2026-09-14 — Research directory migration"
kind: journal
created: "2026-09-14"
tags:
  - archive-maintenance
  - migration
  - repository-structure
  - validation
aliases: []
---

# 2026-09-14 — Research directory migration

## Objective

Move the complete research corpus below one repository-level `research/`
directory so future runtime implementation, build, and integration files can
coexist without mixing roles with the archive.

## Scope

The migration moved the archive README, numbered directories, `assets/`,
`templates/`, frontmatter schema, validation requirements, and validation tools
without changing the relative arrangement inside the corpus. Root-level
`AGENTS.md` and `.gitignore` remain repository-wide. A short root `README.md`
now directs readers and validation commands into `research/`.

## Path contract

- Repository root: `/home/ducky/code/erts_wasm`
- Research root: `/home/ducky/code/erts_wasm/research`
- Corpus validator: `research/70-tools/validate_archive.py`
- All-checks runner: `research/70-tools/check_all.py`
- Metadata schema: `research/frontmatter.schema.json`
- Validation dependencies: `research/requirements-validation.txt`

Internal Markdown links required no prefix changes because the archive's
relative directory layout was preserved. Repository-root documentation,
commands, and Python path helpers were updated explicitly.

## Verification

Run from the repository root:

```bash
python3 research/70-tools/validate_archive.py
python3 -m unittest discover -s research/70-tools -p 'test_validate_archive.py'
python3 research/70-tools/check_all.py
git diff --check
```

Observed final results:

```text
Archive validation passed: 38 completed documents, 13 directories, 225 local links, and 15 source notes checked.
Ran 11 tests
OK
```

The bounded all-checks runner and `git diff --check` also completed
successfully.

## Related work

- [Research home](../10-maps/home.md)
- [Corpus recovery and migration](2026-09-14-corpus-recovery-and-migration.md)
- [Research tooling](../70-tools/README.md)
