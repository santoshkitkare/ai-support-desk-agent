from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from sqlalchemy.orm import Session

from app.services.db import get_db
from app.services import chat_service
from app.services import conversation_service

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str

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
    session_id = request.session_id
    user_msg = request.message

    if not session_id or not user_msg:
        raise HTTPException(status_code=400, detail="session_id and message required")

    # Get or create conversation
    conv = conversation_service.get_or_create_conversation(db, session_id)

    # Save user message
    conversation_service.add_message(
        db=db,
        conversation_id=conv.id,
        role="user",
        content=user_msg,
    )

    # Load conversation history (last 10 messages)
    history = conversation_service.get_history(db, conv.id, last_n=10)

    # Run RAG + LLM
    result = chat_service.answer_with_rag(
        user_query=user_msg,
        history=history,
        db=db,
    )

    # Store assistant reply
    conversation_service.add_message(
        db=db,
        conversation_id=conv.id,
        role="assistant",
        content=result["answer"],
    )

    return ChatResponse(
        answer=result["answer"],
        escalate_to_human=result["escalate_to_human"],
        context_docs=result.get("context_docs", []),
    )
    

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    session_id = request.session_id
    user_msg = request.message

    if not session_id or not user_msg:
        raise HTTPException(status_code=400, detail="session_id and message required")

    # Get or create conversation
    conv = conversation_service.get_or_create_conversation(db, session_id)

    # Save user message
    conversation_service.add_message(
        db=db,
        conversation_id=conv.id,
        role="user",
        content=user_msg,
    )

    # Load recent history
    history = conversation_service.get_history(db, conv.id, last_n=10)

    # RAG + LLM
    result = chat_service.answer_with_rag(
        user_query=user_msg,
        history=history,
        db=db,
    )

    # Save assistant message
    conversation_service.add_message(
        db=db,
        conversation_id=conv.id,
        role="assistant",
        content=result["answer"],
    )

    return ChatResponse(
        answer=result["answer"],
        escalate_to_human=result["escalate_to_human"],
        context_docs=result["context_docs"],
    )
