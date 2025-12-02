import os
from typing import List, Tuple

import numpy as np
import faiss

from app.services.config import settings

os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)
INDEX_PATH = os.path.join(settings.FAISS_INDEX_DIR, "index.faiss")

_index = None  # global singleton
_embedding_dim = None


def _create_new_index(embedding_dim: int):
    global _index, _embedding_dim
    _embedding_dim = embedding_dim
    base_index = faiss.IndexFlatL2(embedding_dim)
    _index = faiss.IndexIDMap2(base_index)


def _load_index():
    global _index, _embedding_dim
    if os.path.exists(INDEX_PATH):
        _index = faiss.read_index(INDEX_PATH)
        _embedding_dim = _index.d  # dimension
    else:
        _index = None
        _embedding_dim = None


def init_index(embedding_dim: int):
    """Call once on startup or before first use."""
    global _index, _embedding_dim
    if _index is not None:
        return

    if os.path.exists(INDEX_PATH):
        _load_index()
    else:
        _create_new_index(embedding_dim)


def save_index():
    global _index
    if _index is not None:
        faiss.write_index(_index, INDEX_PATH)


def add_embeddings(chunk_ids: List[int], embeddings: List[List[float]]):
    """
    Add embeddings to FAISS, mapping each vector to the corresponding chunk_id.
    """
    global _index, _embedding_dim

    if not embeddings:
        return

    vecs = np.array(embeddings).astype("float32")
    if _index is None:
        # infer dim from embeddings
        init_index(embedding_dim=len(embeddings[0]))

    ids = np.array(chunk_ids).astype("int64")
    _index.add_with_ids(vecs, ids)
    save_index()


def search_similar(embedding: List[float], top_k: int) -> List[Tuple[int, float]]:
    """
    Returns list of (chunk_id, score). Score is distance (L2); smaller is better.
    """
    global _index
    if _index is None or _index.ntotal == 0:
        return []

    query = np.array([embedding]).astype("float32")
    distances, ids = _index.search(query, top_k)

    results: List[Tuple[int, float]] = []
    for idx, dist in zip(ids[0], distances[0]):
        if idx == -1:
            continue
        results.append((int(idx), float(dist)))
    return results
