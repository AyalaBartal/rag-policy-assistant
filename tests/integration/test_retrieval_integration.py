"""
Integration tests for the retrieval pipeline using the real vector store.

These tests verify end-to-end behaviour from query → Chroma → RAG wrapper
without calling an LLM.
"""
from __future__ import annotations

import pytest

from src.retrieval.rag_retriever import RagRetriever
from src.retrieval.vector_retriever import Retriever, VECTORSTORE_DIR


# ---------------------------------------------------------------------------
# Vector store sanity checks
# ---------------------------------------------------------------------------

def test_vectorstore_directory_exists():
    """The pre-built vector store must be present in the repository."""
    assert VECTORSTORE_DIR.exists(), (
        f"vectorstore directory not found at {VECTORSTORE_DIR.resolve()}"
    )


def test_vectorstore_contains_documents():
    """The Chroma collection must contain at least 20 indexed policy chunks."""
    retriever = Retriever()
    count = retriever.collection.count()
    assert count >= 20, f"Expected >= 20 chunks in vectorstore, got {count}"


# ---------------------------------------------------------------------------
# Retrieval quality checks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("query,expected_keyword", [
    ("What is the return policy for unopened books?", "return"),
    ("Do you ship internationally?", "ship"),
    ("What file types are accepted for photo uploads?", "photo"),
    ("How do you handle children's data under COPPA?", "privacy"),
    ("Do you offer discounts for bulk orders?", "bulk"),
])
def test_retrieval_returns_relevant_chunk_for_policy_question(query, expected_keyword):
    """
    Each in-scope policy question must retrieve at least one chunk whose text
    contains the expected keyword (case-insensitive).
    """
    retriever = RagRetriever()
    result = retriever.retrieve(query, k=5)

    assert result.allowed, (
        f"Query '{query}' was blocked (best_distance={result.best_distance}); "
        "expected it to be allowed."
    )
    assert result.hits, "No hits returned."

    all_text = " ".join(h.text for h in result.hits).lower()
    assert expected_keyword.lower() in all_text, (
        f"Expected keyword '{expected_keyword}' not found in retrieved chunks "
        f"for query: '{query}'"
    )


def test_retrieval_returns_top_k_results():
    """Retrieval must return exactly k=5 results for an in-scope query."""
    retriever = RagRetriever()
    result = retriever.retrieve("What is the refund process?", k=5)

    assert result.allowed
    assert len(result.hits) == 5


def test_retrieval_best_distance_matches_first_hit():
    """best_distance must equal the distance of the first (closest) hit."""
    retriever = RagRetriever()
    result = retriever.retrieve("Return policy for unopened books", k=5)

    assert result.hits
    assert result.best_distance == pytest.approx(result.hits[0].distance)


def test_hits_are_ordered_by_distance_ascending():
    """Chroma must return hits in ascending distance order (closest first)."""
    retriever = RagRetriever()
    result = retriever.retrieve("Shipping policy for international orders", k=5)

    distances = [h.distance for h in result.hits]
    assert distances == sorted(distances), "Hits are not sorted by distance ascending."


def test_each_hit_has_required_metadata_fields():
    """Every returned hit must carry doc_id, doc_title, section_path metadata."""
    retriever = RagRetriever()
    result = retriever.retrieve("How long does shipping take?", k=3)

    assert result.hits
    for hit in result.hits:
        assert hit.chunk_id, "chunk_id must not be empty."
        assert hit.text, "text must not be empty."
        assert "doc_id" in hit.meta, f"Missing doc_id in metadata: {hit.meta}"
        assert "doc_title" in hit.meta, f"Missing doc_title in metadata: {hit.meta}"
        assert "section_path" in hit.meta, f"Missing section_path in metadata: {hit.meta}"


# ---------------------------------------------------------------------------
# Guardrail / out-of-scope checks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("query", [
    "What is the weather in Tokyo today?",
    "Who won the last World Cup?",
    "What is my name?",
])
def test_out_of_scope_query_is_refused(query):
    """
    Completely unrelated queries must be blocked by the distance threshold.
    """
    retriever = RagRetriever(distance_threshold=0.55)
    result = retriever.retrieve(query)

    assert not result.allowed, (
        f"Expected query '{query}' to be refused, "
        f"but it was allowed with best_distance={result.best_distance}"
    )


def test_empty_query_is_refused():
    """An empty query must be refused immediately without hitting the DB."""
    retriever = RagRetriever()
    result = retriever.retrieve("   ")

    assert not result.allowed
    assert result.best_distance is None
    assert result.hits == []


# ---------------------------------------------------------------------------
# Context builder integration
# ---------------------------------------------------------------------------

def test_build_context_includes_source_labels_and_text():
    """build_context must produce numbered [Source N] blocks with text."""
    retriever = RagRetriever()
    result = retriever.retrieve("What is the return policy?", k=3)

    context = retriever.build_context(result)

    assert "[Source 1]" in context
    assert "[Source 2]" in context
    assert "Content:" in context
    assert "Citation:" in context


# ---------------------------------------------------------------------------
# CI / mock-mode pipeline integration
# ---------------------------------------------------------------------------

def test_rag_pipeline_ci_mode_returns_mock_answer():
    """In CI mode (no LLM client), the pipeline must return a mock answer."""
    from src.rag.rag_pipeline import RagPipeline

    pipeline = RagPipeline(llm_client=None)
    result = pipeline.answer("What is the return policy?")

    assert result.answer == "Mock response (CI mode)"
    assert result.allowed is True
    assert result.citations == []
