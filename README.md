# Magnetar-AI

Production-grade, security-hardened Retrieval-Augmented Generation (RAG) microservice and intelligence dashboard.

## 🚀 Features

- **Hybrid RAG Engine**: Dual-retriever combining ChromaDB vector embeddings with BM25 Okapi lexical scoring.
- **Security & Input Guard**: Prompt injection detection and constant-time API Key authentication (`hmac.compare_digest`).
- **High-Performance Caching**: Redis SHA256 context-aware caching layer with configurable TTL.
- **Observability**: Prometheus metrics endpoint and OpenTelemetry distributed tracing with Jaeger integration.
- **TLS & Reverse Proxy**: Hardened Nginx configuration with Automated Certbot Let's Encrypt renewal.
- **Modern UI**: Dark mode glassmorphism frontend dashboard with real-time response rendering and document dropzone.

## 🛠️ Architecture

```
[ Frontend (Vite/React) ] ---> [ Nginx (SSL/Reverse Proxy) ]
                                          |
                                   [ FastAPI API ]
                                    /     |     \
                        [ Redis Cache ] [ RAG ] [ Ollama LLM ]
                                       /     \
                                [Chroma]     [BM25]
```

## 🧪 Quick Start & Testing

1. Setup environment:
   ```bash
   cp .env.example .env
   ```
2. Run automated tests:
   ```bash
   pytest
   ```
3. Launch with Docker Compose:
   ```bash
   docker compose -f docker-compose.yml up -d
   ```
