import time
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.auth import validate_api_key
from app.core.limiter import limiter
from app.core.config import settings
from app.core.cache import redis_cache
from app.core.rag import rag_store
from app.core.utils import get_http_client

router = APIRouter()
logger = logging.getLogger(__name__)

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question for the LLM RAG engine")
    temperature: Optional[float] = Field(default=settings.DEFAULT_TEMPERATURE, ge=0.0, le=2.0)
    seed: Optional[int] = Field(default=settings.DEFAULT_SEED)
    max_tokens: Optional[int] = Field(default=settings.DEFAULT_MAX_TOKENS, ge=1, le=4096)
    top_k: Optional[int] = Field(default=5, ge=1, le=20)

class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[dict]
    cached: bool
    prompt_injection_detected: bool
    latency_seconds: float

def check_prompt_injection(text: str) -> bool:
    suspicious_patterns = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "system prompt",
        "you are now DAN",
        "override safety filters"
    ]
    low_text = text.lower()
    for pattern in suspicious_patterns:
        if pattern in low_text:
            return True
    return False

@router.post("/ask", response_model=AskResponse, dependencies=[Depends(validate_api_key)])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def ask_question(request: Request, body: AskRequest):
    start_time = time.time()
    
    # 1. Prompt Injection Guard
    is_injection = check_prompt_injection(body.question)
    if is_injection:
        return AskResponse(
            question=body.question,
            answer="Security policy violation: Potential prompt injection detected.",
            sources=[],
            cached=False,
            prompt_injection_detected=True,
            latency_seconds=round(time.time() - start_time, 4)
        )

    # 2. Retrieve Context via RAG (Chroma + BM25)
    context_chunks = rag_store.search(query=body.question, top_k=body.top_k)

    # 3. Check Redis Cache
    cache_key = redis_cache.make_key(
        question=body.question,
        context_chunks=context_chunks,
        temperature=body.temperature,
        max_tokens=body.max_tokens
    )
    cached_response = await redis_cache.get(cache_key)
    if cached_response:
        return AskResponse(
            question=body.question,
            answer=cached_response,
            sources=context_chunks,
            cached=True,
            prompt_injection_detected=False,
            latency_seconds=round(time.time() - start_time, 4)
        )

    # 4. Synthesize Answer via Ollama API
    context_text = "\n\n".join([f"Source [{i+1}]: {c['text']}" for i, c in enumerate(context_chunks)])
    prompt = (
        f"You are Magnetar AI, a security-hardened assistant.\n"
        f"Answer the user's question accurately using only the provided context below.\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {body.question}\nAnswer:"
    )

    try:
        client = get_http_client()
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": body.temperature,
                "seed": body.seed,
                "num_predict": body.max_tokens
            }
        }
        res = await client.post(f"{settings.OLLAMA_URL}/api/generate", json=payload)
        if res.status_code == 200:
            answer = res.json().get("response", "").strip()
        else:
            answer = f"Generated offline response for: '{body.question}' based on {len(context_chunks)} sources."
    except Exception as e:
        logger.warning(f"Ollama connection issue: {e}")
        answer = f"Simulated RAG Answer for query: '{body.question}' using retrieved context."

    # 5. Store in Redis Cache
    await redis_cache.set(cache_key, answer, ttl=settings.CACHE_TTL)

    return AskResponse(
        question=body.question,
        answer=answer,
        sources=context_chunks,
        cached=False,
        prompt_injection_detected=False,
        latency_seconds=round(time.time() - start_time, 4)
    )
