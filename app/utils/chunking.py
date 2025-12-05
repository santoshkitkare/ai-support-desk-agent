from typing import List


# def simple_split(text: str, max_tokens: int = 500, overlap: int = 50) -> List[str]:
#     """
#     Very naive chunker by words.
#     Later you can swap with tiktoken-based token chunker.
#     """
#     words = text.split()
#     if not words:
#         return []

#     chunks: List[str] = []
#     start = 0
#     while start < len(words):
#         end = start + max_tokens
#         chunk_words = words[start:end]
#         chunks.append(" ".join(chunk_words))
#         # Overlap to preserve context
#         start = end - overlap

#     return chunks
from typing import List

def split_by_chars(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 250,
) -> List[str]:
    """
    Simple char-based chunking with overlap.
    Works well enough for support docs, FAQs, policies.
    """
    text = text.strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = start + chunk_size
        chunk = text[start:end]

        # try to break at last sentence/line end for nicer splits
        if end < n:
            for sep in [".\n", ". ", "\n", " "]:
                idx = chunk.rfind(sep)
                if idx != -1 and idx > chunk_size * 0.4:
                    chunk = chunk[:idx + len(sep)]
                    end = start + len(chunk)
                    break

        chunks.append(chunk.strip())
        start = max(end - overlap, 0)

        if end >= n:
            break

    # remove tiny noise chunks
    chunks = [c for c in chunks if len(c) > 50]
    return chunks
