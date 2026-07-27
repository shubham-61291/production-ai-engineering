# MAGNETAR‑WEBSTACK

**Self‑hosted AI assistant with DeepSeek‑R1, RAG, guards, caching, Jaeger observability, React frontend, and a fully autonomous legal compliance audit agent.**

## Features

- DeepSeek‑R1:32B via Ollama (GPU‑accelerated)
- RAG with Qdrant + all‑MiniLM‑L6‑v2 embeddings
- Legal Compliance Audit (GDPR & EU AI Act) using a reflexion‑based multi‑agent workflow (Junior → Reflector → Researcher → Revisor)
- Input guard (DeBERTa‑v3) & output guard (Presidio)
- Redis caching (deterministic)
- Jaeger tracing (OpenTelemetry)
- React frontend with API key login
- Audit report generation (PDF with executive summary, score, flagged clauses)
- CI/CD with OIDC, security scanning

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐
│ Frontend    │─────▶│ FastAPI      │─────▶│ Background Task    │
│ (React)     │     │ Backend      │     │ (LangGraph)        │
└─────────────┘     └──────────────┘     └─────────────────────┘
       │                     │                        │
       │                     ▼                        ▼
       │              ┌─────────────┐         ┌────────────┐
       │              │ Redis       │         │ Ollama     │
       │              │ (cache,     │         │ DeepSeek   │
       │              │  jobs)      │         └────────────┘
       │              └─────────────┘               │
       │                     │                      │
       │              ┌─────────────┐         ┌────────────┐
       └──────────────│ Qdrant      │         │ Tavily     │
                      │ (RAG)       │         │ (Search)   │
                      └─────────────┘         └────────────┘
```

## Quick Start (Deployment)

1. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and set API_KEY and TAVILY_API_KEY
   ```

2. **Download ML Models**:
   ```bash
   python scripts/download_models.py
   ```

3. **Build Frontend**:
   ```bash
   cd frontend
   npm install
   VITE_API_URL=/api/v1 npm run build
   cd ..
   ```

4. **Launch Containers**:
   ```bash
   docker compose up -d --build
   ```

5. **Verify Setup**:
   ```bash
   curl -H "X-API-Key: your-strong-api-key-here" http://localhost:8000/health
   ```
