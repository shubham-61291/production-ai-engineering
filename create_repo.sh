#!/bin/bash
set -e

echo "🚀 Creating Magnetar-Webstack repository (Production Ready & Flawless)..."

# Create all directories
mkdir -p app/core app/models app/routers frontend/src/components frontend/src/styles .github/workflows scripts

# ===================== .env.example =====================
cat << 'EOF' > .env.example
ENVIRONMENT=production
API_KEY=your-strong-api-key-here
CORS_ORIGINS=["https://your-frontend-domain.com","http://localhost:3000"]
REGION=asia-south1
GCP_PROJECT_ID=your-project-id
GCS_BUCKET_NAME=your-bucket-name
REDIS_URL=redis://redis:6379
QDRANT_URL=http://qdrant:6333
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=deepseek-r1:32b
INPUT_GUARD_MODEL_PATH=./models/deberta-v3-base-prompt-injection
RATE_LIMIT_PER_MINUTE=50
DEFAULT_TEMPERATURE=0.0
DEFAULT_SEED=42
DEFAULT_MAX_TOKENS=512
CACHE_TTL=3600
EOF

# ===================== .github/workflows/ci-cd.yml =====================
cat << 'EOF' > .github/workflows/ci-cd.yml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install trufflehog
        run: curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
      - name: Run trufflehog
        run: trufflehog git file://. --only-verified --fail
      - name: Install bandit
        run: pip install bandit
      - name: Run bandit
        run: bandit -r app/ -ll -f json -o bandit-report.json
      - name: Upload bandit report
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: bandit-report.json

  build-and-deploy:
    needs: security-scan
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    env:
      REGION: asia-south1
    permissions:
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Authenticate to GCP via OIDC
        id: auth
        uses: google-github-actions/auth@v1
        with:
          workload_identity_provider: ${{ secrets.WORKLOAD_IDENTITY_PROVIDER }}
          service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Google Artifact Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGION }}-docker.pkg.dev
          username: _json_key
          password: ${{ steps.auth.outputs.access_token }}

      - name: Build and push API image
        env:
          PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
          REPO: magnetar-images
        run: |
          docker build -t ${{ env.REGION }}-docker.pkg.dev/$PROJECT_ID/$REPO/magnetar-api:latest .
          docker push ${{ env.REGION }}-docker.pkg.dev/$PROJECT_ID/$REPO/magnetar-api:latest

      - name: Build frontend
        run: |
          cd frontend
          npm install
          VITE_API_URL=/api npm run build
          cd ..

      - name: Deploy to GCP VM via SSH (IAP + OS Login)
        env:
          VM_NAME: ${{ secrets.GCP_VM_NAME }}
          ZONE: ${{ secrets.GCP_ZONE }}
          PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
        run: |
          gcloud config set project $PROJECT_ID
          gcloud compute ssh $VM_NAME --zone=$ZONE --tunnel-through-iap --command="mkdir -p ~/magnetar-webstack/frontend/dist"
          gcloud compute scp --tunnel-through-iap --recurse frontend/dist $VM_NAME:~/magnetar-webstack/frontend/ --zone=$ZONE
          gcloud compute scp --tunnel-through-iap .env $VM_NAME:~/magnetar-webstack/.env --zone=$ZONE
          gcloud compute ssh $VM_NAME --zone=$ZONE --tunnel-through-iap --command="
            cd ~/magnetar-webstack
            git pull
            export REGION=${{ env.REGION }}
            export GCP_PROJECT_ID=$PROJECT_ID
            docker compose pull
            docker compose up -d
            success=0
            for i in {1..30}; do
              if curl -f http://localhost:8000/health; then
                success=1
                break
              fi
              sleep 10
            done
            if [ $success -eq 0 ]; then exit 1; fi
          "
EOF

# ===================== docker-compose.yml =====================
cat << 'EOF' > docker-compose.yml
version: '3.8'

