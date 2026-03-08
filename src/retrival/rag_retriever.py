from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.retrival.vector_retriever import Retriever


DEFAULT_TOP_K = 5
DEFAULT_DISTANCE_THRESHOLD = 0.55


@dataclass(frozen=True)
class RetrievalHit:
    chunk_id: str
    text: str
    distance: float
    meta: Dict[str, Any]


@dataclass(frozen=True)
class RetrievalResult:
    query: str
    hits: List[RetrievalHit]
    top_k: int
    best_distance: Optional[float]
    allowed: bool
    threshold: float


class RagRetriever:
    """
    RAG-aware retrieval wrapper.

    Lower distance is better.
    A query is allowed only if:
    - at least one hit exists
    - best_distance <= threshold
    """

    def __init__(
        self,
        retriever: Optional[Retriever] = None,
        *,
        default_top_k: int = DEFAULT_TOP_K,
        distance_threshold: float = DEFAULT_DISTANCE_THRESHOLD,
    ) -> None:
        self.retriever = retriever or Retriever()
        self.default_top_k = default_top_k
        self.distance_threshold = distance_threshold

    def retrieve(self, query: str, k: Optional[int] = None) -> RetrievalResult:
        query = query.strip()
        top_k = k or self.default_top_k

        if not query:
            return RetrievalResult(
                query=query,
                hits=[],
                top_k=top_k,
                best_distance=None,
                allowed=False,
                threshold=self.distance_threshold,
            )

        raw_hits = self.retriever.search(query, k=top_k)

        hits = [
            RetrievalHit(
                chunk_id=h["id"],
                text=h["text"],
                distance=float(h["distance"]),
                meta=h["meta"],
            )
            for h in raw_hits
        ]

        best_distance = hits[0].distance if hits else None
        allowed = best_distance is not None and best_distance <= self.distance_threshold

        return RetrievalResult(
            query=query,
            hits=hits,
            top_k=top_k,
            best_distance=best_distance,
            allowed=allowed,
            threshold=self.distance_threshold,
        )

    @staticmethod
    def format_citation(meta: Dict[str, Any]) -> str:
        """
        Format:
        Document Title vX.X (YYYY-MM-DD) – Section
        """
        doc_title = meta.get("doc_title", "Unknown Document")
        version = meta.get("version", "")
        last_updated = meta.get("last_updated", "")
        section_path = meta.get("section_path", "Unknown Section")

        version_part = f" v{version}" if version else ""
        date_part = f" ({last_updated})" if last_updated else ""

        return f"{doc_title}{version_part}{date_part} – {section_path}"

    def build_context(self, result: RetrievalResult) -> str:
        """
        Build LLM-ready context from retrieved hits.
        """
        blocks: List[str] = []

        for i, hit in enumerate(result.hits, start=1):
            citation = self.format_citation(hit.meta)
            blocks.append(
                f"[Source {i}]\n"
                f"Citation: {citation}\n"
                f"Chunk ID: {hit.chunk_id}\n"
                f"Content:\n{hit.text}"
            )

        return "\n\n".join(blocks)