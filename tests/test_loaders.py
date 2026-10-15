"""
Unit tests for document loaders (txt, pdf, html).
"""

import os
import pytest
from promptshield.loaders import load_file, load_text, load_html

def test_load_text_file(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("Hello text content", encoding="utf-8")
    content = load_file(str(p))
    assert content == "Hello text content"

def test_load_html_file_with_comments(tmp_path):
    html_content = "<html><body><!-- secret comment directive --><h1>Title</h1></body></html>"
    p = tmp_path / "page.html"
    p.write_text(html_content, encoding="utf-8")
    extracted = load_file(str(p))
    # Must preserve the comment for inspection
    assert "<!-- secret comment directive -->" in extracted
    assert "Title" in extracted

def test_load_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        load_file("non_existent_file_12345.xyz")
