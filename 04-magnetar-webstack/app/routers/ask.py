import logging
import json
import time
import asyncio
from fastapi import APIRouter, HTTPException, Request, Depends
import httpx
from app.models.schemas import AskRequest, AskResponse
from app.core.config import settings
from app.core.guards import get_input_guard, get_output_guard
from app.core.rag import retrieve_chunks
from app.core.cache import redis_cache
from app.core.auth import validate_api_key
from app.core.limiter import limiter
from app.core.tracing import tracer

router = APIRouter()
logger = logging.getLogger(__name__)

def build_prompt(question: str, context_chunks: list) -> str:
    if not context_chunks:
        return question
    context = "\n\n".join([c["text"] for c in context_chunks])
    return f"""System: You are an expert assistant. Answer using ONLY the provided context. If not in context, say "I don't have information about that."

Context: {context}

Question: {question}"""

@router.post("/ask", response_model=AskResponse)
@limiter.limit("50/minute")
async def ask(request: Request, body: AskRequest, api_key: str = Depends(validate_api_key)):
    with tracer.start_as_current_span("ask_request") as root_span:
        root_span.set_attribute("session_id", body.session_id or "default")
        root_span.set_attribute("use_rag", body.use_rag)
        root_span.set_attribute("question", body.question)

        with tracer.start_as_current_span("input_guard") as span:
            guard = get_input_guard()
            is_safe, score = await asyncio.to_thread(guard.analyze, body.question)
            span.set_attribute("is_safe", is_safe)
            span.set_attribute("score", score)
            if not is_safe:
                logger.warning(f"Blocked prompt: {body.question} (score={score})")
                raise HTTPException(status_code=400, detail="Prompt blocked due to policy violation.")

        session_id = body.session_id or "default"
        context_chunks = []

        if body.use_rag:
            with tracer.start_as_current_span("rag_retrieval") as span:
                try:
                    context_chunks = await asyncio.to_thread(retrieve_chunks, body.question, session_id, top_k=3)
                    span.set_attribute("chunks_count", len(context_chunks))
                    span.set_attribute("filenames", [c.get("filename") for c in context_chunks])
                except Exception as e:
                    logger.error(f"RAG failed: {e}")
                    span.record_exception(e)

        prompt = build_prompt(body.question, context_chunks)
        temp = body.temperature if body.temperature is not None else settings.DEFAULT_TEMPERATURE

        with tracer.start_as_current_span("cache_check") as span:
            cache_key = redis_cache.make_key(body.question, context_chunks, temp)
            cached = await redis_cache.get(cache_key)
            span.set_attribute("cache_hit", bool(cached))
            if cached:
                sources = [c["filename"] for c in context_chunks]
                return AskResponse(answer=cached, sources=sources, cached=True)

        with tracer.start_as_current_span("ollama_generation") as span:
            span.set_attribute("model", settings.OLLAMA_MODEL)
            span.set_attribute("temperature", temp)
            payload = {
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temp,
                    "seed": settings.DEFAULT_SEED,
                    "num_predict": body.max_tokens or settings.DEFAULT_MAX_TOKENS,
                    "top_k": 1
                }
            }
            try:
                start = time.time()
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(f"{settings.OLLAMA_URL}/api/generate", json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    raw = data.get("response", "").strip()
                    span.set_attribute("latency_ms", (time.time() - start) * 1000)
                    span.set_attribute("tokens_used", len(raw.split()))
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                span.record_exception(e)
                raise HTTPException(status_code=503, detail="LLM service unavailable")

        with tracer.start_as_current_span("output_guard") as span:
            output_guard = get_output_guard()
            redacted = await asyncio.to_thread(output_guard.redact, raw)
            span.set_attribute("redacted", redacted != raw)

        await redis_cache.set(cache_key, redacted)
        sources = [c["filename"] for c in context_chunks]
        return AskResponse(answer=redacted, sources=sources, cached=False)
