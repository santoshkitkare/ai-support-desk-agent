from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chat_router, docs_router, health_router
from app.services.db import init_db
from app.routers import analytics_router

app = FastAPI(
    title="AI Support Agent",
    version="0.1.0",
    description="RAG-based AI support desk agent using company knowledge base.",
)

# CORS – allow local frontend & potential prod domain
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # for dev; tighten later
    allow_origins=["*", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Support Agent API is running"}

# Register routers
app.include_router(health_router.router, prefix="/health", tags=["Health"])
app.include_router(docs_router.router, prefix="/docs", tags=["Documents"])
app.include_router(chat_router.router, prefix="/chat", tags=["Chat"])
app.include_router(analytics_router.router, prefix="/analytics", tags=["Analytics"])
