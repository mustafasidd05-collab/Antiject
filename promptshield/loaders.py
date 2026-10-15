"""
Document Loaders for PromptShield (txt, pdf, html, md).
Extracts raw content from various file formats for inspection.
"""

import os
from pathlib import Path
from typing import Optional

def load_text(path: str) -> str:
    """Reads a text or markdown file."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def load_pdf(path: str) -> str:
    """Extracts text from all pages of a PDF document using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("pypdf is required to load PDF files. Install via: pip install pypdf")

    reader = PdfReader(path)
    pages = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append(text)
    return "\n\n".join(pages)

def load_html(path: str) -> str:
    """
    Extracts text from an HTML file using BeautifulSoup.
    Preserves raw HTML comments and hidden elements so hidden injections can be detected.
    """
    try:
        from bs4 import BeautifulSoup, Comment
    except ImportError:
        raise ImportError("beautifulsoup4 is required to load HTML files. Install via: pip install beautifulsoup4")

    raw_html = load_text(path)
    soup = BeautifulSoup(raw_html, "html.parser")

    # Extract comments so Layer 1 HTML comment detector sees them
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    comment_text = "\n".join(f"<!--{c}-->" for c in comments)

    # Extract text from visible elements
    body_text = soup.get_text(separator="\n", strip=True)

    if comment_text:
        return f"{comment_text}\n\n{body_text}"
    return body_text

def load_file(path: str) -> str:
    """
    Automatically detects file extension and loads text content.
    Supports .txt, .md, .pdf, .html, .htm, .json, .csv.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return load_pdf(path)
    elif ext in (".html", ".htm"):
        return load_html(path)
    elif ext in (".txt", ".md", ".json", ".csv", ".log", ".yaml", ".yml"):
        return load_text(path)
    else:
        # Default fallback to text reader
        return load_text(path)
