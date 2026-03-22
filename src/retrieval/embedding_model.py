from __future__ import annotations

from pathlib import Path
from typing import Optional


EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_CACHE_DIR = Path("model_cache")

_model = None


def get_embedding_model():
    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer
        MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _model = SentenceTransformer(
            EMBED_MODEL_NAME,
            cache_folder=str(MODEL_CACHE_DIR),
        )

    return _model