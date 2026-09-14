# ERTS WebAssembly

This repository contains a research program for a first-party browser
WebAssembly port of upstream Erlang/OTP ERTS.

The complete research corpus, including its maps, notes, sources, inquiries,
journals, templates, metadata schema, and validation tools, lives under
[`research/`](research/README.md). Repository-wide working conventions are in
[`AGENTS.md`](AGENTS.md).

Start with the [research home map](research/10-maps/home.md).

## Validate the corpus

From the repository root:

```bash
python3 -m pip install -r research/requirements-validation.txt
python3 research/70-tools/check_all.py
```
