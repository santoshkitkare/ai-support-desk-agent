from typing import List, Tuple

from sentence_transformers import CrossEncoder

# cross-encoder model: scores (query, passage) pairs
_reranker = CrossEncoder("BAAI/bge-reranker-base")

def rerank_chunks(
    query: str,
    candidates: List[Tuple[int, str]],  # (chunk_id, content)
    top_k: int,
) -> List[Tuple[int, str, float]]:
    """
    Returns list sorted by relevance desc:
    [(chunk_id, content, score), ...]
    """
    if not candidates:
        return []

    pairs = [(query, text) for _, text in candidates]
    scores = _reranker.predict(pairs)

    ranked = []
    for (chunk_id, text), score in zip(candidates, scores):
        ranked.append((chunk_id, text, float(score)))

    ranked.sort(key=lambda x: x[2], reverse=True)
    return ranked[:top_k]
