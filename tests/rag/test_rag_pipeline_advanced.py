"""Advanced unit tests for RagPipeline using fake collaborators."""
from __future__ import annotations

from src.rag.rag_pipeline import RagPipeline
from src.retrieval.rag_retriever import RetrievalHit, RetrievalResult


# ---------------------------------------------------------------------------
# Fake collaborators (mirrored from test_rag_pipeline.py — not importable)
# ---------------------------------------------------------------------------

class FakeRagRetriever:
    def __init__(self, result: RetrievalResult):
        self._result = result
        self.last_k = None

    def retrieve(self, question: str, k=None):
        self.last_k = k
        return self._result

    def build_context(self, retrieval_result: RetrievalResult) -> str:
        return (
            "[Source 1]\n"
            "Citation: Return Refund Policy v1.0 (2026-02-22) – Refund Process\n"
            "Chunk ID: chunk-1\n"
            "Content:\nRefunds are processed within 5-7 business days."
        )

    @staticmethod
    def format_citation(meta):
        doc_title = meta.get("doc_title", "Unknown Document")
        version = meta.get("version", "")
        last_updated = meta.get("last_updated", "")
        section_path = meta.get("section_path", "Unknown Section")
        version_part = f" v{version}" if version else ""
        date_part = f" ({last_updated})" if last_updated else ""
        return f"{doc_title}{version_part}{date_part} – {section_path}"


class FakeChoiceMessage:
    def __init__(self, content: str):
        self.content = content


class FakeChoice:
    def __init__(self, content: str):
        self.message = FakeChoiceMessage(content)


class FakeResponse:
    def __init__(self, content: str):
        self.choices = [FakeChoice(content)]


class FakeChatCompletions:
    def __init__(self, content: str):
        self._content = content

    def create(self, model, messages):
        return FakeResponse(self._content)


class FakeChat:
    def __init__(self, content: str):
        self.completions = FakeChatCompletions(content)


class FakeLLMClient:
    def __init__(self, content: str):
        self.chat = FakeChat(content)


def make_allowed_result() -> RetrievalResult:
    return RetrievalResult(
        query="What is the refund timeline?",
        hits=[
            RetrievalHit(
                chunk_id="chunk-1",
                text="Refunds are processed within 5-7 business days.",
                distance=0.32,
                meta={
                    "doc_id": "return_refund_policy",
                    "doc_title": "Return Refund Policy",
                    "version": "1.0",
                    "last_updated": "2026-02-22",
                    "section_path": "Return Refund Policy > Refund Process",
                },
            )
        ],
        top_k=5,
        best_distance=0.32,
        allowed=True,
        threshold=0.55,
    )


def make_blocked_result() -> RetrievalResult:
    return RetrievalResult(
        query="What is the capital of Mars?",
        hits=[],
        top_k=5,
        best_distance=None,
        allowed=False,
        threshold=0.55,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_system_prompt_instructs_grounded_answers():
    prompt = RagPipeline.system_prompt()
    assert "only" in prompt.lower()
    assert "sources" in prompt.lower()


def test_answer_with_k_override():
    fake_retriever = FakeRagRetriever(make_allowed_result())
    pipeline = RagPipeline(
        rag_retriever=fake_retriever,
        llm_client=None,
    )
    pipeline.answer("What is the refund policy?", k=3)
    assert fake_retriever.last_k == 3


def test_call_llm_returns_mock_in_ci_mode():
    pipeline = RagPipeline(
        rag_retriever=FakeRagRetriever(make_allowed_result()),
        llm_client=None,
    )
    result = pipeline._call_llm("system prompt", "user prompt")
    assert result == "Mock response (CI mode)"


def test_answer_includes_best_distance():
    pipeline = RagPipeline(
        rag_retriever=FakeRagRetriever(make_allowed_result()),
        llm_client=None,
    )
    result = pipeline.answer("What is the refund timeline?")
    assert result.best_distance == 0.32


def test_refusal_has_empty_citations():
    pipeline = RagPipeline(
        rag_retriever=FakeRagRetriever(make_blocked_result()),
        llm_client=FakeLLMClient("Should not be used."),
    )
    result = pipeline.answer("What is the capital of Mars?")
    assert result.citations == []
    assert result.allowed is False
