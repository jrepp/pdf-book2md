from __future__ import annotations

import re


def clean_markdown(text: str) -> str:
    """Normalize common PDF-to-Markdown artifacts."""
    text = re.sub(r"\n*©.*?IBM Corp\..*?\n*", "\n", text)
    text = re.sub(r"\n\s*\*\*\d+\*\*\s*\n", "\n", text)
    text = re.sub(r"\n(Chapter|Appendix|Part) [^\n]+ \*\*\d+\*\*\n", "\n", text)
    text = re.sub(r"\n\s{2,}[-•]\s", "\n- ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"([a-z,])\n([a-z])", r"\1 \2", text)
    text = re.sub(r"([a-z])\n(\([A-Z])", r"\1 \2", text)
    text = re.sub(r"(\d)\)\n([a-z])", r"\1) \2", text)
    return text.strip()
