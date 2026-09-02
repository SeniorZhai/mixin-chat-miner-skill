import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH_ENV = "MIXIN_CHAT_DB_PATH"
DB_ROOT = Path.home() / "Library/Containers/one.mixin.messenger.desktop/Data/Documents"


def _like_pattern(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _timestamp_milliseconds(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError as error:
            raise ValueError(
                f"Invalid time '{value}'. Use YYYY-MM-DD HH:MM:SS."
            ) from error
        return int(parsed.timestamp() * 1000)


def get_database_path() -> Path:
    """Find the configured Mixin database."""
    configured_path = os.environ.get(DB_PATH_ENV)
    if configured_path:
        path = Path(configured_path).expanduser()
        if path.is_file():
            return path
        raise FileNotFoundError(f"Configured Mixin database not found. Check {DB_PATH_ENV}.")

    candidates = sorted(DB_ROOT.glob("*/mixin.db"))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise FileNotFoundError(f"No Mixin database found. Set {DB_PATH_ENV}.")
    raise FileNotFoundError(
        f"Multiple Mixin databases found. Set {DB_PATH_ENV}."
    )


def get_connection() -> sqlite3.Connection:
    """Get a read-only connection to the Mixin database."""
    db_path = get_database_path()
    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def list_conversations(conn: sqlite3.Connection, limit: int = 50) -> List[Dict[str, Any]]:
    """List conversations with message counts."""
    query = """
    SELECT
        c.conversation_id,
        c.name,
        COUNT(m.message_id) as message_count,
        MAX(m.created_at) as last_message_at
    FROM conversations c
    LEFT JOIN messages m ON c.conversation_id = m.conversation_id
    GROUP BY c.conversation_id
    HAVING message_count > 0
    ORDER BY last_message_at DESC
    LIMIT ?
    """
    cursor = conn.execute(query, (limit,))
    return [dict(row) for row in cursor.fetchall()]


def search_conversations(conn: sqlite3.Connection, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search conversations by name."""
    query = """
    SELECT
        c.conversation_id,
        c.name,
        COUNT(m.message_id) as message_count
    FROM conversations c
    LEFT JOIN messages m ON c.conversation_id = m.conversation_id
    WHERE c.name LIKE ? ESCAPE '\\'
    GROUP BY c.conversation_id
    ORDER BY message_count DESC
    LIMIT ?
    """
    cursor = conn.execute(query, (_like_pattern(keyword), limit))
    return [dict(row) for row in cursor.fetchall()]


def get_messages(
    conn: sqlite3.Connection,
    conversation_id: str,
    keyword: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Get messages for a conversation with optional filters."""

    # Base query
    query = """
    SELECT
        m.message_id,
        m.conversation_id,
        m.category,
        m.content,
        m.created_at,
        u.full_name as sender_name,
        c.name as conversation_name
    FROM messages m
    LEFT JOIN users u ON m.user_id = u.user_id
    LEFT JOIN conversations c ON m.conversation_id = c.conversation_id
    WHERE m.conversation_id = ?
    """
    params = [conversation_id]

    # Add keyword filter
    if keyword:
        query += " AND m.content LIKE ? ESCAPE '\\'"
        params.append(_like_pattern(keyword))

    # Add time filters
    if start_time:
        query += " AND m.created_at >= ?"
        params.append(_timestamp_milliseconds(start_time))

    if end_time:
        query += " AND m.created_at <= ?"
        params.append(_timestamp_milliseconds(end_time))

    # Order and limit
    query += " ORDER BY m.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor = conn.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]


def get_conversation_info(conn: sqlite3.Connection, conversation_id: str) -> Optional[Dict[str, Any]]:
    """Get conversation metadata."""
    query = """
    SELECT
        conversation_id,
        name,
        category,
        created_at
    FROM conversations
    WHERE conversation_id = ?
    """
    cursor = conn.execute(query, (conversation_id,))
    row = cursor.fetchone()
    return dict(row) if row else None
