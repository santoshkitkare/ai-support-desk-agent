from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from sqlalchemy.orm import Session

from app.services.db import get_db
from app.services import chat_service


router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    session_id: Optional[str] = None  # will be used later when we persist history
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    answer: str
    escalate_to_human: bool = False
    context_docs: Optional[List[str]] = None


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    Main chat endpoint with RAG:
    - Embed last user message
    - Retrieve relevant chunks from FAISS
    - Ask LLM with KB context
    - Return answer + escalate flag + context doc references
    """
    # Get latest user message
    user_msg = next(
        (m.content for m in reversed(request.messages) if m.role == "user"),
        None,
    )
    if not user_msg:
        raise HTTPException(status_code=400, detail="No user message provided")

    history = [{"role": m.role, "content": m.content} for m in request.messages]

    result = chat_service.answer_with_rag(
        user_query=user_msg,
        history=history,
        db=db,
    )

    return ChatResponse(
        answer=result["answer"],
        escalate_to_human=result["escalate_to_human"],
        context_docs=result.get("context_docs", []),
    )
