import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import make_asgi_app
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from app.core.config import settings
from app.core.utils import setup_logging
from app.core.rag import init_qdrant_collection, get_qdrant_client
from app.core.cache import redis_cache

setup_logging()

# OpenTelemetry Setup
resource = Resource(attributes={SERVICE_NAME: "magnetar-api"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger = logging.getLogger(__name__)
    logger.info("Initializing background resources...")
    try:
        await asyncio.to_thread(init_qdrant_collection)
    except Exception as e:
        logger.warning(f"Qdrant collection init deferred: {e}")
    yield
    # Shutdown actions
    logger.info("Shutting down background resources...")
    try:
        await redis_cache.client.close()
    except Exception as e:
        logger.error(f"Error closing Redis client: {e}")

from app.routers import ask, upload, audit

app = FastAPI(title="Magnetar Webstack API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.limiter import limiter

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()

app.include_router(ask.router, prefix="/api/v1", tags=["Ask"])
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(audit.router, prefix="/api/v1", tags=["Audit"])

@app.get("/health")
async def health_check():
    import httpx
    health = {"status": "ok"}
    try:
        await redis_cache.client.ping()
        health["redis"] = "healthy"
    except Exception:
        health["redis"] = "unhealthy"
        health["status"] = "degraded"
    try:
        client = get_qdrant_client()
        await asyncio.to_thread(client.get_collections)
        health["qdrant"] = "healthy"
    except Exception:
        health["qdrant"] = "unhealthy"
        health["status"] = "degraded"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
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
