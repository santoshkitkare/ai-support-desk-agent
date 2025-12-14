##############################################################################
# file: 🚀 embedding_service.py — "The Vector Factory"
# This module handles:
# - Loading SentenceTransformer model
# - Generating embeddings (single + batch)
# - Normalizing vectors
# - GPU support (optional)
# Your RAG accuracy heavily depends on this file.
from typing import List
import torch
from sentence_transformers import SentenceTransformer
from app.services.config import settings

# Load once at startup
# If you want GPU and it's available: .to('cuda')
# 📌 1. Model Initialization
# ✔ What’s happening:
# - Loads HuggingFace embedding model once at startup
# - Stores it in a module-level variable _model
# - Ensures max input sequence length = 512 tokens

# 🧠 Why this is awesome:
# - Faster inference: model is not reloaded per request
# - No reinitialization across uploads
# - Efficient memory usage
# - Production-grade design
_model = SentenceTransformer(settings.HF_EMBEDDING_MODEL)
_model.max_seq_length = 512  # safety for large chunks

# 📌 2. Embedding a Single Text
# Key behaviors:
# 🔹 convert_to_numpy=True
# Returns NumPy arrays → fast, clean, FAISS-compatible.
# 🔹 normalize_embeddings=True
# Normalizes vectors to unit length → essential for cosine similarity.
# This dramatically stabilizes retrieval quality.
# Output:
# A single vector → likely 384 or 768 dimensions depending on model.
def get_embedding(text: str) -> List[float]:
    """
    Encode a single text into a vector (length 384).
    """
    emb = _model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return emb.tolist()

# 📌 3. Batch Embeddings
# 🔥 Why batching matters:
# - Faster (vectorized computation)
# - Efficient on GPU or CPU
# - Required when processing hundreds of chunks during ingestion
# Good engineering choices:
# - batch_size=32 → optimal for CPU
# - show_progress_bar=True → useful during debugging
# Normalized embeddings improve FAISS performance
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Encode multiple texts into vectors (batch).
    """
    embs = _model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, batch_size=32, show_progress_bar=True)
    return [vec.tolist() for vec in embs]



"""
⚡ Opportunities for Enhancements (Optional)
Not required, but future upgrades:
1️⃣ Model quantization
Reduce memory footprint by ~40%.
2️⃣ Switch to bge-large-en for higher accuracy
If you have GPU.
3️⃣ Add async support
Not critical unless embedding thousands of docs at once.
4️⃣ Add caching layer
Avoid recomputing identical chunk embeddings.
"""