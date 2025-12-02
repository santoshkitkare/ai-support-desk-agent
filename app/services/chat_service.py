from typing import List, Dict, Any, Tuple
import json

from sqlalchemy.orm import Session
from openai import OpenAI

from app.services.config import settings
from app.services.embedding_service import get_embedding
from app.services.vector_store_service import search_similar
from app.models.db_models import DocumentChunk

client = None
if settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _ensure_openai():
    if client is None:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to your .env to enable LLM responses."
        )


def retrieve_relevant_chunks(
    query: str,
    db: Session,
    top_k: int,
) -> List[Tuple[DocumentChunk, float]]:
    """
    Embed the user query, search FAISS, fetch matching chunks from DB
    ordered by similarity (lowest distance first).
    """
    query_emb = get_embedding(query)
    results = search_similar(query_emb, top_k)
    if not results:
        return []

    chunk_ids = [cid for cid, _ in results]
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.id.in_(chunk_ids))
        .all()
    )
    chunk_by_id = {c.id: c for c in chunks}

    # Re-order to match FAISS ranking
    ordered: List[Tuple[DocumentChunk, float]] = []
    for cid, dist in results:
        chunk = chunk_by_id.get(cid)
        if chunk is not None:
            ordered.append((chunk, dist))

    return ordered


def build_context_from_chunks(
    chunks_with_scores: List[Tuple[DocumentChunk, float]]
) -> Tuple[str, List[str]]:
    """
    Turn retrieved chunks into a single context string + a list of
    human-readable context doc descriptors.
    """
    sections: List[str] = []
    context_docs: List[str] = []

    for chunk, dist in chunks_with_scores:
        doc = chunk.document  # via relationship
        header = (
            f"[Doc: {doc.filename} | doc_id={doc.id} | "
            f"chunk_id={chunk.id} | distance={dist:.4f}]"
        )
        sections.append(f"{header}\n{chunk.content}")
        context_docs.append(f"{doc.filename} (doc_id={doc.id}, chunk_id={chunk.id})")

    context_text = "\n\n---\n\n".join(sections)
    return context_text, context_docs


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

    system_msg = (
        "You are an AI support agent for a company. "
        "You answer ONLY using the provided knowledge base context. "
        "If the context does not clearly contain the answer, "
        "you must set \"escalate_to_human\" to true and explain briefly "
        "why a human agent is needed.\n\n"
        "Return your answer as STRICT JSON with keys:\n"
        "  - answer (string)\n"
        "  - escalate_to_human (boolean)\n"
        "  - confidence (number between 0 and 1)\n"
        "Do not include markdown, code fences, or any extra text outside the JSON."
    )

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

    user_content = f"User question:\n{query}"
    if history_text:
        user_content += f"\n\nConversation history:\n{history_text}"

    messages.append({"role": "user", "content": user_content})

    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.2,
    )

    raw = resp.choices[0].message.content

    try:
        data = json.loads(raw)
        answer = data.get("answer", raw)
        escalate = bool(data.get("escalate_to_human", False))
        confidence = float(data.get("confidence", 0.7))
    except Exception:
        # LLM messed up JSON; fall back
        answer = raw
        escalate = False
        confidence = 0.7

    # Simple business rule on top of LLM self-confidence
    if confidence < settings.ESCALATION_CONFIDENCE_THRESHOLD:
        escalate = True

    return {
        "answer": answer,
        "escalate_to_human": escalate,
        "confidence": confidence,
    }


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
        top_k=settings.TOP_K,
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
