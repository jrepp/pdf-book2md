from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pdf_extract_cli.chapters import sanitize_filename, split_into_chapters


class ChapterSplitTests(unittest.TestCase):
    def test_split_writes_frontmatter_and_chapters(self) -> None:
        markdown = """# _Sample Manual_

Intro text.

## **Chapter 1. Overview**
First chapter.

## **Chapter 2. Setup**
Second chapter.

## **Appendix A. Reference**
Appendix.
"""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            created = split_into_chapters(markdown, output_dir)
            names = [path.name for path in created]
            self.assertEqual(names[0], "00_frontmatter.md")
            self.assertIn("01_Chapter_1_Overview.md", names)
            self.assertIn("02_Chapter_2_Setup.md", names)
            self.assertIn("03_Appendix_A_Reference.md", names)

    def test_split_falls_back_to_full_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            created = split_into_chapters("plain text", output_dir)
            self.assertEqual([path.name for path in created], ["full_document.md"])

    def test_sanitize_filename_has_fallback(self) -> None:
        self.assertEqual(sanitize_filename("!!!"), "section")
