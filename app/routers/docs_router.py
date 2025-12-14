#######################################################################
# file: docs_router.py
# 🚀 docs_router.py — The Document Onboarding Gateway
# Think of this router as your “Document HR Department.”
# Every PDF, DOCX, CSV, or TXT entering the system gets vetted and handed off for processing.

# 📌 What this module does:
# - Accepts uploaded documents via REST API
# - Validates incoming files
# - Injects them into the ingestion pipeline
# - Returns document IDs
# - Surfaces errors if extraction fails
# - Nothing fancy — but it’s the front door to your knowledge base.
# 
# What This Router Actually Owns
# It handles:
# - Upload request validation
# - DB session injection
# - Delegating ingestion
# - Error reporting
# - Success response shaping

# It does NOT handle:
# - Parsing
# - Chunking
# - Embedding
# - FAISS indexing
# All of that is intentionally abstracted inside the ingestion service → this keeps routers clean and maintainable.
#########################################################################
# 1️⃣ Import Layer
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List

from sqlalchemy.orm import Session

from app.services.db import get_db
from app.services.ingestion_service import ingest_uploaded_files
"""
What’s happening:
- APIRouter → allows modular endpoint grouping
- UploadFile + File → handles streaming file uploads
- Depends(get_db) → injects SQLAlchemy DB session
- ingest_uploaded_files → triggers full ingestion pipeline
This router doesn’t do any heavy lifting — it delegates.
"""
# 2️⃣ Router Initialization
# A fresh router group that later gets registered in main.py under: /docs
router = APIRouter()

# 3️⃣ Upload Endpoint Definition
# 🔍 Breakdown:
# - POST /docs/upload
# -Accepts multiple files (List[UploadFile])
# - DB session injected automatically
# - async allows efficient file streaming
# Why async matters:
# You’ll avoid blocking the server when users upload large PDFs.
@router.post("/upload")
async def upload_docs(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload one or more documents (PDF, DOCX, CSV, TXT) to the knowledge base.
    Performs full ingestion: parse, chunk, embed, index in FAISS.
    """
    # 4️⃣ Validation — Zero Files Check
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # 5️⃣ Core Processing Call
    # This triggers the entire pipeline:
    # 🔥 Inside ingestion service (what this call actually does):
    # 1. Reads PDFs, DOCX, CSV, TXT
    # 2. Extracts raw text
    # 3. Cleans text
    # 4. Chunks it
    # 5. Embeds chunks using BGE-small
    # 6. Saves chunks to DB
    # 7. Saves embeddings to FAISS
    # 8. Returns final document IDs
    # This is where the horsepower lives — this router is just the dispatcher.
    doc_ids = ingest_uploaded_files(files, db)

    # 6️⃣ Handle No-Text Case
    # This prevents garbage documents (empty PDFs, image-only scans) from polluting your vector DB.
    if not doc_ids:
        raise HTTPException(status_code=400, detail="No valid text extracted from files")

    # 7️⃣ Final Success Response
    return {
        "message": "Documents ingested successfully",
        "document_ids": doc_ids,
        "count": len(doc_ids),
    }
