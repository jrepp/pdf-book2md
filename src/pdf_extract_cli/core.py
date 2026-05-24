from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

from .chapters import extract_title_from_frontmatter, split_into_chapters
from .cleaning import clean_markdown

Extractor = Callable[[Path], str]


@dataclass(slots=True)
class ExtractionResult:
    pdf_path: Path
    output_dir: Path
    chapter_count: int
    total_chars: int
    files: list[Path]
    full_document_path: Path | None
    title: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["pdf_path"] = str(self.pdf_path)
        payload["output_dir"] = str(self.output_dir)
        payload["files"] = [str(path) for path in self.files]
        payload["full_document_path"] = (
            str(self.full_document_path) if self.full_document_path else None
        )
        return payload


@dataclass(slots=True)
class BatchResult:
    input_dir: Path
    output_root: Path
    processed: list[ExtractionResult]
    skipped: list[Path] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "input_dir": str(self.input_dir),
            "output_root": str(self.output_root),
            "processed": [item.to_dict() for item in self.processed],
            "skipped": [str(path) for path in self.skipped],
        }


def extract_pdf(
    pdf_path: Path,
    output_dir: Path,
    *,
    extractor: Extractor | None = None,
    write_full_document: bool = True,
) -> ExtractionResult:
    pdf_path = pdf_path.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if not pdf_path.is_file():
        raise ValueError(f"PDF path is not a file: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Input path must end in .pdf: {pdf_path}")

    markdown_content = (extractor or default_extractor)(pdf_path)
    markdown_content = clean_markdown(markdown_content)
    chapter_files = split_into_chapters(markdown_content, output_dir)

    has_chapters = len(chapter_files) > 1 or (
        len(chapter_files) == 1 and chapter_files[0].name != "full_document.md"
    )
    full_document_path: Path | None = None
    if write_full_document and has_chapters:
        full_document_path = output_dir / "full_document.md"
        full_document_path.write_text(markdown_content, encoding="utf-8")
    elif chapter_files and chapter_files[0].name == "full_document.md":
        full_document_path = chapter_files[0]

    return ExtractionResult(
        pdf_path=pdf_path,
        output_dir=output_dir,
        chapter_count=len(chapter_files),
        total_chars=len(markdown_content),
        files=chapter_files,
        full_document_path=full_document_path,
        title=extract_title_from_frontmatter(output_dir),
    )


def batch_extract(
    input_dir: Path,
    output_root: Path,
    *,
    pattern: str = "*.pdf",
    extractor: Extractor | None = None,
    force: bool = False,
) -> BatchResult:
    input_dir = input_dir.expanduser().resolve()
    output_root = output_root.expanduser().resolve()
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    processed: list[ExtractionResult] = []
    skipped: list[Path] = []
    for pdf_path in sorted(input_dir.glob(pattern)):
        if pdf_path.suffix.lower() != ".pdf":
            continue
        target_dir = output_root / pdf_path.stem / "chapters"
        already_processed = target_dir.exists() and any(target_dir.glob("*.md"))
        if already_processed and not force:
            skipped.append(pdf_path)
            continue
        processed.append(extract_pdf(pdf_path, target_dir, extractor=extractor))
    return BatchResult(
        input_dir=input_dir,
        output_root=output_root,
        processed=processed,
        skipped=skipped,
    )


def default_extractor(pdf_path: Path) -> str:
    try:
        import pymupdf4llm
    except ImportError as exc:
        raise RuntimeError(
            "pymupdf4llm is required for runtime extraction. Install the package dependencies first."
        ) from exc

    return pymupdf4llm.to_markdown(
        str(pdf_path),
        ignore_images=True,
        ignore_graphics=True,
        table_strategy="lines_strict",
        margins=40,
        fontsize_limit=5,
    )
