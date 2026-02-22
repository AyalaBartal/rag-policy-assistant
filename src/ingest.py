from __future__ import annotations

from pathlib import Path
from typing import List

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from src.doc_loader import load_markdown_documents
from src.section_splitter import split_markdown_into_sections
from src.chunker import chunk_sections


VECTORSTORE_DIR = Path("vectorstore")
COLLECTION_NAME = "policy_chunks"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"


def ingest(recreate: bool = True) -> None:
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(VECTORSTORE_DIR),
        settings=Settings(anonymized_telemetry=False),
    )

    if recreate:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    else:
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    model = SentenceTransformer(EMBED_MODEL_NAME)

    docs = load_markdown_documents()

    all_ids: List[str] = []
    all_texts: List[str] = []
    all_metas: List[dict] = []

    for d in docs:
        sections = split_markdown_into_sections(d.content)
        chunks = chunk_sections(d.meta, d.path, sections)

        for c in chunks:
            all_ids.append(c.chunk_id)
            all_texts.append(c.text)
            all_metas.append(c.meta)

    if not all_texts:
        raise RuntimeError("No chunks produced. Check corpus and chunking settings.")

    batch_size = 64
    for i in range(0, len(all_texts), batch_size):
        batch_texts = all_texts[i : i + batch_size]
        batch_ids = all_ids[i : i + batch_size]
        batch_metas = all_metas[i : i + batch_size]

        embeddings = model.encode(batch_texts, normalize_embeddings=True).tolist()

        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=batch_metas,
            embeddings=embeddings,
        )

    print(f"Ingested documents: {len(docs)}")
    print(f"Total chunks stored: {len(all_ids)}")
    print(f"Vector store location: {VECTORSTORE_DIR.resolve()}")
    print(f"Collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    ingest(recreate=True)