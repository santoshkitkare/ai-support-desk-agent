import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.db_models import Base
from app.services.config import settings

# SQLite in data dir
os.makedirs(settings.DATA_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(settings.DATA_DIR, 'ai_support.db')}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


# FastAPI dependency
from typing import Generator

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
