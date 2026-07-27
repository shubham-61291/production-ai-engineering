import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from prometheus_client import make_asgi_app
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from app.core.config import settings
from app.core.utils import setup_logging, get_http_client, close_http_client
from app.core.tracing import tracer
from app.core.limiter import limiter
from app.core.auth import validate_api_key
from app.routers import ask, upload, delete

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    yield
    # Shutdown logic
    try:
        from app.core.cache import redis_cache
        await redis_cache.client.close()
    except Exception:
        pass
    await close_http_client()

app = FastAPI(title="Magnetar AI API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def metrics_auth(request: Request, call_next):
    if request.url.path == "/metrics":
        api_key = request.headers.get("X-API-Key")
        try:
            await validate_api_key(api_key)
        except HTTPException:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

try:
    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()
except Exception:
    pass

app.include_router(ask.router, prefix="/api/v1", tags=["Ask"])
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(delete.router, prefix="/api/v1", tags=["Delete"])

@app.get("/health")
async def health_check():
    from app.core.cache import redis_cache
    from app.core.rag import rag_store
    
    health = {"status": "ok"}
    try:
        await redis_cache.client.ping()
        health["redis"] = "healthy"
    except Exception:
        health["redis"] = "unhealthy"
        health["status"] = "degraded"
        
    try:
        await asyncio.to_thread(rag_store.collection.count)
        health["chromadb"] = "healthy"
    except Exception:
        health["chromadb"] = "unhealthy"
        health["status"] = "degraded"
        
    try:
        client = get_http_client()
        resp = await client.get(f"{settings.OLLAMA_URL}/api/tags")
        if resp.status_code == 200:
            health["ollama"] = "healthy"
        else:
            health["ollama"] = "unhealthy"
            health["status"] = "degraded"
    except Exception:
        health["ollama"] = "unhealthy"
        health["status"] = "degraded"

    return health
