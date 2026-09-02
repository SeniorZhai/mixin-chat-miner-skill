#!/usr/bin/env bash
set -euo pipefail

skill_dir="$(cd "$(dirname "$0")/.." && pwd -P)"
export PYTHONPATH="$skill_dir/src${PYTHONPATH:+:$PYTHONPATH}"

usage() {
  printf 'Usage: %s [db-check|interactive|snapshots|latest|help]\n' "$(basename "$0")" >&2
}

command_name="${1:-interactive}"

case "$command_name" in
  db-check)
    python3 - <<'PY'
from mixin_chat_miner.db import get_database_path

try:
    get_database_path()
except FileNotFoundError:
    print("missing")
    raise SystemExit(1)
print("available")
PY
    ;;
  interactive|cli)
    exec python3 -m mixin_chat_miner.cli
    ;;
  snapshots|latest)
    snapshot_dir="$(python3 - <<'PY'
from mixin_chat_miner.snapshot import get_snapshot_dir
print(get_snapshot_dir())
PY
)"
    if [[ ! -d "$snapshot_dir" ]]; then
      printf 'No snapshots found.\n' >&2
      exit 1
    fi
    if [[ "$command_name" == "snapshots" ]]; then
      find "$snapshot_dir" -maxdepth 1 -type f -name 'snapshot-*.jsonl' -exec basename {} \; | sort
      exit 0
    fi
    latest_file="$(find "$snapshot_dir" -maxdepth 1 -type f -name 'snapshot-*.jsonl' -print | sort | tail -n 1)"
    if [[ -z "$latest_file" ]]; then
      printf 'No snapshots found.\n' >&2
      exit 1
    fi
    basename "$latest_file"
    printf 'records=%s\n' "$(wc -l < "$latest_file" | tr -d ' ')"
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    usage
    exit 2
    ;;
esac
