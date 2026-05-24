# pdf-book2md

`pdf-book2md` is a standalone installable Python CLI for turning PDF books and manuals into cleaned Markdown with structured chapter files.


## Features

- extract a single PDF book into Markdown
- batch-process a directory of PDFs
- preserve a deterministic cleanup pass for common PDF artifacts
- split large book/manual-style documents into numbered chapter files
- skip already-processed batch outputs unless `--force` is supplied
- print machine-readable JSON summaries for automation
- lazy-load `pymupdf4llm`, so tests and CLI help work without the runtime dependency installed

## Install

```bash
python -m pip install pdf-book2md
```

From source:

```bash
python3 -m pip install .
```

## Usage

### Single PDF

```bash
pdf-book2md extract ./manual.pdf --output-dir ./out/manual/chapters
```

If the document has detectable chapter headings, the command writes one file per
chapter plus `full_document.md`. If no chapter split is detected, it writes a
single `full_document.md`.

Use `--skip-full-document` when you only want chapter files:

```bash
pdf-book2md extract ./manual.pdf --output-dir ./out/manual/chapters --skip-full-document
```

### Batch directory

```bash
pdf-book2md batch ./pdfs --output-root ./out
```

This writes per-document outputs like:

```text
out/
  manual/
    chapters/
      00_frontmatter.md
      01_Chapter_1_Overview.md
      02_Chapter_2_Setup.md
      full_document.md
```

Batch mode skips PDFs that already have Markdown files under their target
`chapters/` directory. Reprocess everything with:

```bash
pdf-book2md batch ./pdfs --output-root ./out --force
```

### JSON summary

```bash
pdf-book2md batch ./pdfs --output-root ./out --json
```

JSON output includes absolute input and output paths, processed documents, and
skipped documents:

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

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Editable install smoke test:

```bash
python3 -m pip install -e . --no-deps
pdf-book2md --help
```
