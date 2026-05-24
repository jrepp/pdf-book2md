from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pdf_extract_cli.cleaning import clean_markdown


class CleanMarkdownTests(unittest.TestCase):
    def test_removes_known_footer_and_page_artifacts(self) -> None:
        text = "hello\n© 2024 IBM Corp. all rights\n\n**123**\n\n\nnext"
        result = clean_markdown(text)
        self.assertIn("hello", result)
        self.assertIn("next", result)
        self.assertNotIn("IBM Corp", result)
        self.assertNotIn("**123**", result)

    def test_joins_broken_sentences(self) -> None:
        text = "alpha\nbeta\nline\n(A\n1)\nfoo"
        result = clean_markdown(text)
        self.assertIn("alpha beta", result)
        self.assertIn("line (A", result)
        self.assertIn("1) foo", result)
