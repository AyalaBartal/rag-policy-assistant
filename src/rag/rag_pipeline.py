from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.retrieval.rag_retriever import RagRetriever, RetrievalResult


DEFAULT_MODEL_NAME = "gpt-4o-mini"


@dataclass(frozen=True)
class RagAnswer:
    question: str
    answer: str
    citations: List[str]
    allowed: bool
    best_distance: Optional[float]


class RagPipeline:
    """
    End-to-end RAG pipeline:
    1. retrieve relevant chunks
    2. block low-confidence queries
    3. build prompt context
    4. ask LLM to answer using only retrieved sources
    5. return answer + structured citations
    """

    def __init__(
        self,
        rag_retriever: Optional[RagRetriever] = None,
        llm_client: Optional[Any] = None,
        model_name: str = DEFAULT_MODEL_NAME,
    ) -> None:
        self.llm_client = llm_client
        self.model_name = model_name

        # Only create the real retriever when needed
        if rag_retriever is not None:
            self.rag_retriever = rag_retriever
        elif llm_client is None:
            self.rag_retriever = None
        else:
            self.rag_retriever = RagRetriever()

    @staticmethod
    def system_prompt() -> str:
        return (
            "You are a policy assistant for Custom Children's Books.\n"
            "Answer using only the provided source excerpts.\n"
            "Do not use outside knowledge.\n"
            "If the answer is not supported by the sources, say that you could not find it in the policy documents.\n"
            "Be concise and accurate.\n"
            "When answering, rely only on facts supported by the retrieved sources.\n"
        )

    def build_user_prompt(self, question: str, retrieval_result: RetrievalResult) -> str:
        context = self.rag_retriever.build_context(retrieval_result)
        return (
            f"User question:\n{question}\n\n"
            f"Retrieved sources:\n{context}\n\n"
            "Instructions:\n"
            "- Answer the user question using only the retrieved sources.\n"
            "- If the sources do not contain enough information, say so clearly.\n"
            "- Do not invent policies, prices, timelines, or facts.\n"
            "- Do not cite sources that are not in the retrieved context.\n"
        )

    def extract_citations(self, retrieval_result: RetrievalResult) -> List[str]:
        return [
            self.rag_retriever.format_citation(hit.meta)
            for hit in retrieval_result.hits
        ]

    def _refusal_answer(self, question: str, retrieval_result: RetrievalResult) -> RagAnswer:
        return RagAnswer(
            question=question,
            answer="I could not find a reliable answer to that in the policy documents.",
            citations=[],
            allowed=False,
            best_distance=retrieval_result.best_distance,
        )

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if self.llm_client is None:
            return "Mock response (CI mode)"

        response = self.llm_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    def answer(self, question: str, k: Optional[int] = None) -> RagAnswer:
        # CI / test mode: no retriever and no LLM
        if self.rag_retriever is None:
            return RagAnswer(
                question=question,
                answer="Mock response (CI mode)",
                citations=[],
                allowed=True,
                best_distance=None,
            )

        retrieval_result = self.rag_retriever.retrieve(question, k=k)

        if not retrieval_result.allowed:
            return self._refusal_answer(question, retrieval_result)

        system_prompt = self.system_prompt()
        user_prompt = self.build_user_prompt(question, retrieval_result)
        llm_answer = self._call_llm(system_prompt, user_prompt)
        citations = self.extract_citations(retrieval_result)

        return RagAnswer(
            question=question,
            answer=llm_answer,
            citations=citations,
            allowed=True,
            best_distance=retrieval_result.best_distance,
        )