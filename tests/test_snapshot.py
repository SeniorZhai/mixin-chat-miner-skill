import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mixin_chat_miner import snapshot


class SnapshotTest(unittest.TestCase):
    def test_snapshot_is_private_and_uses_opaque_filename(self):
        messages = [{"conversation_name": "private group", "sender_name": "Alice", "content": "secret"}]
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {snapshot.SNAPSHOT_DIR_ENV: str(Path(directory) / "snapshots")}
        ):
            filename = snapshot.generate_snapshot_filename()
            path = snapshot.save_snapshot(messages, filename)
            self.assertTrue(filename.startswith("snapshot-"))
            self.assertNotIn("private", filename)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(path.read_text())["content"], "secret")


if __name__ == "__main__":
    unittest.main()
