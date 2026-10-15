# Magnetar Webstack

**A self-hosted AI assistant combining local LLM inference, document-grounded RAG, privacy-oriented output filtering, and multi-agent contract review.**

Magnetar Webstack brings conversational AI, document retrieval, and a LangGraph-based legal-audit workflow into a single web application. The stack includes a React interface, FastAPI API, Qdrant vector storage, Redis caching and job state, Ollama inference, and operational telemetry.

## Overview

Magnetar Webstack supports three connected workflows:

1. **Chat:** Send a question to a locally hosted Ollama model, with configurable generation settings.
2. **Document Q&A:** Upload PDF, DOCX, TXT, or Markdown files, chunk and embed extracted text, store it in Qdrant, and retrieve context for questions scoped to a session.
3. **Contract audit:** Run a four-stage LangGraph workflow—Junior Auditor, Reflector, Researcher, and Revisor—and generate a structured report that can be downloaded as a PDF.

The project is designed to make the major stages of AI request handling visible and configurable: input screening, optional retrieval, model generation, output PII redaction, caching, and tracing.

## Key capabilities

- **Local inference:** Connects to Ollama, with `deepseek-r1:32b` as the configured default model.
- **Retrieval-augmented generation:** Uses `sentence-transformers/all-MiniLM-L6-v2` embeddings and Qdrant cosine-similarity search. Retrieved chunks are filtered by session ID.
- **Document ingestion:** Extracts text from PDF, DOCX, TXT, and Markdown uploads, then splits it into overlapping token-based chunks.
- **Input screening:** Uses the ProtectAI DeBERTa prompt-injection classifier when its model files are available.
- **Output PII redaction:** Uses Microsoft Presidio to detect and redact supported entities, including email addresses, phone numbers, SSNs, IP addresses, and credit-card numbers.
- **API-key authentication:** Protected API routes use the `X-API-Key` header.
- **Caching and audit-job state:** Redis stores cached answers and legal-audit job status/results.
- **Multi-agent legal review:** A LangGraph workflow drafts findings, reflects on citations and research needs, optionally searches with Tavily, and revises the report against retrieved evidence.
- **PDF reports:** Audit results can be returned as structured data and generated as downloadable PDF reports.
- **Observability:** FastAPI instrumentation exports OpenTelemetry traces to Jaeger; Prometheus metrics are exposed at `/metrics`.
- **Containerized services:** Docker Compose defines the API, Qdrant, Redis, Ollama, Jaeger, and Nginx services.
- **Optional Google Cloud Storage integration:** Uploads and audit reports can be stored in GCS when the bucket and credentials are configured.

## Architecture

```mermaid
flowchart TD
    U[Browser / React UI] --> N[Nginx]
    N --> API[FastAPI]
    API --> GUARD[DeBERTa Input Guard]
    GUARD -->|Allowed| RAG{RAG enabled?}
    RAG -->|Yes| EMB[MiniLM Embeddings]
    EMB --> Q[Qdrant]
    Q --> PROMPT[Context-grounded prompt]
    RAG -->|No| PROMPT
    PROMPT --> LLM[Ollama / DeepSeek-R1]
    LLM --> PII[Presidio Output Redaction]
    PII --> CACHE[Redis Cache]
    CACHE --> API
    API --> UI[Response]
    API --> AUDIT[LangGraph Legal Audit]
    AUDIT --> TAVILY[Tavily Search - optional]
    AUDIT --> PDF[PDF Report]
    API -. traces .-> J[Jaeger / OpenTelemetry]
    API -. metrics .-> M[Prometheus endpoint]
```

### Request flows

**Chat and RAG**

1. The client sends a question with its API key, session ID, and generation settings.
2. The input guard scores the prompt. Requests blocked by the configured threshold are rejected.
3. If RAG is enabled, the question is embedded and relevant chunks are retrieved from Qdrant for that session.
4. The context, when present, is included in the prompt sent to Ollama.
5. Presidio redacts supported PII from the response, and Redis caches the result for the configured TTL.

**Contract audit**

