# Instructions for AI coding agents

Read this file before modifying Mixin Chat Miner.

## Goal and boundaries

This repository contains a host-neutral Agent Skill and its bundled CLI. It exports a small, user-selected chat snapshot from the local Mixin Desktop SQLite database. Preserve these boundaries:

- Open the source database in read-only mode.
- Keep all processing local unless the user explicitly requests an external service.
- Never inspect, print, commit, or upload real snapshots or database files.
- Keep snapshot fields limited to those already defined in `snapshot.py` unless the user approves a privacy expansion.
- Treat conversation names, sender names, message text, account IDs, paths, and database contents as private data.

## Initialize

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

The runtime requires Python 3.9+, macOS, and a locally synced Mixin Desktop database. No API key or third-party runtime dependency is required. `MIXIN_CHAT_DB_PATH` may point to a specific `mixin.db`; otherwise the CLI accepts exactly one database under the standard Mixin Desktop data directory.

## Project map

- `SKILL.md`: host-neutral operational instructions loaded by an Agent.
- `scripts/run_miner.sh`: privacy-safe helper used by the Skill.
- `src/mixin_chat_miner/cli.py`: interactive flow and terminal output.
- `src/mixin_chat_miner/db.py`: database discovery and read-only queries.
- `src/mixin_chat_miner/snapshot.py`: JSONL snapshot creation.
- `bin/mixin-chat-miner`: repository-local launcher.
- `tests/`: standard-library tests.

## Change workflow

1. Read every touched module and find all callers before editing shared behavior.
2. Reuse the standard library and existing helpers; add no dependency without user approval.
3. Make the smallest focused change and preserve the read-only and local-data boundaries.
4. Run the smallest relevant check. For general changes, run:

```bash
python -m unittest discover -s tests
python -m compileall -q src
```

5. Report changed files and any validation that could not be run.

Keep code and comments in English. Avoid comments unless the logic is genuinely non-obvious. Do not commit or push unless the user asks.
