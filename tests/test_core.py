from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pdf_extract_cli.core import batch_extract, extract_pdf


def fake_extractor(_: Path) -> str:
    return """# _Demo Manual_

Intro.

## **Chapter 1. Start**
Hello.

## **Chapter 2. Continue**
World.

## **Appendix A. End**
Done.
"""


class CoreTests(unittest.TestCase):
    def test_extract_pdf_writes_full_document_and_chapters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pdf_path = tmp_path / "demo.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 demo")
            output_dir = tmp_path / "out"

            result = extract_pdf(pdf_path, output_dir, extractor=fake_extractor)

            self.assertEqual(result.chapter_count, 4)
            self.assertIsNotNone(result.full_document_path)
            self.assertTrue((output_dir / "full_document.md").exists())
            self.assertEqual(result.title, "Demo Manual")

    def test_batch_extract_processes_matching_pdfs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_dir = tmp_path / "pdfs"
            input_dir.mkdir()
            (input_dir / "a.pdf").write_bytes(b"%PDF-1.4 a")
            (input_dir / "b.pdf").write_bytes(b"%PDF-1.4 b")
            (input_dir / "ignore.txt").write_text("nope", encoding="utf-8")

            result = batch_extract(input_dir, tmp_path / "out", extractor=fake_extractor)

            self.assertEqual(len(result.processed), 2)
            self.assertTrue((tmp_path / "out" / "a" / "chapters").exists())
            self.assertTrue((tmp_path / "out" / "b" / "chapters").exists())
            self.assertEqual(result.skipped, [])

    def test_batch_extract_reports_skipped_existing_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_dir = tmp_path / "pdfs"
            input_dir.mkdir()
            pdf_path = input_dir / "a.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 a")
            target_dir = tmp_path / "out" / "a" / "chapters"
            target_dir.mkdir(parents=True)
            (target_dir / "full_document.md").write_text("done", encoding="utf-8")

            result = batch_extract(input_dir, tmp_path / "out", extractor=fake_extractor)

            self.assertEqual(result.processed, [])
            self.assertEqual(result.skipped, [pdf_path.resolve()])

    def test_extract_pdf_rejects_non_pdf_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            text_path = tmp_path / "demo.txt"
            text_path.write_text("not a pdf", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "must end in .pdf"):
                extract_pdf(text_path, tmp_path / "out", extractor=fake_extractor)
