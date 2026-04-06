from src.rag.rag_pipeline import RagPipeline
from src.retrieval.rag_retriever import RetrievalHit, RetrievalResult


class FakeRagRetriever:
    def __init__(self, result: RetrievalResult):
        self._result = result

    def retrieve(self, question: str, k=None):
        return self._result

    def build_context(self, retrieval_result: RetrievalResult) -> str:
        return (
            "[Source 1]\n"
            "Citation: Return Refund Policy v1.0 (2026-02-22) – Return Refund Policy > Refund Process\n"
            "Chunk ID: chunk-1\n"
            "Content:\n"
            "Refunds are processed within 5-7 business days."
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

    def create(self, model, messages, **kwargs):
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
        query="Where is your office in Tokyo?",
        hits=[],
        top_k=5,
        best_distance=None,
        allowed=False,
        threshold=0.55,
    )


def test_build_user_prompt_includes_question_and_sources():
    pipeline = RagPipeline(
        rag_retriever=FakeRagRetriever(make_allowed_result()),
        llm_client=FakeLLMClient("Refunds are processed within 5-7 business days."),
    )

    prompt = pipeline.build_user_prompt(
        "What is the refund timeline?",
        make_allowed_result(),
    )

    assert "User question:" in prompt
    assert "What is the refund timeline?" in prompt
    assert "Retrieved sources:" in prompt
    assert "[Source 1]" in prompt
    assert "Refunds are processed within 5-7 business days." in prompt


def test_answer_returns_refusal_when_not_allowed():
    pipeline = RagPipeline(
        rag_retriever=FakeRagRetriever(make_blocked_result()),
        llm_client=FakeLLMClient("This should not be used."),
    )

    result = pipeline.answer("Where is your office in Tokyo?")

    assert result.allowed is False
    assert result.citations == []
    assert "could not find" in result.answer.lower()


def test_answer_returns_llm_response_and_citations_when_allowed():
    pipeline = RagPipeline(
        rag_retriever=FakeRagRetriever(make_allowed_result()),
        llm_client=FakeLLMClient("Refunds are processed within 5-7 business days."),
    )

    result = pipeline.answer("What is the refund timeline?")

    assert result.allowed is True
    assert result.answer == "Refunds are processed within 5-7 business days."
    assert len(result.citations) == 1
    assert "Return Refund Policy v1.0 (2026-02-22)" in result.citations[0]


def test_extract_citations_returns_formatted_citations():
    pipeline = RagPipeline(
        rag_retriever=FakeRagRetriever(make_allowed_result()),
        llm_client=FakeLLMClient("Refunds are processed within 5-7 business days."),
    )

    citations = pipeline.extract_citations(make_allowed_result())

    assert len(citations) == 1
    assert citations[0] == (
        "Return Refund Policy v1.0 (2026-02-22) – "
        "Return Refund Policy > Refund Process"
    )