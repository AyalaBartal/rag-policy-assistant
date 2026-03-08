from src.retrieval.rag_retriever import RagRetriever


class FakeRetriever:
    def __init__(self, hits):
        self._hits = hits

    def search(self, query: str, k: int = 5):
        return self._hits[:k]


def test_retrieve_allows_when_best_distance_is_below_threshold():
    fake_hits = [
        {
            "id": "chunk-1",
            "text": "Refunds are processed within 5-7 business days.",
            "distance": 0.32,
            "meta": {
                "doc_id": "return_refund_policy",
                "doc_title": "Return Refund Policy",
                "version": "1.0",
                "last_updated": "2026-02-22",
                "section_path": "Return Refund Policy > Refund Process",
            },
        }
    ]

    rr = RagRetriever(
        retriever=FakeRetriever(fake_hits),
        distance_threshold=0.55,
    )

    result = rr.retrieve("What is the refund timeline?")

    assert result.allowed is True
    assert result.best_distance == 0.32
    assert len(result.hits) == 1
    assert result.hits[0].chunk_id == "chunk-1"


def test_retrieve_blocks_when_best_distance_is_above_threshold():
    fake_hits = [
        {
            "id": "chunk-1",
            "text": "Some unrelated content.",
            "distance": 0.81,
            "meta": {
                "doc_id": "faq",
                "doc_title": "FAQ",
                "version": "1.0",
                "last_updated": "2026-02-22",
                "section_path": "FAQ > Miscellaneous",
            },
        }
    ]

    rr = RagRetriever(
        retriever=FakeRetriever(fake_hits),
        distance_threshold=0.55,
    )

    result = rr.retrieve("What is your office address in Tokyo?")

    assert result.allowed is False
    assert result.best_distance == 0.81
    assert len(result.hits) == 1


def test_retrieve_blocks_empty_query():
    rr = RagRetriever(
        retriever=FakeRetriever([]),
        distance_threshold=0.55,
    )

    result = rr.retrieve("   ")

    assert result.allowed is False
    assert result.best_distance is None
    assert result.hits == []


def test_format_citation():
    meta = {
        "doc_title": "Privacy Policy",
        "version": "1.0",
        "last_updated": "2026-02-22",
        "section_path": "Privacy Policy > Children's Privacy Rights (COPPA Compliance)",
    }

    citation = RagRetriever.format_citation(meta)

    assert citation == (
        "Privacy Policy v1.0 (2026-02-22) – "
        "Privacy Policy > Children's Privacy Rights (COPPA Compliance)"
    )


def test_build_context_includes_sources_and_citations():
    fake_hits = [
        {
            "id": "chunk-1",
            "text": "We comply fully with COPPA.",
            "distance": 0.31,
            "meta": {
                "doc_id": "privacy_policy",
                "doc_title": "Privacy Policy",
                "version": "1.0",
                "last_updated": "2026-02-22",
                "section_path": "Privacy Policy > COPPA",
            },
        },
        {
            "id": "chunk-2",
            "text": "Parents may review and delete child data.",
            "distance": 0.40,
            "meta": {
                "doc_id": "privacy_policy",
                "doc_title": "Privacy Policy",
                "version": "1.0",
                "last_updated": "2026-02-22",
                "section_path": "Privacy Policy > Parent Rights",
            },
        },
    ]

    rr = RagRetriever(
        retriever=FakeRetriever(fake_hits),
        distance_threshold=0.55,
    )

    result = rr.retrieve("How do you handle children's data?")
    context = rr.build_context(result)

    assert "[Source 1]" in context
    assert "[Source 2]" in context
    assert "Privacy Policy v1.0 (2026-02-22)" in context
    assert "We comply fully with COPPA." in context
    assert "Parents may review and delete child data." in context