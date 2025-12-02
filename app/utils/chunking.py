from typing import List


def simple_split(text: str, max_tokens: int = 500, overlap: int = 50) -> List[str]:
    """
    Very naive chunker by words.
    Later you can swap with tiktoken-based token chunker.
    """
    words = text.split()
    if not words:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(words):
        end = start + max_tokens
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        # Overlap to preserve context
        start = end - overlap

    return chunks
