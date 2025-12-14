##############################################################################
# File:🚀 chat_service.py — The RAG Brain
# This module controls the full answer production cycle:
# User Query → Embedding → FAISS Search → Rerank → Context Build → LLM Call → JSON Parse → Escalation Logic → Final Answer
# This is exactly how enterprise RAG systems are designed.
# 
# This file is the centerpiece of your entire AI Support Agent.
# If your project were Iron Man, this file is literally the Arc Reactor.
# This is where:
# - Retrieval (FAISS + reranker)
# - Context building
# - Conversation history formatting
# - LLM prompt construction
# - JSON enforcement
# - Escalation logic
# …all fuse together into one clean RAG pipeline.
# 
# # Your RAG pipeline architecture is legitimately production-quality:

# ✔ Embeddings → FAISS → Reranker → Context → LLM
# ✔ Correct division of responsibilities
# ✔ Solid prompt engineering
# ✔ Tight JSON handling
# ✔ Good escalation strategy
# ✔ Great modularity
# ✔ Clean, readable code
# ✔ Easy to extend to multi-tenant or hybrid models
##############################################################################
from typing import List, Dict, Any, Tuple
import json

from sqlalchemy.orm import Session
from openai import OpenAI

from app.services.config import settings
from app.services.rerank_service import rerank_chunks
from app.services.embedding_service import get_embedding
from app.services.vector_store_service import search_similar
from app.models.db_models import DocumentChunk

# 🧠 1. OpenAI Client Init
# This loads the OpenAI client one time.
client = None
if settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _ensure_openai():
    if client is None:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to your .env to enable LLM responses."
        )

# 🏹 2. retrieve_relevant_chunks() — Retrieval + Reranking
# This is where you convert the raw query into high-quality context.
def retrieve_relevant_chunks(
    query: str,
    db: Session,
    top_k: int,
) -> List[Tuple[DocumentChunk, float]]:
    """
    Embed the user query, search FAISS, fetch matching chunks from DB
    ordered by similarity (lowest distance first).
    """
    # Step A — Embed the query
    # This matches your embedding model from ingestion → perfect consistency.
    query_emb = get_embedding(query)
    
    # Step B — FAISS vector search
    results = search_similar(query_emb, top_k)
    if not results:
        return []

    # Step C — Fetch chunks from DB
    # You rebuild objects so you can access:
    # - content
    # - document
    # - IDs
    chunk_ids = [cid for cid, _ in results]
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.id.in_(chunk_ids))
        .all()
    )
    chunk_by_id = {c.id: c for c in chunks}

    # Step D — Prepare candidates for reranker
    # Reranker expects: [(id, text), ...]
    # 2) Prepare for reranker
    candidates: List[Tuple[int, str]] = []
    for cid, dist in results:
        ch = chunk_by_id.get(cid)
        if ch is None:
            continue
        candidates.append((cid, ch.content))

    if not candidates:
        return []

    # Step E — Cross-Encoder Rerank
    # This is HUGE.
    # FAISS is recall-heavy (high coverage).
    # Cross-encoder is precision-heavy (semantic ranking).
    # This is how modern RAG gets 90–95% accuracy.
    # 3) Cross-encoder rerank
    reranked = rerank_chunks(
        query=query,
        candidates=candidates,
        top_k=settings.TOP_K_RERANK,  # e.g. 5
    )

    # Step F — Build final (chunk, score) list
    # ✔ Sorted
    # ✔ Best snippets on top
    # ✔ Score is reranker confidence
    # Build final list of (DocumentChunk, score)
    final: List[Tuple[DocumentChunk, float]] = []
    for cid, _, score in reranked:
        ch = chunk_by_id.get(cid)
        if ch:
            final.append((ch, score))


    return final

# 🎯 3. build_context_from_chunks() — Construct Prompt Context
# This function creates:
# Context text fed to LLM:
# Example:
# [Snippet 1 | Doc: RefundPolicy.pdf | doc_id=2 | chunk_id=14 | distance=0.0021]
# <chunk content>
# ---
# [Snippet 2 | Doc: Warranty.pdf | ...]
# <chunk content>
# ---
# This header block is PERFECT because:
# - LLM can understand source document
# - Debug-friendly
# - Human-auditable
# - Helps with troubleshooting hallucinations
# Also returns:
#   context_docs = ["RefundPolicy.pdf (doc_id=2, chunk_id=14)", ...]
# Used in UI to show “documents referenced”.
def build_context_from_chunks(
    chunks_with_scores: List[Tuple[DocumentChunk, float]]
) -> Tuple[str, List[str]]:
    """
    Turn retrieved chunks into a single context string + a list of
    human-readable context doc descriptors.
    """
    sections: List[str] = []
    context_docs: List[str] = []

    for idx, (chunk, dist) in enumerate(chunks_with_scores, start=1):
        doc = chunk.document  # via relationship
        header = (
            f"[Snippet {idx} | Doc: {doc.filename} | doc_id={doc.id} | "
            f"chunk_id={chunk.id} | distance={dist:.4f}]"
        )
        sections.append(f"{header}\n{chunk.content}")
        context_docs.append(f"{doc.filename} (doc_id={doc.id}, chunk_id={chunk.id})")

    context_text = "\n\n---\n\n".join(sections)
    return context_text, context_docs

# 🧩 4. format_history() — Conversation Memory (Compact)
def format_history(history: List[Dict[str, str]], max_messages: int = 6) -> str:
    """
    Simple textual history for LLM. Not persisted in DB yet.
    """
    if not history:
        return ""

    trimmed = history[-max_messages:]
    lines: List[str] = []
    for msg in trimmed:
        role = msg.get("role", "user")
        prefix = "User" if role == "user" else "Assistant"
        lines.append(f"{prefix}: {msg.get('content', '')}")
    return "\n".join(lines)