1. Submit contract text or an accepted document format to the audit endpoint.
2. The API creates a job ID and starts the audit in a background task.
3. The LangGraph sequence runs the Junior Auditor, Reflector, Researcher, and Revisor stages.
4. The result is stored in Redis and a PDF report is generated. Report storage can be local or configured for GCS.
5. Poll the job status and retrieve the structured result or PDF report using the job ID.

## Technology stack

| Layer | Components |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS, Axios |
| API | Python 3.10, FastAPI, Uvicorn |
| Model runtime | Ollama, DeepSeek-R1 32B (configured default) |
| Embeddings | Sentence Transformers, `all-MiniLM-L6-v2` |
| Vector database | Qdrant |
| Cache and job state | Redis |
| Input screening | ProtectAI DeBERTa-v3 prompt-injection classifier |
| PII protection | Microsoft Presidio, spaCy |
| Agent workflow | LangChain, LangGraph, optional Tavily Search |
| Reports | FPDF2 |
| Telemetry | OpenTelemetry, Jaeger, Prometheus client |
| Edge and deployment | Nginx, Docker, Docker Compose; optional Google Cloud Storage |

## Repository structure

```text
04-magnetar-webstack/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── audit_workflow.py
│   │   ├── auth.py
│   │   ├── cache.py
│   │   ├── config.py
│   │   ├── document_parser.py
│   │   ├── guards.py
│   │   ├── limiter.py
│   │   ├── rag.py
│   │   ├── tracing.py
│   │   └── utils.py
│   └── routers/
│       ├── ask.py
│       ├── audit.py
│       └── upload.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   └── components/
│   ├── package.json
│   └── vite.config.ts
├── scripts/
│   └── download_models.py
├── mws1.png
├── mws2.png
├── mws4.png
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── requirements.txt
├── setup_vm.sh
└── test_verification.py
```

## Screenshots

The screenshots below show the UI and example security behavior from this project.

### 1. Secure login

![Magnetar Webstack login page](./mws1.png)

### 2. Authenticated assistant interface

![Magnetar Webstack authenticated interface](./mws2.png)

### 3. Prompt-injection screening example

![Magnetar Webstack prompt-injection example](./mws4.png)

## Quick start with Docker Compose

### Prerequisites

- Docker Engine and Docker Compose v2
- Node.js and npm to build the frontend
- Python 3.10 for the model-download script
- Sufficient memory for the configured LLM; performance depends on the Ollama runtime and available hardware

### 1. Clone the repository

Run these commands from a directory where you want the repository checked out:

```bash
git clone https://github.com/shubham-61291/production-ai-engineering.git
cd production-ai-engineering/04-magnetar-webstack
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

At minimum, edit `.env` and set a strong, unique `API_KEY`. Review these settings for your environment:

| Variable | Purpose |
|---|---|
| `API_KEY` | Credential required by protected API routes |
| `CORS_ORIGINS` | Allowed browser origins |
| `OLLAMA_URL` | Ollama endpoint reachable by the API container; Compose defaults to `http://ollama:11434` |
| `OLLAMA_MODEL` | Intended model name; the application default is `deepseek-r1:32b` |
| `TAVILY_API_KEY` | Optional key for external research during legal audits |
| `GCS_BUCKET_NAME` | Optional bucket for GCS uploads and reports |
| `REPORT_STORAGE` | `local` or `gcs` report storage mode |
| `REPORTS_DIR` | Directory for locally stored reports |

Do not commit `.env`, API keys, cloud credentials, uploaded documents, or generated reports.

### 3. Download the guard and embedding models

The model-download script downloads the DeBERTa prompt-injection classifier, `all-MiniLM-L6-v2`, and the spaCy `en_core_web_sm` model into the local environment/model cache. Run it in a Python 3.10 environment with the project dependencies installed so the resulting `models/` directory is available to the API container.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/download_models.py
```

### 4. Build the frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

The build output is written to `frontend/dist`, which Nginx serves.

### 5. Start the services

```bash
docker compose up -d --build
```

Pull the configured model into the Compose-managed Ollama service:

```bash
docker compose exec ollama ollama pull deepseek-r1:32b
```

Check service status and logs:

```bash
docker compose ps
docker compose logs -f api
```

### 6. Open the application

- Web interface: `http://localhost/` or `http://<your-vm-ip>/`
- API health: `http://localhost:8000/health`
- Jaeger UI: `http://localhost:16686/`
- Prometheus metrics: `http://localhost:8000/metrics`

