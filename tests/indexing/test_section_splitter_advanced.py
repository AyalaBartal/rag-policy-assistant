"""Advanced unit tests for the section splitter using synthetic markdown."""
from __future__ import annotations

from src.indexing.section_splitter import split_markdown_into_sections


def test_no_headings_returns_document_section():
    md = "Just some plain text with no headings."
    sections = split_markdown_into_sections(md)
    assert len(sections) >= 1
    paths = [s[0] for s in sections]
    assert "Document" in paths


def test_single_h1_section_path():
    md = "# Return Policy\n\nContent here"
    sections = split_markdown_into_sections(md)
    paths = [s[0] for s in sections]
    assert "Return Policy" in paths


def test_nested_headings_produce_path():
    md = "# H1 Title\n\nSome content\n\n## H2 Title\n\nMore content"
    sections = split_markdown_into_sections(md)
    paths = [s[0] for s in sections]
    assert any("H1 Title > H2 Title" in p for p in paths)


def test_empty_string_returns_no_sections():
    sections = split_markdown_into_sections("")
    assert sections == []


def test_multiple_h1s_produce_separate_sections():
    md = "# First Section\n\nContent one\n\n# Second Section\n\nContent two"
    sections = split_markdown_into_sections(md)
    paths = [s[0] for s in sections]
    assert len(sections) >= 2
    assert "First Section" in paths
    assert "Second Section" in paths


def test_section_text_is_not_empty():
    md = "# Section A\n\nHello world\n\n## Sub Section\n\nMore text here"
    sections = split_markdown_into_sections(md)
    assert sections, "Expected at least one section"
    for path, text in sections:
        assert len(text) > 0, f"Section '{path}' has empty text"