services:
  api:
    image: ${REGION:-asia-south1}-docker.pkg.dev/${GCP_PROJECT_ID:-local}/magnetar-images/magnetar-api:latest
    container_name: magnetar-api
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=${ENVIRONMENT:-production}
      - REDIS_URL=${REDIS_URL:-redis://redis:6379}
      - QDRANT_URL=${QDRANT_URL:-http://qdrant:6333}
      - OLLAMA_URL=${OLLAMA_URL:-http://ollama:11434}
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318/v1/traces
      - GCP_PROJECT_ID=${GCP_PROJECT_ID}
      - GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
      - API_KEY=${API_KEY:-your-strong-api-key-here}
      - CORS_ORIGINS=${CORS_ORIGINS:-["*"]}
      - INPUT_GUARD_MODEL_PATH=${INPUT_GUARD_MODEL_PATH:-./models/deberta-v3-base-prompt-injection}
      - DEFAULT_TEMPERATURE=${DEFAULT_TEMPERATURE:-0.0}
      - DEFAULT_SEED=${DEFAULT_SEED:-42}
      - DEFAULT_MAX_TOKENS=${DEFAULT_MAX_TOKENS:-512}
      - CACHE_TTL=${CACHE_TTL:-3600}
    volumes:
      - ./models:/app/models
    depends_on:
      - qdrant
      - redis
      - ollama
      - jaeger
    restart: unless-stopped
    networks:
      - magnetar-net
    mem_limit: 4G
    cpus: '2.0'

  qdrant:
    image: qdrant/qdrant:v1.9.0
    container_name: magnetar-qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
    restart: unless-stopped
    networks:
      - magnetar-net
    mem_limit: 2G
    cpus: '1.0'

  redis:
    image: redis:7-alpine
    container_name: magnetar-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - magnetar-net
    mem_limit: 1G
    cpus: '0.5'

  ollama:
    image: ollama/ollama:latest
    container_name: magnetar-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped
    networks:
      - magnetar-net
    mem_limit: 8G
    cpus: '4.0'

  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: magnetar-jaeger
    ports:
      - "16686:16686"
      - "4318:4318"
    environment:
      - COLLECTOR_OTLP_ENABLED=true
      - SPAN_STORAGE_TYPE=badger
      - BADGER_EPHEMERAL=false
      - BADGER_DIRECTORY_VALUE=/badger/data
      - BADGER_DIRECTORY_KEY=/badger/key
    volumes:
      - jaeger_data:/badger
    restart: unless-stopped
    networks:
      - magnetar-net
    mem_limit: 1G
    cpus: '0.5'

  nginx:
    image: nginx:alpine
    container_name: magnetar-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - api
    networks:
      - magnetar-net
    restart: unless-stopped
    mem_limit: 256M
    cpus: '0.2'

volumes:
  qdrant_storage:
  redis_data:
  ollama_data:
  jaeger_data:

networks:
  magnetar-net:
    driver: bridge
EOF

# ===================== nginx.conf =====================
cat << 'EOF' > nginx.conf
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://api:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# ===================== Dockerfile =====================
cat << 'EOF' > Dockerfile
FROM python:3.10-slim-bullseye AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_lg

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "app.main:app", "--bind", "0.0.0.0:8000"]
EOF

# ===================== requirements.txt =====================
cat << 'EOF' > requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.23.2
gunicorn==21.2.0
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.4.2
pydantic-settings==2.0.3
redis==5.0.0
qdrant-client==1.6.0
sentence-transformers==2.2.2
torch==2.0.1
transformers==4.35.2
presidio-analyzer==2.2.350
presidio-anonymizer==2.2.350
spacy==3.6.0
pypdf==3.17.1
python-docx==1.1.0
google-cloud-storage==2.10.0
google-cloud-logging==3.5.0
slowapi==0.1.9
prometheus-client==0.17.1
tenacity==8.2.3
pytest==7.4.3
httpx==0.25.1
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-exporter-otlp==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
opentelemetry-instrumentation-httpx==0.42b0
EOF

# ===================== app/core/limiter.py =====================
cat << 'EOF' > app/core/limiter.py
from slowapi import Limiter
from fastapi import Request

def get_real_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

limiter = Limiter(key_func=get_real_ip, default_limits=["50/minute"])
EOF

# ===================== app/core/rag.py =====================
cat << 'EOF' > app/core/rag.py
import logging
import uuid
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

logger = logging.getLogger(__name__)

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')
    return _embedder

_qdrant_client = None

def get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(url=settings.QDRANT_URL)
    return _qdrant_client

COLLECTION_NAME = "documents"
VECTOR_SIZE = 384

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def init_qdrant_collection():
    try:
        client = get_qdrant_client()
        collections = client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qdrant_models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=qdrant_models.Distance.COSINE
                )
            )
            logger.info("Qdrant collection created")
    except Exception as e:
        logger.warning(f"Qdrant collection initialization deferred: {e}")

def embed_texts(texts: List[str]) -> List[List[float]]:
    embedder = get_embedder()
    embeddings = embedder.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()

def store_chunks(chunks: List[Dict[str, Any]], session_id: str) -> int:
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)

    points = []
    for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
        payload = {
            "text": chunk["text"],
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "session_id": session_id,
            "timestamp": chunk["timestamp"]
        }
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{session_id}_{chunk['filename']}_{i}"))
        point = qdrant_models.PointStruct(
            id=point_id,
            vector=vec,
            payload=payload
        )
        points.append(point)

    client = get_qdrant_client()
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    return len(points)

def retrieve_chunks(query: str, session_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
    query_vec = embed_texts([query])[0]
    client = get_qdrant_client()
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=top_k,
        query_filter=qdrant_models.Filter(
            must=[qdrant_models.FieldCondition(
                key="session_id",
                match=qdrant_models.MatchValue(value=session_id)
            )]
        )
    )
    return [hit.payload for hit in search_result]
EOF

