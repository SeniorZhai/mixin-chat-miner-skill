import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

SNAPSHOT_DIR_ENV = "MIXIN_CHAT_SNAPSHOT_DIR"


def get_snapshot_dir() -> Path:
    configured_path = os.environ.get(SNAPSHOT_DIR_ENV)
    if configured_path:
        return Path(configured_path).expanduser()
    return Path.home() / "Library/Application Support/Mixin Chat Miner/snapshots"


def ensure_snapshot_dir():
    """Ensure the snapshots directory exists."""
    snapshot_dir = get_snapshot_dir()
    snapshot_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    snapshot_dir.chmod(0o700)
    return snapshot_dir


def generate_snapshot_filename() -> str:
    """Generate a snapshot filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    return f"snapshot-{timestamp}.jsonl"


def save_snapshot(messages: List[Dict[str, Any]], filename: str) -> Path:
    """Save messages to a JSONL snapshot file."""
    filepath = ensure_snapshot_dir() / filename
    descriptor = os.open(filepath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(descriptor, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as f:
        for msg in messages:
            snapshot_record = {
                "conversation_name": msg.get("conversation_name", ""),
                "sender_name": msg.get("sender_name", ""),
                "created_at": msg.get("created_at", ""),
                "category": msg.get("category", ""),
                "content": msg.get("content", "")
            }
            f.write(json.dumps(snapshot_record, ensure_ascii=False) + '\n')

    return filepath
