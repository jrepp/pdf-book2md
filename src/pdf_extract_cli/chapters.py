from __future__ import annotations

import re
from pathlib import Path


CHAPTER_PATTERNS = (
    re.compile(r"^#{2,6} \*\*(Part \d+|Chapter \d+|Appendix [A-Z])[.\s][^\n]*\*\*", re.MULTILINE),
    re.compile(r"^#{3,4} \*\*[A-Z][^\n]{5,60}\*\*$", re.MULTILINE),
    re.compile(r"^## \*\*[A-Z][^\n]{5,60}\*\*$", re.MULTILINE),
)


def split_into_chapters(markdown_content: str, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    matches = []
    for pattern in CHAPTER_PATTERNS:
        found = list(pattern.finditer(markdown_content))
        if 3 <= len(found) <= 100:
            matches = found
            break

    created_files: list[Path] = []
    if not matches:
        output_file = output_dir / "full_document.md"
        output_file.write_text(markdown_content, encoding="utf-8")
        return [output_file]

    if matches[0].start() > 0:
        frontmatter = markdown_content[: matches[0].start()].strip()
        if frontmatter:
            output_file = output_dir / "00_frontmatter.md"
            output_file.write_text(frontmatter, encoding="utf-8")
            created_files.append(output_file)

    for index, match in enumerate(matches, start=1):
        start = match.start()
        end = matches[index].start() if index < len(matches) else len(markdown_content)
        content = markdown_content[start:end].strip()
        title = _normalize_title(match.group(0).strip())
        output_file = output_dir / f"{index:02d}_{sanitize_filename(title)}.md"
        output_file.write_text(content, encoding="utf-8")
        created_files.append(output_file)

    return created_files


def extract_title_from_frontmatter(chapters_dir: Path) -> str | None:
    path = chapters_dir / "00_frontmatter.md"
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()[:20]
    pattern = re.compile(r"^#{1,5}\s+_(.+?)_\s*$")
    for line in lines:
        match = pattern.search(line.strip())
        if not match:
            continue
        candidate = match.group(1).replace("_ _", " ").replace("_", " ").strip()
        if candidate and candidate != "IBM Z and LinuxONE":
            return candidate
    return None


def sanitize_filename(title: str) -> str:
    filtered = "".join(
        ch for ch in title if ch.isalnum() or ch in {"_", "-"} or ch.isspace()
    )
    collapsed = re.sub(r"\s+", "_", filtered).strip("_")[:60]
    return collapsed or "section"


def _normalize_title(title: str) -> str:
    title = re.sub(r"^#{1,6}\s+\*\*", "", title)
    title = re.sub(r"\*\*$", "", title)
    return title.strip()
