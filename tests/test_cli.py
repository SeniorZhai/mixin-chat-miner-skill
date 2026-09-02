import unittest

from mixin_chat_miner.cli import terminal_text


class TerminalTextTest(unittest.TestCase):
    def test_control_characters_are_escaped(self):
        value = "中文\x1b]52;clipboard\x07\nline\r\u202esecret"
        rendered = terminal_text(value)
        self.assertTrue(rendered.startswith("中文"))
        self.assertNotIn("\x1b", rendered)
        self.assertNotIn("\n", rendered)
        self.assertNotIn("\r", rendered)
        self.assertNotIn("\u202e", rendered)
        self.assertIn("\\x1b", rendered)
        self.assertIn("\\u202e", rendered)


if __name__ == "__main__":
    unittest.main()
