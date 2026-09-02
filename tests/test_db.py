import os
import sqlite3
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from mixin_chat_miner import db


class DatabaseTest(unittest.TestCase):
    def test_like_pattern_treats_wildcards_as_text(self):
        self.assertEqual(db._like_pattern(r"50%_\done"), r"%50\%\_\\done%")

        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.executescript(
            """
            CREATE TABLE conversations (conversation_id TEXT, name TEXT);
            CREATE TABLE messages (
                message_id TEXT, conversation_id TEXT, user_id TEXT,
                category TEXT, content TEXT, created_at INTEGER
            );
            CREATE TABLE users (user_id TEXT, full_name TEXT);
            INSERT INTO conversations VALUES ('literal', '50%_done'), ('wildcard', '500Xdone');
            INSERT INTO messages VALUES ('one', 'literal', NULL, 'TEXT', '50%_done', 1);
            """
        )
        self.assertEqual(db.search_conversations(connection, "50%_done")[0]["conversation_id"], "literal")
        self.assertEqual(len(db.get_messages(connection, "literal", keyword="50%_done")), 1)
        connection.close()

    def test_timestamp_conversion(self):
        value = "2026-09-02 12:34:56"
        expected = int(datetime.strptime(value, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
        self.assertEqual(db._timestamp_milliseconds(value), expected)
        self.assertEqual(db._timestamp_milliseconds("123"), 123)
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD HH:MM:SS"):
            db._timestamp_milliseconds("September 2")

    def test_auto_discovery_and_read_only_connection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "account" / "mixin.db"
            database.parent.mkdir()
            with sqlite3.connect(database) as connection:
                connection.execute("CREATE TABLE example (value TEXT)")

            with patch.object(db, "DB_ROOT", root), patch.dict(
                os.environ, {db.DB_PATH_ENV: ""}
            ):
                self.assertEqual(db.get_database_path(), database)
                connection = db.get_connection()
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM example").fetchone()[0], 0)
                with self.assertRaises(sqlite3.OperationalError):
                    connection.execute("INSERT INTO example VALUES ('write')")
                connection.close()

    def test_environment_override(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "mixin.db"
            database.touch()
            with patch.dict(os.environ, {db.DB_PATH_ENV: str(database)}):
                self.assertEqual(db.get_database_path(), database)

    def test_missing_override_does_not_echo_private_path(self):
        private_path = "/private/account-id/mixin.db"
        with patch.dict(os.environ, {db.DB_PATH_ENV: private_path}):
            with self.assertRaises(FileNotFoundError) as error:
                db.get_database_path()
        self.assertNotIn(private_path, str(error.exception))

    def test_multiple_databases_require_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for account in ("one", "two"):
                path = root / account / "mixin.db"
                path.parent.mkdir()
                path.touch()
            with patch.object(db, "DB_ROOT", root), patch.dict(
                os.environ, {db.DB_PATH_ENV: ""}
            ):
                with self.assertRaisesRegex(FileNotFoundError, db.DB_PATH_ENV):
                    db.get_database_path()


if __name__ == "__main__":
    unittest.main()
