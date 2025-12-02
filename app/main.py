from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chat_router, docs_router, health_router

app = FastAPI(
    title="AI Support Agent",
    version="0.1.0",
    description="RAG-based AI support desk agent using company knowledge base.",
)

# CORS – allow local frontend & potential prod domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Support Agent API is running"}


# Register routers
app.include_router(health_router.router, prefix="/health", tags=["Health"])
app.include_router(docs_router.router, prefix="/docs", tags=["Documents"])
app.include_router(chat_router.router, prefix="/chat", tags=["Chat"])