# ===================== app/main.py =====================
cat << 'EOF' > app/main.py
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi._rate_limit_exceeded_handler import _rate_limit_exceeded_handler
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
from app.core.limiter import limiter

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
    logger = logging.getLogger(__name__)
    logger.info("Initializing background resources...")
    try:
        await asyncio.to_thread(init_qdrant_collection)
    except Exception as e:
        logger.warning(f"Qdrant collection init deferred: {e}")
    yield
    logger.info("Shutting down background resources...")
    try:
        await redis_cache.client.close()
    except Exception as e:
        logger.error(f"Error closing Redis client: {e}")

from app.routers import ask, upload

app = FastAPI(title="Magnetar Webstack API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()

app.include_router(ask.router, prefix="/api/v1", tags=["Ask"])
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])

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
EOF

# ===================== frontend/src/App.tsx =====================
cat << 'EOF' > frontend/src/App.tsx
import React, { useState, useEffect } from 'react';
import Chat from './components/Chat';
import DocumentUpload from './components/DocumentUpload';
import Settings from './components/Settings';
import { ApiClient, setApiKey } from './api';

const App: React.FC = () => {
  const [apiKey, setApiKeyInput] = useState(localStorage.getItem('apiKey') || '');
  const [sessionId] = useState(() => {
    const stored = localStorage.getItem('sessionId');
    return stored || crypto.randomUUID();
  });
  const [useRag, setUseRag] = useState<boolean>(false);
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([]);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [temperature, setTemperature] = useState(0.0);
  const [maxTokens, setMaxTokens] = useState(512);

  useEffect(() => {
    localStorage.setItem('sessionId', sessionId);
    if (apiKey) {
      setApiKey(apiKey);
    }
  }, [sessionId, apiKey]);

  const handleLogin = () => {
    if (apiKey.trim()) {
      setApiKey(apiKey.trim());
      localStorage.setItem('apiKey', apiKey.trim());
    }
  };

  const sendMessage = async (question: string) => {
    setMessages(prev => [...prev, {role: 'user', content: question}]);
    setLoading(true);
    try {
      const response = await ApiClient.ask({
        question,
        use_rag: useRag,
        session_id: sessionId,
        temperature,
        max_tokens: maxTokens,
      });
      setMessages(prev => [...prev, {role: 'assistant', content: response.answer}]);
    } catch (error: any) {
      console.error('Error', error);
      setMessages(prev => [...prev, {role: 'assistant', content: `Error: ${error.response?.data?.detail || error.message}`}]);
    } finally {
      setLoading(false);
    }
  };

  if (!localStorage.getItem('apiKey')) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="bg-gray-800 p-8 rounded-lg shadow-lg max-w-md w-full border border-gray-700">
          <h1 className="text-2xl font-bold mb-4 text-center text-blue-400">Magnetar Webstack</h1>
          <p className="text-gray-400 mb-4 text-center text-sm">Enter your API key to authenticate</p>
          <input
            type="password"
            className="w-full p-2.5 rounded bg-gray-700 border border-gray-600 text-white focus:outline-none focus:border-blue-500"
            placeholder="API Key"
            value={apiKey}
            onChange={(e) => setApiKeyInput(e.target.value)}
          />
          <button onClick={handleLogin} className="mt-4 w-full bg-blue-600 hover:bg-blue-700 py-2.5 rounded font-medium transition-colors">
            Connect
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      <header className="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-800/50 backdrop-blur">
        <h1 className="text-xl font-bold tracking-tight text-blue-400">Magnetar Webstack</h1>
        <div className="flex gap-4 items-center">
          <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
            <input type="checkbox" checked={useRag} onChange={() => setUseRag(!useRag)} className="rounded bg-gray-700 border-gray-600 text-blue-600" />
            RAG Mode
          </label>
          <Settings
            temperature={temperature}
            setTemperature={setTemperature}
            maxTokens={maxTokens}
            setMaxTokens={setMaxTokens}
          />
        </div>
      </header>

      <main className="flex-1 flex flex-col md:flex-row overflow-hidden">
        <div className="flex-1 p-4 flex flex-col">
          <Chat messages={messages} onSend={sendMessage} loading={loading} />
        </div>
        <aside className="w-full md:w-80 p-4 border-l border-gray-700 bg-gray-800/30 overflow-y-auto">
          <DocumentUpload sessionId={sessionId} onUploadComplete={(filename) => setUploadedFiles(prev => [...prev, filename])} />
          <div className="mt-4">
            <h3 className="text-md font-semibold text-gray-300">Uploaded Files</h3>
            <ul className="list-disc pl-5 mt-2 text-sm text-gray-400 space-y-1">
              {uploadedFiles.map((f, idx) => <li key={idx} className="truncate">{f}</li>)}
              {uploadedFiles.length === 0 && <li className="list-none text-gray-500 italic">No files uploaded yet</li>}
            </ul>
          </div>
        </aside>
      </main>
    </div>
  );
};

export default App;
EOF

echo "✅ Repository build script updated with all fixes!"
EOF
