##############################################################################
# File: 🚀 conversation_service.py — Conversation Memory Manager
# This service abstracts all conversation-related DB operations.
# 
# This is your conversation memory service — the layer that makes your bot 
# “remember” past messages, group them by session, and feed history into RAG.
# It’s not glamorous, but it is mission-critical for:
# - multi-turn chat
# - analytics
# - replay
# - debugging
# - escalating conversations
# - preserving tone
from sqlalchemy.orm import Session

from app.models.db_models import Conversation, Message

# 🧱 1. get_or_create_conversation()
# ✔ What it does:
# - Finds existing conversation by session_id
# - If none → creates one
# - Returns a Conversation row with a unique DB ID
# 🎯 Why it’s important:
# Your Streamlit UI generates a session_id per browser instance.
# Every message is tied back to this conversation row.
# This enables:
# - History
# - Analytics
# - Filtering
# - Identifying who asked what
# - Multi-turn RAG
def get_or_create_conversation(db: Session, session_id: str) -> Conversation:
    conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if conv:
        return conv

    conv = Conversation(session_id=session_id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


# 📝 2. add_message()
# ✔ Stores each message in DB:
# - conversation_id
# - role → "user" or "assistant"
# - content → message text
# 🧩 Why this matters:
# Your RAG pipeline uses conversation history to maintain tone and avoid repeating answers.
# Analytics dashboard uses these logs to:
# - compute resolution rate
# - track escalations
# - show last 5 questions
# - show trending topics
# This table is the audit trail of your AI system.
def add_message(db: Session, conversation_id: int, role: str, content: str):
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    db.add(msg)
    db.commit()
    return msg

# 🧠 3. get_history()
# ✔ What it does:
# Retrieves the last N messages of a conversation.
# ⚠️ Small observation:
# .limit(last_n) with order_by(id.asc()) returns the first 10 messages, not last 10.
# Example:
# Messages: ids 1,2,3,4,5
# limit(3) → 1,2,3
# NOT 3,4,5
# 📌 The correct behavior for “last N messages” is:
# Either:
# Sort descending then limit:
#   .order_by(Message.id.desc()).limit(last_n)
# then reverse the list.
# Or:
# Use offset if total count available.
# 
# But for your small-scale support bot, this is not critical unless you want the most recent messages to influence tone.
def get_history(db: Session, conversation_id: int, last_n: int = 10):
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.id.asc())
        .limit(last_n)
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in msgs]
