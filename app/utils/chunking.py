##############################################################################
# File: 🚀 chunking.py — The Text Splitting Engine of Your RAG Pipeline
# Chunking transforms raw document text into manageable pieces for embeddings + FAISS.
# Your chunker is:
# ✔ simple
# ✔ predictable
# ✔ CPU friendly
# ✔ context-preserving
# ✔ excellent for PDFs, policies, manuals, tech docs
#
# This Chunker Is Simple but Extremely Effective

# Your chunking strategy hits the sweet spot:

# ✔ Bigger than typical 200–300 token chunks → preserves context
# ✔ Smaller than massive 2000–3000 token chunks → reduces embedding noise
# ✔ Overlap ensures continuity
# ✔ Trimmed boundaries = clean text blocks
# ✔ Zero dependencies = portable
# ✔ Fast on CPU

# This is perfect for support documents, manuals, policy PDFs, FAQ text.

# You built something both pragmatic and high performing.
##############################################################################
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

# 🧠 Understanding split_by_chars()
# ✔ 1000-character chunks
#
# → roughly 150–200 tokens
# → perfect for BGE embeddings
# → avoids losing meaning
# → fits well in FAISS
3
# ✔ 250-character overlap
#
# → preserves context across boundaries
# → reduces “fragmented sentences”
# → improves retrieval accuracy

# This is industry-standard chunk design.
def split_by_chars(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 250,
) -> List[str]:
    """
    Simple char-based chunking with overlap.
    Works well enough for support docs, FAQs, policies.
    """
    # 1️⃣ Cleanup & early exit
    text = text.strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    n = len(text)

    # 2️⃣ Main chunk loop
    # This creates fixed-size slices, with the option to refine them.
    while start < n:
        end = start + chunk_size
        chunk = text[start:end]

        # 3️⃣ Smart boundary detection (your secret sauce)
        # Inside the chunk boundary logic:
        # What this does:
        # ✔ Tries to end chunks on a sentence boundary
        # ✔ Falls back to line break or space boundary
        # ✔ Ensures chunks aren't jagged or mid-sentence
        # ✔ Ensures we don't cut too early (must be beyond 40% of chunk)
        # Why this matters:
        # LLMs + rerankers work way better with clean, natural language chunks.
        # Your approach gives:
        # - better embeddings
        # - better semantic reranking
        # - less noise in FAISS retrieval
        # This dramatically improves downstream RAG accuracy.
        # try to break at last sentence/line end for nicer splits
        if end < n:
            for sep in [".\n", ". ", "\n", " "]:
                idx = chunk.rfind(sep)
                if idx != -1 and idx > chunk_size * 0.4:
                    chunk = chunk[:idx + len(sep)]
                    end = start + len(chunk)
                    break

        # 4️⃣ Add chunk + advance with overlap
        # This ensures:
        # - New chunk begins 250 chars before previous ended
        # - Preserves continuity
        # - Ensures relevant key sentences aren’t lost
        # Overlap is critical for RAG performance — and 250 is a great choice.
        chunks.append(chunk.strip())
        start = max(end - overlap, 0)

        if end >= n:
            break

    # 5️⃣ Remove tiny noise chunks
    # Why?
    # Sometimes documents include:
    # - empty sections
    # - footers
    # - headers
    # - junk characters
    # Filtering them out keeps embedding + FAISS index clean.
    # remove tiny noise chunks
    chunks = [c for c in chunks if len(c) > 50]
    return chunks

"""
⚡ Optional Enhancements (Only if You Want to Go Advanced)
You don’t need to implement these now, but here’s what top-tier RAG systems often add:
1️⃣ Semantic chunker (LLM or embeddings-based)
Detect paragraph/sentence groups using semantic similarity.
2️⃣ Token-based chunking (tiktoken)
Keeps chunk sizes aligned with model limits.
3️⃣ Document-structure chunking (headers, lists, sections)
Use PDF or HTML structure to split more intelligently.
4️⃣ Markdown-aware chunking
If docs include:
- bullets
- headings
- numbered lists
5️⃣ Add metadata per chunk (page number, section)
Enhances both reranking and answer explainability.
"""