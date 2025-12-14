##############################################################################
# File: analytics_router.py — Your Observability & Reporting Layer
# This endpoint gives your Streamlit dashboard the power to display:
# - total conversation volumes
# - escalation rates
# - trending user questions
# - basic message analytics
# It’s lightweight, fast, and fits perfectly with your schema.
# This is short but strategically super important because it powers your dashboard, visibility, metrics, and portfolio story.
#
# This Analytics Layer Is Perfect for Your MVP

# Your analytics router:

# ✔ Tracks meaningful KPIs
# ✔ Uses clean SQLAlchemy queries
# ✔ Works instantly with your DB schema
# ✔ Supports your Streamlit dashboard
# ✔ Helps debug, evaluate, and improve your RAG system
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.services.db import get_db
from app.models.db_models import Conversation, Message

router = APIRouter()

# 📊 1. /analytics/summary — The KPI Endpoint
# This endpoint compiles operational metrics for your AI system.
@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    # Every conversation_id = one chat session.
    total_conversations = db.query(Conversation).count()
    
    # Good proxy for:
    # - user engagement
    # - average session length
    # - overall system usage
    total_messages = db.query(Message).count()
    
    # ✔ Escalated Conversations
    escalated = (
        db.query(Message)
        .filter(Message.role == "assistant")
        .filter(Message.content.ilike("%escalate%human%"))
        .count()
    )
    
    # ✔ Resolution Rate
    # Then formatted as %.
    # This shows:
    # - How often the AI could answer without human help
    # - Core metric in customer support automation
    resolution_rate = (
        0 if total_conversations == 0
        else round(100 * (total_conversations - escalated) / total_conversations, 2)
    )

    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "escalated_conversations": escalated,
        "resolution_rate": f"{resolution_rate}%",
    }

# 🔥 2. /analytics/trending-queries — Recent User Questions
# This gives the latest 50 user questions.
# Useful for:
# - spotting common user pain points
# - discovering missing documentation
# - tuning the RAG model
# - improving FAQs
# - marketing insights
@router.get("/trending-queries")
def trending_queries(db: Session = Depends(get_db)):
    rows = (
        db.query(Message.content)
        .filter(Message.role == "user")
        .order_by(Message.id.desc())
        .limit(50)
        .all()
    )
    return {"latest_user_queries": [r[0] for r in rows]}

"""
1️⃣ Store escalation flag in DB (avoid string matching)
You already compute:
"escalate_to_human": True/False
You could store that in the DB in the Message table or Conversation table.
2️⃣ Add response time metrics
Useful for diagnosing slow RAG operations.
3️⃣ Add "documents referenced" histogram
Which documents are used most?
4️⃣ Add conversation duration & average messages per session
This helps UX improvement and tuning.
5️⃣ Add Heatmap of peak usage times
Great for dashboards.
"""