The Compose configuration maps the API and observability ports. Restrict access to these ports with host firewall rules or private networking when deployed to a VM. The checked-in `nginx.conf` listens on HTTP port 80; TLS must be configured separately before exposing the application publicly over HTTPS.

## API reference

Protected API routes require the header `X-API-Key: <your-api-key>`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Reports the health of Redis, Qdrant, and Ollama; no API key is required by this route |
| `POST` | `/api/v1/ask` | Ask a general question or enable RAG for a session |
| `POST` | `/api/v1/upload` | Upload and index a PDF, DOCX, TXT, or Markdown document |
| `POST` | `/api/v1/audit` | Start a contract audit from an uploaded file or submitted text |
| `GET` | `/api/v1/audit/{job_id}/status` | Poll audit progress and status |
| `GET` | `/api/v1/audit/{job_id}/result` | Retrieve the structured audit report |
| `GET` | `/api/v1/audit/{job_id}/report` | Download the generated PDF report |
| `GET` | `/metrics` | Prometheus metrics endpoint |

### Example: ask a question

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "question": "Summarize the uploaded policy on data retention.",
    "use_rag": true,
    "session_id": "demo-session",
    "temperature": 0.0,
    "max_tokens": 512
  }'
```

### Example: upload a document

```bash
curl -X POST "http://localhost:8000/api/v1/upload?session_id=demo-session" \
  -H "X-API-Key: $API_KEY" \
  -F "file=@./policy.pdf"
```

### Example: start a legal audit

```bash
curl -X POST http://localhost:8000/api/v1/audit \
  -H "X-API-Key: $API_KEY" \
  -F "text=Paste contract text to audit here" \
  -F "session_id=demo-session"
```

The response contains a `job_id`. Use that ID with the status, result, and report endpoints listed above.

## Security and privacy considerations

- **Protect the API key:** Replace the example value before running the stack and do not expose it in source control or client-side logs.
- **Input guard model availability matters:** If the configured DeBERTa model files are missing, `InputGuard` logs a warning and allows prompts through. Confirm the model is present before relying on input screening.
- **PII redaction is not a guarantee:** Presidio detects a defined set of entities; it should be treated as a safeguard, not proof that all sensitive data will be removed.
- **Protect telemetry and metrics:** `/metrics` is mounted without API-key validation in the current API entry point. Restrict access at the network or reverse-proxy layer.
- **Review cloud storage settings:** When GCS is configured, uploaded files or reports may be written to the configured bucket. Configure IAM and bucket access deliberately.
- **Legal audit is informational:** The audit workflow can flag potential issues against GDPR and the EU AI Act, but model-generated analysis is not legal advice and should be reviewed by a qualified professional.
- **Optional external research:** If `TAVILY_API_KEY` is configured, audit-generated search queries and search activity are sent to Tavily. Core chat and RAG inference use the configured Ollama service.

## Validation

The repository includes `test_verification.py`, which contains lightweight checks for chunking behavior, UUID generation, and forwarded-IP parsing. These are not an end-to-end test of the FastAPI, model, vector database, frontend, or Docker deployment.

Run the included checks with:

```bash
python test_verification.py
```

## Known implementation notes

- In the currently visible repository tree, the route modules import `app.models.schemas`, but an `app/models/` directory was not present. Restore that module before expecting the API to start successfully; the quick-start commands do not replace missing application source.
- The checked-in Compose file does not explicitly request GPU devices for the Ollama container. GPU acceleration depends on the host, drivers, and Ollama container configuration; otherwise inference may run without GPU acceleration.
- The input guard's fail-open behavior when model files are absent should be addressed before using the stack in a security-sensitive environment.

## Author

**Shubham Kumar Singh**

## License

MIT License
