import os
import uuid
import re
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel

from app.core.auth import validate_api_key
from app.core.limiter import limiter
from app.core.config import settings
from app.core.rag import rag_store

router = APIRouter()
logger = logging.getLogger(__name__)

class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunks_created: int
    message: str

def sanitize_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return filename

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())
        i += (chunk_size - overlap)
    return chunks if chunks else [text]

@router.post("/upload", response_model=UploadResponse, dependencies=[Depends(validate_api_key)])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def upload_document(
    request: Request,
    file: UploadFile = File(...)
):
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File size exceeds limit of {settings.MAX_UPLOAD_SIZE_MB}MB")

    safe_name = sanitize_filename(file.filename or "uploaded_doc.txt")
    doc_id = str(uuid.uuid4())

    try:
        if safe_name.endswith(".pdf"):
            import pypdf
            import io
            reader = pypdf.PdfReader(io.BytesIO(content))
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif safe_name.endswith(".docx"):
            import docx
            import io
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([p.text for p in doc.paragraphs if p.text])
        else:
            text = content.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"Error parsing document {safe_name}: {e}")
        text = content.decode("utf-8", errors="ignore")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text content from file.")

    chunks = chunk_text(text)
    metadata = {
        "filename": safe_name,
        "content_type": file.content_type or "text/plain",
        "file_size": len(content)
    }

    rag_store.add_chunks(doc_id=doc_id, chunks=chunks, metadata=metadata)

    return UploadResponse(
        doc_id=doc_id,
        filename=safe_name,
        chunks_created=len(chunks),
        message="Document uploaded and indexed successfully."
    )
