"""Turn a PDF file into plain text."""

from pathlib import Path

import pdfplumber


def pdf_to_text(path: str | Path) -> str:
    """Return the text of every page, joined with blank lines."""
    with pdfplumber.open(path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n\n".join(pages).strip()