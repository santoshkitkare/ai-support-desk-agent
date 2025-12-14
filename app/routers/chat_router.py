##############################################################################
# Filename: 🚀 chat_router.py — The Chat Orchestration Layer
# This module:
# - Accepts chat requests
# - Manages conversation sessions
# - Logs messages to DB
# - Sends queries to the RAG engine
# - Packages the response back to the UI
# It doesn’t contain logic — it delegates to services.
# That’s exactly how API layers should be: thin, clean, predictable.
# 
# What This Router Does Right

# ✔ Thin API layer (perfect)
# ✔ Delegates business logic to services
# ✔ Clean Pydantic models
# ✔ Manages conversation memory
# ✔ Logs user + assistant messages
# ✔ Supports multi-turn chat
# ✔ Works with /chat and /chat/
# ✔ CORS-safe with OPTIONS handler
##############################################################################
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from sqlalchemy.orm import Session

from app.services.db import get_db
from app.services import chat_service
from app.services import conversation_service

from app.agents.supervisor import SupervisorAgent
from app.agents.rag_tool import RAGTool
from app.agents.query_rewriter import QueryRewriter
from app.utils.llm_client import call_llm

from app.agents.guardrail_agent import GuardrailAgent
from app.utils.llm_client import call_llm



router = APIRouter()

rag_tool = RAGTool()
rewriter = QueryRewriter(call_llm)
supervisor = SupervisorAgent(
    rag_tool=rag_tool,
    llm=call_llm,
    rewriter=rewriter,
)
guardrail = GuardrailAgent(call_llm)


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str

# 🧱 1. Request/Response Models
# 📥 ChatRequest
# Every user message must include:
# - session_id → ties multiple messages to same conversation
# - message → the actual user query
# Streamlit generates session_id once per browser.
class ChatRequest(BaseModel):
    session_id: str
    message: str


def map_confidence_level(confidence: float | None) -> str | None:
    if confidence is None:
        return None
    if confidence >= 0.8:
        return "High"
    if confidence >= 0.5:
        return "Medium"
    return "Low"


# 📤 ChatResponse
# Returned back to UI:
# - answer → LLM’s final response
# - escalate_to_human → if your prompt told LLM to escalate
# - context_docs → file names of chunks used (for explainability)
# 
# Nice trick:
# Two decorators → endpoint works with and without trailing /.
# Example:
# POST /chat
# POST /chat/
# This avoids frontend errors. Good move.
class ChatResponse(BaseModel):
    answer: str
    escalate_to_human: bool = False
    context_docs: Optional[List[str]] = None
    
    # Phase 3B additions (optional fields)
    confidence: Optional[float] = None
    confidence_level: Optional[str] = None
    escalation_reason: Optional[str] = None

# 🔌 2. The Chat Endpoint
@router.post("", response_model=ChatResponse)
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
    # 🎯 3. Chat Workflow Step-by-Step
    session_id = request.session_id
    user_msg = request.message

    # Step 1 → Validate Input
    if not session_id or not user_msg:
        raise HTTPException(status_code=400, detail="session_id and message required")

    # Step 2 → Get Conversation Record
    # If the session exists → return it.
    # If not → create a new conversation row.
    # This powers:
    # - History
    # - Analytics
    # - Multi-turn context
    # - Conversation logs
    # Get or create conversation
    conv = conversation_service.get_or_create_conversation(db, session_id)

    # Step 3 → Save User Message
    # The DB now stores:
    # role=user
    # content=user_msg
    # timestamp
    # conversation_id
    # This is what populates your “conversation history UI.”
    # Save user message
    conversation_service.add_message(
        db=db,
        conversation_id=conv.id,
        role="user",
        content=user_msg,
    )

    # Step 4 → Fetch Last 10 Messages
    # This ensures the RAG + LLM can maintain context.
    # You’re doing sliding window of last 10 messages — perfect for support bots.
    # Load conversation history (last 10 messages)
    history = conversation_service.get_history(db, conv.id, last_n=10)

    # Step 5 → RAG + LLM Pipeline
    # This function handles the heavy lifting:
    # embed query
    # search FAISS
    # rerank chunks (bge-reranker)
    # build prompt with context
    # call GPT-4o-mini
    # parse JSON
    # output answer + escalate flag
    # Run RAG + LLM
    # result = chat_service.answer_with_rag(
    #     user_query=user_msg,
    #     history=history,
    #     db=db,
    # )
    
    # 🚧 Guardrail Check (Phase 3A)
    guardrail_result = guardrail.check(user_msg)

    if not guardrail_result["allowed"]:
        conversation_service.add_message(
            db=db,
            conversation_id=conv.id,
            role="assistant",
            content=guardrail_result["reason"],
        )

        return ChatResponse(
            answer="Your request can’t be processed due to safety or privacy reasons.",
            escalate_to_human=False,
            context_docs=[],
            confidence=None,
            confidence_level=None,
            escalation_reason=guardrail_result["reason"],
        )
    
    result = supervisor.handle(
        user_query=user_msg,
        history=history,
        db=db,
    )

    # Step 6 → Store Assistant Reply
    # You are logging every AI answer → great for analytics:
    # resolution rate
    # trending questions
    # escalations
    # satisfaction tracking
    # offline evaluations
    # Store assistant reply
    conversation_service.add_message(
        db=db,
        conversation_id=conv.id,
        role="assistant",
        content=result["answer"],
    )

    # Step 7 → Return Response
    # return ChatResponse(
    #     answer=result["answer"],
    #     escalate_to_human=result["escalate_to_human"],
    #     context_docs=result.get("context_docs", []),
    # )
    return ChatResponse(
    answer=result["answer"],
    escalate_to_human=result["escalate_to_human"],
    context_docs=result.get("context_docs", []),
    confidence=result.get("confidence"),
    confidence_level=map_confidence_level(result.get("confidence")),
    escalation_reason=(
        "Low confidence in retrieved knowledge"
        if result.get("escalate_to_human")
        else None
    ),
)

    

# 🧯 8. OPTIONS Handler → CORS Preflight
# This ensures browsers don't freak out when sending CORS preflight requests:
# Streamlit → FastAPI
# POST → requires OPTIONS preflight
# OPTIONS returns 200 OK
@router.options("/")
async def options_handler():
    return {}    # This makes the preflight return 200 OK
