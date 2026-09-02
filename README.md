# Mixin Chat Miner Skill

[简体中文](README.zh-CN.md)

A portable Agent Skill and local CLI for exporting a focused subset of Mixin Desktop chat history to JSONL. It reads the source SQLite database in read-only mode and keeps the analysis workflow local.

The repository is not tied to a specific AI product. Any agent that can load a `SKILL.md` and run local shell commands can use it; other agents can be instructed to read [SKILL.md](SKILL.md) before starting.

## Requirements

- macOS with Mixin Messenger Desktop installed and chat history synced locally.
- Python 3.9 or newer.
- Bash for the bundled helper script.
- Read access to the Mixin Desktop application container.

No API key or third-party runtime dependency is required. If macOS denies access, grant the terminal or agent host the required Files and Folders or Full Disk Access permission in System Settings.

## Install as an Agent Skill

Clone the repository into the skill directory used by your agent host:

```bash
git clone https://github.com/SeniorZhai/mixin-chat-miner-skill.git \
  /path/to/your-agent/skills/mixin-chat-miner
cd /path/to/your-agent/skills/mixin-chat-miner
./scripts/run_miner.sh db-check
```

Skill directories differ between agent products. Use the host's documented skill location or add this repository as a skill source. The only required skill entrypoint is `SKILL.md`.

## Initialize

The helper automatically discovers the database when exactly one account exists under the standard Mixin Desktop data directory. With multiple accounts, set the database explicitly:

```bash
export MIXIN_CHAT_DB_PATH="$HOME/Library/Containers/one.mixin.messenger.desktop/Data/Documents/<account-id>/mixin.db"
./scripts/run_miner.sh db-check
```

`available` means initialization is complete. The default private snapshot directory is:

```text
~/Library/Application Support/Mixin Chat Miner/snapshots
```

Override it only when needed:

```bash
export MIXIN_CHAT_SNAPSHOT_DIR="/path/to/private/snapshots"
```

## Use the skill

Ask the agent for a conversation, topic, time range, and maximum message count. The skill will use these commands:

```bash
./scripts/run_miner.sh interactive
./scripts/run_miner.sh snapshots
./scripts/run_miner.sh latest
```

`latest` prints only the opaque filename and record count, not message text.

## Use the CLI directly

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
mixin-chat-miner
```

The repository launcher also works without installation:

```bash
./bin/mixin-chat-miner
```

## Privacy and safety

- The Mixin database is opened with SQLite `mode=ro`.
- Snapshots use an owner-only directory (`0700`) and files (`0600`).
- Snapshot filenames do not contain conversation names or query terms.
- The CLI does not print message previews or Python tracebacks.
- The tool makes no network requests and copies no attachments.
- Snapshots still contain message text and display names. Do not commit, archive, upload, or share them without reviewing the contents and recipient.

Using the skill through a hosted agent may send snapshot content to that agent provider. Use an environment whose data handling you accept; the CLI itself never uploads data.

## Development

```bash
python -m unittest discover -s tests
python -m compileall -q src tests
bash -n scripts/run_miner.sh
```

AI coding agents modifying this repository should also read [AI.md](AI.md).

## Current limitations

- Only the current macOS Mixin Desktop database layout is supported.
- Keyword matching uses SQLite `LIKE`, not semantic search.
- Snapshots are one-time exports, not backups or incremental syncs.
- Message content is exported as stored; media files are not copied.

## License

[MIT](LICENSE)
