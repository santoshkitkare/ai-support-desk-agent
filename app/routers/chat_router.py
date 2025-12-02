from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    session_id: Optional[str] = None  # future: for conversation tracking
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    answer: str
    escalate_to_human: bool = False
    context_docs: Optional[List[str]] = None  # snippet titles or ids


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    For now: just echo last user message with a stub response.
    Later: RAG + LLM + escalate_to_human.
    """
    last_user_msg = next((m.content for m in reversed(request.messages) if m.role == "user"), "")
    dummy_answer = f"(Stub) You said: {last_user_msg}. RAG + LLM integration is coming."

    return ChatResponse(
        answer=dummy_answer,
        escalate_to_human=False,
        context_docs=[]
    )
