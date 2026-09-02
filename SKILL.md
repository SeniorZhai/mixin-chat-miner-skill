---
name: mixin-chat-miner
description: Extract and analyze focused local Mixin Desktop chat snapshots when the user asks to search conversations, inspect message history, build a timeline, or summarize a topic.
---

# Mixin Chat Miner

Use the bundled CLI to query the user's local Mixin Desktop database in read-only mode and create a bounded JSONL snapshot.

## Privacy

- Treat messages, names, query terms, database paths, IDs, and snapshots as private.
- Keep processing in the active agent environment. Use another service only with explicit user approval.
- Report counts, filters, time ranges, and high-level findings by default. Quote messages only when the user requests exact excerpts.
- Never put database or snapshot data in commits, issues, pull requests, documentation, or logs.
- Leave existing snapshots untouched unless the user asks to remove or rewrite them.

## Initialize

The skill requires macOS, Python 3.9+, a locally synced Mixin Desktop database, and permission to read the Mixin application container. It has no third-party runtime dependency or API key.

Run from the skill directory:

```bash
scripts/run_miner.sh db-check
```

If more than one local account exists, set `MIXIN_CHAT_DB_PATH` to the intended `mixin.db`. Set `MIXIN_CHAT_SNAPSHOT_DIR` only when the user wants a non-default private output directory.

## Workflow

1. Establish the conversation, keyword or topic, time range, maximum message count, and whether the user wants a new export or analysis of an existing snapshot.
2. Run `scripts/run_miner.sh db-check`. Stop and explain the local prerequisite when it reports `missing`.
3. Run `scripts/run_miner.sh interactive` in an interactive terminal to create a focused snapshot.
4. Run `scripts/run_miner.sh latest` to obtain its opaque filename and record count without printing message text.
5. Parse the JSONL locally and answer the requested question. Preserve the reverse-chronological ordering when sequence matters, or sort by `created_at` explicitly.

Use `scripts/run_miner.sh snapshots` to list snapshot filenames. Each record contains `conversation_name`, `sender_name`, `created_at`, `category`, and `content`.

Do not query the full database or broaden the requested filters merely to avoid the interactive workflow.
