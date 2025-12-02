from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

router = APIRouter()

@router.post("/upload")
async def upload_docs(files: List[UploadFile] = File(...)):
    """
    Upload one or more documents (PDF, DOCX, CSV) to the knowledge base.
    Later: store file, parse, chunk, embed, add to FAISS.
    """
    # For now, just return filenames to confirm flow works
    filenames = [f.filename for f in files]
    if not filenames:
        raise HTTPException(status_code=400, detail="No files uploaded")

    return {"uploaded_files": filenames, "message": "Stub endpoint - ingestion coming soon"}
