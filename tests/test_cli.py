from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pdf_extract_cli.cli import main
from pdf_extract_cli.core import BatchResult, ExtractionResult


class CliTests(unittest.TestCase):
    def test_help_includes_quick_start(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                main(["--help"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("quick start:", stdout.getvalue())
        self.assertIn("pdf-book2md extract", stdout.getvalue())

    def test_extract_json_prints_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pdf_path = tmp_path / "demo.pdf"
            output_dir = tmp_path / "out"
            result = ExtractionResult(
                pdf_path=pdf_path,
                output_dir=output_dir,
                chapter_count=1,
                total_chars=12,
                files=[output_dir / "full_document.md"],
                full_document_path=output_dir / "full_document.md",
                title=None,
            )

            stdout = io.StringIO()
            with patch("pdf_extract_cli.cli.extract_pdf", return_value=result):
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(
                        ["extract", str(pdf_path), "--output-dir", str(output_dir), "--json"]
                    )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["pdf_path"], str(pdf_path))
            self.assertEqual(payload["chapter_count"], 1)

    def test_batch_text_summary_includes_skipped_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = BatchResult(
                input_dir=tmp_path / "pdfs",
                output_root=tmp_path / "out",
                processed=[],
                skipped=[tmp_path / "pdfs" / "done.pdf"],
            )

            stdout = io.StringIO()
            with patch("pdf_extract_cli.cli.batch_extract", return_value=result):
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(
                        ["batch", str(result.input_dir), "--output-root", str(result.output_root)]
                    )

            self.assertEqual(exit_code, 0)
            self.assertIn("processed 0 PDF(s)", stdout.getvalue())
            self.assertIn("skipped 1 existing", stdout.getvalue())

    def test_runtime_errors_return_one_and_print_stderr(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = main(["extract", "missing.pdf", "--output-dir", "out"])

        self.assertEqual(exit_code, 1)
        self.assertIn("error: PDF not found:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
