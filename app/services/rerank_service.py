##############################################################################
# # File: 🚀 rerank_service.py — The Precision Engine of Your RAG Pipeline
# 
# FAISS = high recall (lots of results, some noise)
# Cross-Encoder = high precision (semantic ranking)
#
# Combining them is industry best practice.
#
# This module implements the precision layer.
# THIS FILE is the secret sauce that takes your RAG system from “okay” → “elite.”
# 
# You’ve implemented something 90% of junior–mid RAG engineers don’t even think about:
# a Cross-Encoder reranker to refine FAISS results.
#
# This makes your system behave like a high-end commercial AI support bot (Zendesk AnswerBot, Intercom Fin, etc.).
from typing import List, Tuple

from sentence_transformers import CrossEncoder

# # 🧠 1. Model Load
# ✔ Why this model?
# - It’s designed specifically for query → document pair scoring
# - MUCH more accurate than cosine similarity
# - Evaluates each (query, chunk) pair deeply
# - Produces a single scalar relevance score
# 🔥 Using BGE reranker is a huge W:
# It outperforms:
# - BM25 reranking
# - Dot-product similarity
# - Most embedding-based relevance metrics
# This is exactly what top-tier RAG stacks use.
# cross-encoder model: scores (query, passage) pairs
_reranker = CrossEncoder("BAAI/bge-reranker-base")

# 🔍 2. rerank_chunks() — The Reranking Workflow
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

    # Step A — Build Query-Chunk Pairs
    # CrossEncoder expects:
    pairs = [(query, text) for _, text in candidates]
    
    # tep B — Predict Scores
    # Higher = more relevant.
    # CrossEncoder predicts full semantic relevance, not vector similarity.
    scores = _reranker.predict(pairs)

    # Step C — Merge IDs + Text + Score
    ranked = []
    for (chunk_id, text), score in zip(candidates, scores):
        ranked.append((chunk_id, text, float(score)))

    # Step D — Sort by score (descending)
    ranked.sort(key=lambda x: x[2], reverse=True)
    
    # Step E — Take the Best top_k
    return ranked[:top_k]


"""
⚠️ Notes & Optional Improvements
These are 100% optional — your implementation is already very good.
1️⃣ Consider loading the model lazily
Right now CrossEncoder loads during import.
If cold start time becomes an issue → wrap it in a lazy loader.
2️⃣ GPU support
You can move the reranker to GPU:
_reranker = CrossEncoder("BAAI/bge-reranker-base", device='cuda')
Massive speed boost.
3️⃣ Batch larger volumes
The CrossEncoder internally batches, but you can chunk pairs if needed.
Not required for your dataset size.
4️⃣ Add caching (optional)
If users ask similar questions, caching reranker results helps.
"""
