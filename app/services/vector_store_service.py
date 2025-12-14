##############################################################################
# File: vector_store_service.py: Your High-Performance Vector Memory Layer
# THIS is the engine room of your retrieval pipeline.
# If embedding_service.py is the brain, vector_store_service.py is the memory cortex — fast, durable, and optimized for similarity search.
# This file wires FAISS into your application and ensures your knowledge base becomes searchable with millisecond latency.
# 
# This module handles:
# - Creating FAISS index
# - Loading/saving index
# - Adding embeddings
# - Searching similar vectors
# - Ensuring ID → chunk mapping
#
# This File Is Solid
# You nailed:
# ✔ Index initialization pattern
# ✔ Persistence strategy
# ✔ ID-mapped vector storage
# ✔ Correct data types
# ✔ Full compatibility with BGE embeddings
# ✔ Clean, readable abstraction
###############################################################################
import os
from typing import List, Tuple

import numpy as np
import faiss

from app.services.config import settings

# 🧱 1. File System Setup
# ✔ Purpose:
# Ensures the folder exists
# Defines fixed path for the FAISS index file
os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)
INDEX_PATH = os.path.join(settings.FAISS_INDEX_DIR, "index.faiss")

# 🧠 2. Global In-Memory State
# Why?
# - FAISS index lives in memory for fast search
# - Dimension stored to prevent reinitialization issues
# This avoids constant disk I/O.
_index = None  # global singleton
_embedding_dim = None

# 🧩 3. Creating a New Index
# What’s happening:
# - IndexFlatL2 → exact search using L2 distance
# - Wrapped with IndexIDMap2 → allows mapping vectors to custom IDs (chunk IDs)
# Why this is great:
# ✔ Perfect for up to ~1M vectors
# ✔ No training needed
# ✔ Deterministic
# ✔ Simple to maintain
# For your use case (support docs), this is exactly the right choice.
def _create_new_index(embedding_dim: int):
    global _index, _embedding_dim
    _embedding_dim = embedding_dim
    base_index = faiss.IndexFlatL2(embedding_dim)
    _index = faiss.IndexIDMap2(base_index)


def _load_index():
    global _index, _embedding_dim
    # 📦 4. Loading Existing Index From Disk
    # Why this matters:
    # Your index persists across restarts.
    # This allows:
    # - Hot reloads
    # - Docker restarts
    # - ECS/EC2 stop/start
    # - No re-ingestion needed
    # Huge time saver.
    if os.path.exists(INDEX_PATH):
        _index = faiss.read_index(INDEX_PATH)
        _embedding_dim = _index.d  # dimension
    else:
        _index = None
        _embedding_dim = None

# ⚡ 5. init_index() — The Safety Wrapper
# Logic flow:
# 1. If index already loaded → do nothing
# 2. If index file exists → load it
# 3. Else → create a new one
# Minimal and effective.
def init_index(embedding_dim: int):
    """Call once on startup or before first use."""
    global _index, _embedding_dim
    if _index is not None:
        return

    if os.path.exists(INDEX_PATH):
        _load_index()
    else:
        _create_new_index(embedding_dim)

# 💾 6. save_index()
# This persists the full vector index to disk.
# You save the index every time you add vectors — this gives durability.
# ✔ Good for consistency
# ✔ Safe for development
# ⚠️ In production, you may want batched saves instead of saving on every insertion (performance consideration).
def save_index():
    global _index
    if _index is not None:
        faiss.write_index(_index, INDEX_PATH)

# 🔥 7. Adding Embeddings to FAISS
# What’s happening:
# - Converts embeddings to float32 (FAISS requirement)
# - Uses chunk IDs as unique identifiers
# - Saves index after insertion
# Key point:
# Each embedding vector is permanently tied to a DocumentChunk.id.
# This enables:
# - Fast Retrieval
# - Context Reconstruction
# - Reranking
# - Traceback to original document
# Your pipeline is correctly wired.
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

# 🔍 8. Searching Similar Chunks
def search_similar(embedding: List[float], top_k: int) -> List[Tuple[int, float]]:
    """
    Returns list of (chunk_id, score). Score is distance (L2); smaller is better.
    """
    global _index
    if _index is None or _index.ntotal == 0:
        return []

    query = np.array([embedding]).astype("float32")
    # Search logic:
    # - Takes L2 distance
    # - Returns top_k nearest vectors
    # - filters idx == -1 (FAISS filler)
    # Returned format:
    # [(chunk_id, distance), ...]
    # Interpretation:
    # - smaller distance = better match
    # - You later convert L2 → relevance using reranker
    # Critical RAG building block.
    distances, ids = _index.search(query, top_k)

    results: List[Tuple[int, float]] = []
    for idx, dist in zip(ids[0], distances[0]):
        if idx == -1:
            continue
        results.append((int(idx), float(dist)))
    return results


"""
💡 Optional Improvements (only when scaling)
1️⃣ Switch to HNSW or IVF for massive datasets (>1M vectors)
Improves query time.
2️⃣ Add locking for concurrent writes (if multiple workers ingest)
Right now it's single-process safe.
3️⃣ Add index metadata versioning
Avoid accidental mixing of embedding models.
4️⃣ Save index only once per ingestion batch
Currently saves after each add — slower for large uploads.
5️⃣ Expose delete/update vector APIs
If you ever want document removal.
"""