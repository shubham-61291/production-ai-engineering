import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.core.auth import validate_api_key
from app.core.limiter import limiter
from app.core.config import settings
from app.core.rag import rag_store

router = APIRouter()
logger = logging.getLogger(__name__)

class DeleteResponse(BaseModel):
    doc_id: str
    message: str

@router.delete("/delete/{doc_id}", response_model=DeleteResponse, dependencies=[Depends(validate_api_key)])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def delete_document(request: Request, doc_id: str):
    try:
        rag_store.delete_document(doc_id)
        return DeleteResponse(
            doc_id=doc_id,
            message=f"Document {doc_id} deleted successfully from vector and BM25 indices."
        )
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
