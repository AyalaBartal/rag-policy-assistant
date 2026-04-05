"""Advanced unit tests for RagRetriever using a fake vector retriever."""
from __future__ import annotations

from src.retrieval.rag_retriever import RagRetriever, RetrievalResult


class FakeRetriever:
    def __init__(self, hits):
        self._hits = hits

    def search(self, query: str, k: int = 5):
        return self._hits[:k]


def _make_hit(chunk_id: str, distance: float, **meta_overrides):
    meta = {
        "doc_id": "some_doc",
        "doc_title": "Some Document",
        "version": "1.0",
        "last_updated": "2024-01-01",
        "section_path": "Some Section",
    }
    meta.update(meta_overrides)
    return {
        "id": chunk_id,
        "text": "Sample text for testing.",
        "distance": distance,
        "meta": meta,
    }


def test_format_citation_handles_missing_fields():
    meta = {"doc_title": "Bare Document", "section_path": "Overview"}
    citation = RagRetriever.format_citation(meta)
    assert "v" not in citation.split("–")[0]  # no version prefix
    assert "(" not in citation  # no date in parentheses
    assert "Bare Document" in citation
    assert "Overview" in citation


def test_format_citation_handles_missing_section_path():
    meta = {
        "doc_title": "Privacy Policy",
        "version": "2.0",
        "last_updated": "2025-06-01",
    }
    citation = RagRetriever.format_citation(meta)
    assert "Unknown Section" in citation
    assert "Privacy Policy v2.0 (2025-06-01)" in citation


def test_retrieve_respects_k_parameter():
    hits = [_make_hit(f"chunk-{i}", 0.1 * i) for i in range(1, 4)]  # 3 hits
    rr = RagRetriever(retriever=FakeRetriever(hits), distance_threshold=0.55)

    result = rr.retrieve("How do returns work?", k=2)

    assert len(result.hits) == 2


def test_build_context_with_no_hits_returns_empty_string():
    rr = RagRetriever(retriever=FakeRetriever([]), distance_threshold=0.55)
    empty_result = RetrievalResult(
        query="anything",
        hits=[],
        top_k=5,
        best_distance=None,
        allowed=False,
        threshold=0.55,
    )
    context = rr.build_context(empty_result)
    assert context == ""


def test_retrieve_with_hits_above_threshold_is_blocked():
    hits = [
        _make_hit("chunk-1", 0.72),
        _make_hit("chunk-2", 0.85),
        _make_hit("chunk-3", 0.91),
    ]
    rr = RagRetriever(retriever=FakeRetriever(hits), distance_threshold=0.55)

    result = rr.retrieve("What is the weather in London?")

    assert result.allowed is False
    assert result.best_distance == 0.72