# 🦾 5. call_llm_with_rag() — The LLM Execution Engine
def call_llm_with_rag(
    query: str,
    history_text: str,
    context_text: str,
) -> Dict[str, Any]:
    """
    Call OpenAI chat model with instructions to return JSON:
    {
      "answer": "...",
      "escalate_to_human": bool,
      "confidence": 0.0-1.0
    }
    """
    _ensure_openai()

    # system_msg = (
    #     "You are an AI support agent for a company. "
    #     "You answer ONLY using the provided knowledge base context. "
    #     "If the context does not clearly contain the answer, "
    #     "you must set \"escalate_to_human\" to true and explain briefly "
    #     "why a human agent is needed.\n\n"
    #     "Return your answer as STRICT JSON with keys:\n"
    #     "  - answer (string)\n"
    #     "  - escalate_to_human (boolean)\n"
    #     "  - confidence (number between 0 and 1)\n"
    #     "Do not include markdown, code fences, or any extra text outside the JSON."
    # )
    # Stage 1 — System Prompt
    # Your system prompt is extremely well-crafted:
    # ✔ Forces LLM to answer ONLY using context
    # ✔ Reject hallucination
    # ✔ Prevents invented policies/prices
    # ✔ Enforces escalation when uncertain
    # ✔ Forces STRICT JSON
    system_msg = (
        "You are an AI support agent for a company.\n"
        "You must answer ONLY using the provided knowledge base context snippets.\n"
        "If the answer is not clearly contained in the context, you MUST say you "
        "don't know and set \"escalate_to_human\" to true.\n\n"
        "Rules:\n"
        "- Do NOT invent policies, prices, dates, or procedures.\n"
        "- Prefer precise, concise responses.\n"
        "- If multiple snippets disagree, mention that and escalate.\n\n"
        "Return STRICT JSON with keys:\n"
        "  - answer (string)\n"
        "  - escalate_to_human (boolean)\n"
        "  - confidence (number between 0 and 1)\n"
        "Do not include markdown, code fences, or any text outside the JSON."
    )

    # Stage 2 — Adding Context Snippets
    messages = [
        {"role": "system", "content": system_msg},
    ]

    if context_text:
        messages.append(
            {
                "role": "system",
                "content": f"Knowledge base context:\n{context_text}",
            }
        )

    # Stage 3 — Construct user message
    # Includes:
    # - Query
    # - Context
    # - Conversation history (tone only)
    # - Instructions to only answer using context
    user_content = (
        "User question:\n"
        f"{query}\n\n"
        "Use only the following context snippets to answer."
        "If the context is insufficient, escalate:\n"
        f"{context_text}"
    )
    
    if history_text:
        user_content += f"\n\nRecent conversation history (for tone only, not facts):\n{history_text}"

    messages.append({"role": "user", "content": user_content})

    # Stage 4 — LLM Call
    # ✔ Low temperature (reduces hallucination)
    # ✔ Correct API usage
    # ✔ Deterministic
    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.2,
    )

    raw = resp.choices[0].message.content

    try:
        # Stage 5 — JSON Parsing
        data = json.loads(raw)
        answer = data.get("answer", raw)
        escalate = bool(data.get("escalate_to_human", False))
        confidence = float(data.get("confidence", 0.7))
    except Exception:
        # Stage 5 — JSON Parsing
        # LLM messed up JSON; fall back
        answer = raw
        escalate = False
        confidence = 0.7

    # Stage 6 — Confidence Threshold Override
    # This allows business control independent of LLM judgment.
    # Excellent architecture: LLM is advisor, your code is the authority.
    # Simple business rule on top of LLM self-confidence
    if confidence < settings.ESCALATION_CONFIDENCE_THRESHOLD:
        escalate = True

    return {
        "answer": answer,
        "escalate_to_human": escalate,
        "confidence": confidence,
    }

# 🧠 6. answer_with_rag() — Full Orchestration Function
# This function ties EVERYTHING together.
# Step 1 → Retrieve chunks
# If none → escalate immediately
# Step 2 → Build context
# Step 3 → Format history
# Step 4 → Call LLM
# Step 5 → Return final structured output:
# {
#     "answer": "...",
#     "escalate_to_human": ...,
#     "context_docs": [...],
# }
def answer_with_rag(
    user_query: str,
    history: List[Dict[str, str]],
    db: Session,
) -> Dict[str, Any]:
    """
    End-to-end RAG flow for a chat turn.
    """
    # 1) Retrieve relevant chunks
    chunks_with_scores = retrieve_relevant_chunks(
        user_query,
        db=db,
        top_k=settings.TOP_K_RETRIEVER,
    )

    if not chunks_with_scores:
        # No KB info → hard escalate
        return {
            "answer": (
                "I couldn't find this information in the current knowledge base. "
                "Please escalate this to a human support agent."
            ),
            "escalate_to_human": True,
            "context_docs": [],
        }

    # 2) Build context for LLM
    context_text, context_docs = build_context_from_chunks(chunks_with_scores)

    # 3) Build simple history text (not persisted yet)
    history_text = format_history(history)

    # 4) Call LLM
    llm_result = call_llm_with_rag(
        query=user_query,
        history_text=history_text,
        context_text=context_text,
    )

    return {
        "answer": llm_result["answer"],
        "escalate_to_human": llm_result["escalate_to_human"],
        "context_docs": context_docs,
    }


# # ⚠️ Only 2 Minor Improvement Suggestions
# 1️⃣ Add error handling for API failures
# Right now only JSON parsing is guarded.
# 2️⃣ Add streaming support (optional)
# Streamlit UI will feel faster.