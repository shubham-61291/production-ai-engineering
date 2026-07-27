import logging
import os
import shutil
import tempfile
import time
import asyncio
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from app.core.limiter import limiter
from uuid import uuid4
from app.models.schemas import UploadResponse
from app.core.rag import store_chunks
from app.core.utils import upload_to_gcs
from app.core.config import settings
from app.core.document_parser import extract_text_from_file, chunk_text
from app.core.auth import validate_api_key

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=UploadResponse)
@limiter.limit("50/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    session_id: Optional[str] = None,
    api_key: str = Depends(validate_api_key)
):
    if not session_id:
        session_id = str(uuid4())

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".pdf", ".docx", ".txt", ".md"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        raw_text = extract_text_from_file(tmp_path, ext)
        if not raw_text:
            raise HTTPException(status_code=400, detail="No text extracted")

        chunks = chunk_text(raw_text)
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks produced")

        now = time.time()
        chunk_objs = []
        for idx, chunk in enumerate(chunks):
            chunk_objs.append({
                "text": chunk,
                "filename": file.filename,
                "chunk_index": idx,
                "timestamp": now
            })

        count = await asyncio.to_thread(store_chunks, chunk_objs, session_id)

        public_url = None
        if settings.GCS_BUCKET_NAME:
            try:
                gcs_path = f"uploads/{session_id}/{file.filename}"
                public_url = await asyncio.to_thread(upload_to_gcs, tmp_path, gcs_path)
            except Exception as e:
                logger.error(f"GCS upload failed: {e}")

        return UploadResponse(
            status="success",
            chunks_uploaded=count,
            file_url=public_url
        )

    finally:
        os.unlink(tmp_path)
