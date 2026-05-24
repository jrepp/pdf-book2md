from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .core import batch_extract, extract_pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract PDFs into cleaned Markdown files",
        epilog=(
            "quick start:\n"
            "  pdf-book2md extract ./manual.pdf --output-dir ./out/manual/chapters\n"
            "  pdf-book2md batch ./pdfs --output-root ./out --json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract one PDF",
        description="Extract one PDF into cleaned Markdown and chapter files.",
    )
    extract_parser.add_argument("pdf", type=Path, help="Input PDF path")
    extract_parser.add_argument("--output-dir", type=Path, required=True, help="Output directory")
    extract_parser.add_argument(
        "--skip-full-document",
        action="store_true",
        help="Do not write full_document.md when chapters are detected",
    )
    extract_parser.add_argument("--json", action="store_true", help="Print JSON summary")

    batch_parser = subparsers.add_parser(
        "batch",
        help="Extract all PDFs in a directory",
        description="Extract matching PDFs in a directory into per-document output folders.",
    )
    batch_parser.add_argument("input_dir", type=Path, help="Directory containing PDFs")
    batch_parser.add_argument("--output-root", type=Path, required=True, help="Root output directory")
    batch_parser.add_argument("--pattern", default="*.pdf", help="Glob for selecting PDFs")
    batch_parser.add_argument(
        "--force",
        action="store_true",
        help="Re-process documents even if markdown already exists",
    )
    batch_parser.add_argument("--json", action="store_true", help="Print JSON summary")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "extract":
            result = extract_pdf(
                args.pdf,
                args.output_dir,
                write_full_document=not args.skip_full_document,
            )
            _emit(
                args.json,
                result.to_dict(),
                f"extracted {result.pdf_path} -> {result.output_dir}",
            )
            return 0

        if args.command == "batch":
            result = batch_extract(
                args.input_dir,
                args.output_root,
                pattern=args.pattern,
                force=args.force,
            )
            skipped = f", skipped {len(result.skipped)} existing" if result.skipped else ""
            _emit(
                args.json,
                result.to_dict(),
                f"processed {len(result.processed)} PDF(s) from {result.input_dir}{skipped}",
            )
            return 0
    except (FileNotFoundError, NotADirectoryError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


def _emit(as_json: bool, payload: dict[str, object], message: str) -> None:
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(message)


if __name__ == "__main__":
    raise SystemExit(main())
