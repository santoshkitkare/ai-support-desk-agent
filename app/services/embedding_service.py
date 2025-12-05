from typing import List
import torch
from sentence_transformers import SentenceTransformer
from app.services.config import settings

# Load once at startup
# If you want GPU and it's available: .to('cuda')
_model = SentenceTransformer(settings.HF_EMBEDDING_MODEL)
_model.max_seq_length = 512  # safety for large chunks


def get_embedding(text: str) -> List[float]:
    """
    Encode a single text into a vector (length 384).
    """
    emb = _model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return emb.tolist()


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Encode multiple texts into vectors (batch).
    """
    embs = _model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, batch_size=32, show_progress_bar=True)
    return [vec.tolist() for vec in embs]
