# pdf-book2md

`pdf-book2md` turns PDF books and manuals into cleaned Markdown organized as
chapter files. It is built for long-form, structured PDFs where you want a
repeatable output tree for reading, search, indexing, or downstream processing.

## Quick Start

Install from PyPI:

```bash
python -m pip install pdf-book2md
```

Extract one book:

```bash
pdf-book2md extract ./manual.pdf --output-dir ./out/manual/chapters
```

Batch-process a directory:

```bash
pdf-book2md batch ./pdfs --output-root ./out
```

## What It Produces

When chapter headings are detected, `pdf-book2md` writes numbered chapter files
and preserves the source text as `full_document.md`:

```text
out/
  manual/
    chapters/
      00_frontmatter.md
      01_Chapter_1_Overview.md
      02_Chapter_2_Setup.md
      03_Appendix_A_Reference.md
      full_document.md
```

If no chapter split is detected, the command writes a single `full_document.md`.

## Features

- Extract one PDF into cleaned Markdown.
- Batch-process PDFs into per-document output directories.
- Split book/manual-style documents into deterministic chapter files.
- Preserve frontmatter separately when introductory material exists before the
  first detected chapter.
- Skip already-processed batch outputs unless `--force` is supplied.
- Print JSON summaries for automation with `--json`.
- Lazy-load `pymupdf4llm`, so tests and CLI help work without the runtime
  extraction dependency installed.

## Usage

### Single PDF

```bash
pdf-book2md extract ./manual.pdf --output-dir ./out/manual/chapters
```

Use `--skip-full-document` when you only want chapter files and do not need the
combined Markdown copy:

```bash
pdf-book2md extract ./manual.pdf --output-dir ./out/manual/chapters --skip-full-document
```

### Batch Directory

```bash
pdf-book2md batch ./pdfs --output-root ./out
```

Batch mode writes each input PDF under `OUTPUT_ROOT/<pdf-stem>/chapters/`.
Existing outputs are skipped when the target `chapters/` directory already
contains Markdown files.

Reprocess existing outputs:

```bash
pdf-book2md batch ./pdfs --output-root ./out --force
```

Select PDFs with a custom glob:

```bash
pdf-book2md batch ./pdfs --output-root ./out --pattern "*guide*.pdf"
```

### JSON Output

```bash
pdf-book2md batch ./pdfs --output-root ./out --json
```

The JSON summary includes absolute input and output paths, processed documents,
and skipped documents:

```json
{
  "input_dir": "/path/to/pdfs",
  "output_root": "/path/to/out",
  "processed": [],
  "skipped": ["/path/to/pdfs/manual.pdf"]
}
```

Common runtime failures are printed to stderr as `error: ...` and exit with
status code `1`. Argument parsing errors exit with status code `2`.

## Library API

```python
from pathlib import Path

from pdf_extract_cli import extract_pdf

result = extract_pdf(Path("manual.pdf"), Path("out/manual/chapters"))
print(result.chapter_count)
```

## Development

Install from source:

```bash
python3 -m pip install -e . --no-deps
```

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Smoke-test the CLI:

```bash
pdf-book2md --help
```

Releases are managed with Python Semantic Release. Conventional commits on
`main` determine whether a release is created; release builds publish to PyPI
using trusted publishing for `.github/workflows/release.yml` on the `main`
branch.
