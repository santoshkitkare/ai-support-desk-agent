import os
import shutil
from typing import List, Tuple

from fastapi import UploadFile

from sqlalchemy.orm import Session

from app.services.config import settings
from app.models.db_models import Document, DocumentChunk
from app.utils.pdf_parser import extract_text_from_pdf
from app.utils.docx_parser import extract_text_from_docx
from app.utils.csv_parser import extract_text_from_csv
from app.utils.chunking import simple_split
from app.services.embedding_service import get_embeddings
from app.services.vector_store_service import add_embeddings, init_index


os.makedirs(settings.RAW_DOCS_DIR, exist_ok=True)


def _save_upload_to_disk(upload: UploadFile) -> Tuple[str, str]:
    filename = upload.filename
    ext = (os.path.splitext(filename)[1] or "").lower()
    dest_path = os.path.join(settings.RAW_DOCS_DIR, filename)

    # Avoid overwrite: simple dedupe
    base, extension = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        filename = f"{base}_{counter}{extension}"
        dest_path = os.path.join(settings.RAW_DOCS_DIR, filename)
        counter += 1

    with open(dest_path, "wb") as out_file:
        shutil.copyfileobj(upload.file, out_file)

    return dest_path, ext


def _extract_text_by_ext(path: str, ext: str) -> str:
    if ext in [".pdf"]:
        return extract_text_from_pdf(path)
    elif ext in [".docx"]:
        return extract_text_from_docx(path)
    elif ext in [".csv"]:
        return extract_text_from_csv(path)
    else:
        # fallback: plain text
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def ingest_uploaded_files(files: List[UploadFile], db: Session) -> List[int]:
    """
    Main ingestion pipeline:
    - Save file
    - Create Document record
    - Parse text
    - Chunk
    - Embed chunks
    - Store chunks in DB
    - Add embeddings to FAISS (id = chunk.id)
    Returns list of document IDs.
    """
    from app.services.config import settings  # to avoid circular import

    created_document_ids: List[int] = []

    for upload in files:
        path, ext = _save_upload_to_disk(upload)
        file_type = ext.replace(".", "") or "txt"

        # Create Document row
        doc = Document(
            filename=os.path.basename(path),
            original_path=path,
            file_type=file_type,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Extract & chunk
        text = _extract_text_by_ext(path, ext)
        chunks = simple_split(text, max_tokens=500, overlap=50)

        if not chunks:
            # no text; skip this doc
            continue

        # Create DB rows for chunks
        chunk_rows: List[DocumentChunk] = []
        for idx, chunk_text in enumerate(chunks):
            chunk_row = DocumentChunk(
                document_id=doc.id,
                chunk_index=idx,
                content=chunk_text,
            )
            db.add(chunk_row)
            chunk_rows.append(chunk_row)

        db.commit()

        # refresh to get IDs
        for ch in chunk_rows:
            db.refresh(ch)

        # Make embeddings
        texts_for_embeddings = [ch.content for ch in chunk_rows]
        embeddings = get_embeddings(texts_for_embeddings)

        # Init FAISS index if needed
        if embeddings:
            init_index(embedding_dim=len(embeddings[0]))

        # Map FAISS vectors to chunk IDs
        chunk_ids = [ch.id for ch in chunk_rows]
        add_embeddings(chunk_ids, embeddings)

        created_document_ids.append(doc.id)

    return created_document_ids
