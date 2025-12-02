from typing import List
import torch
from sentence_transformers import SentenceTransformer

# Load once at startup
# If you want GPU and it's available: .to('cuda')
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
model.max_seq_length = 512  # safety for large chunks


def get_embedding(text: str) -> List[float]:
    """
    Encode a single text into a vector (length 384).
    """
    emb = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return emb.tolist()


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Encode multiple texts into vectors (batch).
    """
    embs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return [vec.tolist() for vec in embs]
