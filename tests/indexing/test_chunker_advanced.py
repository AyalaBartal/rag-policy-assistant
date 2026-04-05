"""Advanced unit tests for the chunker using synthetic data."""
from __future__ import annotations

from src.indexing.chunker import (
    MAX_CHARS,
    MIN_CHARS,
    _normalize_whitespace,
    chunk_sections,
)

_DOC_META = {
    "doc_id": "test_doc",
    "title": "Test Document",
    "version": "1.0",
    "last_updated": "2024-01-01",
}

_SOURCE_PATH = "corpus/test_doc.md"


def _make_sections(text: str = "A " * 500):
    """Return a single section with the given text (~1000 chars, above MIN_CHARS)."""
    return [("Doc > Section", text)]


def test_chunk_id_is_deterministic():
    sections = _make_sections()
    chunks_a = chunk_sections(_DOC_META, _SOURCE_PATH, sections)
    chunks_b = chunk_sections(_DOC_META, _SOURCE_PATH, sections)
    assert [c.chunk_id for c in chunks_a] == [c.chunk_id for c in chunks_b]


def test_chunk_ids_are_unique_within_document():
    long_text = ("Word " * 300 + "\n\n") * 5  # ~8000 chars — forces multiple chunks
    sections = [("Doc > Section", long_text)]
    chunks = chunk_sections(_DOC_META, _SOURCE_PATH, sections)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))


def test_chunks_respect_max_chars():
    long_text = "A " * 5000  # 10000 chars, forces chunking
    sections = [("Doc > Section", long_text)]
    chunks = chunk_sections(_DOC_META, _SOURCE_PATH, sections)
    for chunk in chunks:
        assert len(chunk.text) <= MAX_CHARS, (
            f"Chunk exceeds MAX_CHARS={MAX_CHARS}: {len(chunk.text)}"
        )


def test_sections_below_min_chars_are_skipped():
    tiny_text = "Short." * 8  # ~48 chars, below MIN_CHARS=200
    sections = [("Doc > Tiny", tiny_text)]
    chunks = chunk_sections(_DOC_META, _SOURCE_PATH, sections)
    assert chunks == []


def test_normalize_whitespace_collapses_triple_newlines():
    text = "Line 1\n\n\n\n\nLine 2"
    result = _normalize_whitespace(text)
    assert "\n\n\n" not in result
    assert "Line 1" in result
    assert "Line 2" in result


def test_metadata_fields_are_all_strings():
    sections = _make_sections()
    chunks = chunk_sections(_DOC_META, _SOURCE_PATH, sections)
    assert chunks, "Expected at least one chunk"
    for chunk in chunks:
        for key, value in chunk.meta.items():
            assert isinstance(value, str), (
                f"meta[{key!r}] is {type(value).__name__}, expected str"
            )
