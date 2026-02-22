from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

VECTORSTORE_DIR = Path("vectorstore")
COLLECTION_NAME = "policy_chunks"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"


class Retriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=str(VECTORSTORE_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_collection(COLLECTION_NAME)
        self.model = SentenceTransformer(EMBED_MODEL_NAME)

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        q_emb = self.model.encode([query], normalize_embeddings=True).tolist()[0]
        res = self.collection.query(
            query_embeddings=[q_emb],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        for i in range(len(res["ids"][0])):
            hits.append(
                {
                    "id": res["ids"][0][i],
                    "distance": res["distances"][0][i],
                    "text": res["documents"][0][i],
                    "meta": res["metadatas"][0][i],
                }
            )
        return hits


if __name__ == "__main__":
    r = Retriever()
    queries = [
        "What is the return and refund timeline?",
        "Do you offer discounts for bulk orders?",
        "What are the photo upload requirements?",
        "Do you ship internationally and how long does it take?",
        "How do you handle children's data (COPPA)?",
    ]

    for q in queries:
        print("\n" + "=" * 100)
        print("Q:", q)
        hits = r.search(q, k=5)
        for h in hits[:3]:
            m = h["meta"]
            print("\n---")
            print(f"{m.get('doc_title')} | {m.get('section_path')} | dist={h['distance']:.4f}")
            print("chunk_id:", h["id"])
            print(h["text"][:350].replace("\n", " "))