##################################################################
# file: app/main.py
# It doesn't do any heavy lifting — but it dictates the entire system architecture.

# ✔ Wires all routers
# ✔ Sets up DB
# ✔ Enables frontend communication
# ✔ Establishes API identity
# ✔ Boots the service cleanly

# This is your entrypoint, not your brain.
# The “brain” lives inside the services/* modules we’ll explore next.
###################################################################
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chat_router, docs_router, health_router
from app.services.db import init_db
from app.routers import analytics_router

"""
# 🧠 1. FastAPI App Initialization
📌 What this does:
Bootstraps your REST API service.
Exposes metadata → automatically reflected in /docs Swagger UI.
Gives clients (frontend, automation scripts, Postman) a clear contract.
🔥 Why it matters:
This is your API identity layer — it informs tools, clients, and devs what's up.
"""
app = FastAPI(
    title="AI Support Agent",
    version="0.1.0",
    description="RAG-based AI support desk agent using company knowledge base.",
)
"""
🌐 2. CORS Middleware Setup
📌 What’s going on:
* Allows your Streamlit UI (running on 8501) to talk to the FastAPI backend.
* opens the door to every domain → okay for dev, tighten in prod.
🔥 Why this matters:

Without this, your frontend can't hit your backend because browsers enforce CORS.
This middleware bridges the gap between Streamlit → FastAPI.

CORS, or Cross-Origin Resource Sharing, is the browser security mechanism that governs 
whether a web page running in one origin is permitted to access resources from another origin
"""
# CORS – allow local frontend & potential prod domain
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # for dev; tighten later
    allow_origins=["*", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
🗄️ 3. Startup Event — DB Initialization
📌 What this triggers:
Runs init_db() right when the server boots.
Creates tables if not present.
Initializes SQLite/PostgreSQL connection.

🔥 Why this matters:
This ensures all database tables exist before any API call.
No startup = no persistence, no documents, no vector metadata, no conversation logs.
This is your infrastructure bootstrapper.
"""
@app.on_event("startup")
def on_startup():
    init_db()

"""
🏠 4. Root Health Check Endpoint
📌 Why it exists:
Quick sanity check for deployment environments (Docker, AWS EC2, Render).
Frontend (Streamlit) can ping this during startup.
Monitoring systems use it for readiness checks.
"""
@app.get("/")
def root():
    return {"status": "ok", "message": "AI Support Agent API is running"}

"""
🔌 5. Router Registration — The Actual API Surface
This is where your entire backend capabilities get wired in:
"""
# Register routers
app.include_router(health_router.router, prefix="/health", tags=["Health"])
app.include_router(docs_router.router, prefix="/docs", tags=["Documents"])
app.include_router(chat_router.router, prefix="/chat", tags=["Chat"])
app.include_router(analytics_router.router, prefix="/analytics", tags=["Analytics"])
