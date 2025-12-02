from sqlalchemy.orm import Session

from app.models.db_models import Conversation, Message


def get_or_create_conversation(db: Session, session_id: str) -> Conversation:
    conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if conv:
        return conv

    conv = Conversation(session_id=session_id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def add_message(db: Session, conversation_id: int, role: str, content: str):
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    db.add(msg)
    db.commit()
    return msg


def get_history(db: Session, conversation_id: int, last_n: int = 10):
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.id.asc())
        .limit(last_n)
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in msgs]
