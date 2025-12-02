from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List

from sqlalchemy.orm import Session

from app.services.db import get_db
from app.services.ingestion_service import ingest_uploaded_files

router = APIRouter()


@router.post("/upload")
async def upload_docs(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload one or more documents (PDF, DOCX, CSV, TXT) to the knowledge base.
    Performs full ingestion: parse, chunk, embed, index in FAISS.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    doc_ids = ingest_uploaded_files(files, db)

    if not doc_ids:
        raise HTTPException(status_code=400, detail="No valid text extracted from files")

    return {
        "message": "Documents ingested successfully",
        "document_ids": doc_ids,
        "count": len(doc_ids),
    }
