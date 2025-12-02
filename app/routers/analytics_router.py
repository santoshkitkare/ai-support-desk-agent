from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.services.db import get_db
from app.models.db_models import Conversation, Message

router = APIRouter()

@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    total_conversations = db.query(Conversation).count()
    total_messages = db.query(Message).count()
    escalated = (
        db.query(Message)
        .filter(Message.role == "assistant")
        .filter(Message.content.ilike("%escalate%human%"))
        .count()
    )
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
