# Production AI Engineering

## Production-Grade AI Systems Portfolio

A unified engineering repository containing **five independently deployable, production-grade AI systems** spanning autonomous application generation, AI-powered web application generation, enterprise Retrieval-Augmented Generation (RAG), agentic control architectures, secure self-hosted AI, and multi-agent compliance analysis.

The systems in this repository are not five variations of the same chatbot or a collection of notebooks and prompt experiments.

Each project is a **standalone systems artifact** designed around a distinct engineering problem, with explicit application architecture, model orchestration, security controls, deployment infrastructure, observability, failure handling, and real execution evidence.

The common engineering foundation across the portfolio is:

- Self-hosted and GPU-accelerated LLM inference
- Agentic workflows
- Retrieval-Augmented Generation
- Hybrid retrieval
- Explicit authorization boundaries
- Prompt-injection protection
- PII protection
- API authentication
- Rate limiting
- Caching
- Audit logging
- Distributed tracing
- Metrics
- Dockerized deployment
- Google Cloud infrastructure
- GitHub Actions automation
- Native Windows build infrastructure

---

# Systems at a Glance

| # | System | Core Engineering Problem | Primary Technologies |
|---|---|---|---|
| 01 | **Aetheris WebForge** | Natural language → deployable web application | Qwen2.5-Coder 32B, Ollama, FastAPI, GCP |
| 02 | **Magnetar AI** | Secure enterprise document intelligence | DeepSeek-R1 32B, ChromaDB, BM25, Redis |
| 03 | **MCP Agentic Control Lab** | Where authority should live in agentic systems | MCP, RBAC, ChromaDB, DeepSeek-R1 |
| 04 | **Magnetar Webstack** | Secure self-hosted AI + RAG + legal audit | DeepSeek-R1 32B, Qdrant, LangGraph, Redis |
| 05 | **Magnetar EXE Builder** | Natural language → native Windows executable | Qwen2.5 32B, ReAct, GitHub Actions, PyInstaller |

---

# Production AI Architecture

The five systems explore different layers of the production AI lifecycle:

```text
                         PRODUCTION AI ENGINEERING
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
       APPLICATION             KNOWLEDGE             CONTROL
        GENERATION              SYSTEMS              SYSTEMS
             │                    │                    │
       ┌─────┴─────┐        ┌─────┴─────┐       ┌────┴──────┐
       │           │        │           │       │           │
   WebForge      EXE      Magnetar    Webstack   MCP Lab
                Builder      AI
       │           │          │           │          │
       └───────────┴──────────┴───────────┴──────────┘
                                  │
                                  ▼
                       PRODUCTION FOUNDATION
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
        Local LLMs            Security             Operations
        GPU / Ollama           Guards             Observability
             │                    │                    │
             │              ┌─────┼─────┐              │
             │              │     │     │              │
             │             Auth  RBAC  PII             │
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
                       Docker / GCP Infrastructure
```

---

# Engineering Philosophy

The projects share several principles.

## 1. Systems Before Models

The model is treated as one component of a larger system.

The engineering focus is not simply:

```text
Prompt → LLM → Response
```

Instead, the systems explicitly address:

```text
Input
  ↓
Application Layer
  ↓
Security / Authorization
  ↓
Model / Agent
  ↓
Retrieval / Tools
  ↓
Validation
  ↓
Observability
  ↓
Artifact / Response
  ↓
Deployment
```

The model can therefore be replaced without redefining the entire architecture.

---

## 2. Explicit Control

The systems make important execution paths visible.

Control can exist in:

* application orchestration
* retrieval tools
* authorization layers
* security guards
* CI/CD pipelines
* audit logs
* deployment infrastructure

The goal is to avoid hidden orchestration and make system behavior inspectable through code, logs, and execution artifacts.

---

## 3. Evidence-First Engineering

The projects were validated through actual executions rather than only architectural diagrams.

Demonstrations include:

* generated Windows executables
* generated websites
* live RAG queries
* blocked prompt-injection attempts
* policy updates
* authorization failures
* audit logs
* cloud deployments
* live execution logs
* compliance reports

The screenshots and outputs described in the individual systems represent actual executions of the systems.

---

## 4. Security as a System Component

Security is integrated into the architecture rather than added as an afterthought.

Depending on the system, controls include:

* Prompt-injection detection
* Output PII redaction
* API-key authentication
* Role-based access control
* Tool-level authorization
* Rate limiting
* Secret protection
* Audit logging
* Defense in depth

---

# 01 — Aetheris WebForge

## AI-Powered Web Application Generator, Hardened Security & One-Click GCP Deployment

Aetheris WebForge converts natural-language requirements into complete, self-contained HTML5 web applications.

The system uses a local GPU-accelerated **Qwen2.5-Coder 32B** model through Ollama to generate functional websites locally and then provides a one-click deployment path to Google Cloud Storage.

### Core Pipeline

```text
Natural Language Prompt
          │
          ▼
   Qwen2.5-Coder 32B
          │
          ▼
   HTML / CSS / JavaScript
          │
          ▼
 Security Filtering
          │
          ▼
      Live Preview
          │
          ▼
 Google Cloud Storage
          │
          ▼
     Public Website
```

### What It Demonstrates

* Local GPU-based code generation
* Natural language → complete web application
* Single-file HTML generation
* Embedded CSS and JavaScript
* Prompt-injection protection
* Output sanitization
* Rate limiting
* Live preview
* CDN-based library support
* One-click GCP deployment
* Cloud deployment without a service-account key

### Key Features

* **Local AI Brain**

  * Qwen2.5-Coder 32B through Ollama
  * GPU-accelerated inference

* **Security Guardrails**

  * Prompt-injection detection
  * Output filtering
  * Rate limiting

* **One-Click GCP Deployment**

  * Generated HTML uploaded directly to Google Cloud Storage
  * Public URL returned after deployment
  * VM identity used for authentication

* **Application Generation**

  * Complete HTML5 applications
  * CSS and JavaScript generation
  * CDN support for frameworks and libraries such as Tailwind, Bootstrap, PDF-lib, and jsPDF

* **Live Preview**

  * Responsive dashboard
  * Generated application rendered directly in the interface

### Technology Stack

| Component      | Technology                                      |
| -------------- | ----------------------------------------------- |
| Language       | Python 3.10                                     |
| Backend        | FastAPI, Uvicorn                                |
| Frontend       | Vanilla HTML / CSS / JavaScript                 |
| AI Inference   | Ollama, Qwen2.5-Coder 32B                       |
| Security       | Custom regex + heuristic prompt-injection guard |
| Deployment     | Google Cloud Storage                            |
| Infrastructure | Docker, Google Cloud GPU VM                     |
| GPU            | NVIDIA L4                                       |

### Demonstrated Application

The system was demonstrated by generating a PDF toolkit-style website with functionality including:

* PDF merge
* PDF split
* PDF compression
* PDF conversion

The generated application was then deployed to Google Cloud Storage.

### Deployment Model

```text
Google Cloud GPU VM
        │
        ├── Docker
        │
        └── Ollama
              │
              ▼
       Qwen2.5-Coder 32B
              │
              ▼
       Aetheris WebForge
              │
              ▼
      Generated HTML
              │
              ▼
      Google Cloud Storage
```

### Important Engineering Decisions

The system is designed so that:

* Core generation happens locally
* User data is not collected or stored by the generation service
* The VM's identity can be used for GCP authentication
* Generated applications do not receive branding or proprietary assets unless explicitly requested

### Quick Start

```bash
git clone https://github.com/shubham-61291/aetheris-webforge.git
cd aetheris-webforge

cp .env.example .env
```

Configure:

```env
OLLAMA_BASE_URL=
OLLAMA_MODEL=qwen2.5-coder:32b
```

Build:

```bash
docker build -t aetheris-webforge .
```

Run:

```bash
docker run -d \
  --name aetheris \
  -p 7860:7860 \
  --env-file .env \
  --restart unless-stopped \
  aetheris-webforge
```

Dashboard:

```text
http://<your-vm-ip>:7860
```

---

# 02 — Magnetar AI

## Self-Hosted Enterprise RAG & Hybrid Intelligence Core

Magnetar AI is a security-hardened, self-hosted Retrieval-Augmented Generation platform designed for enterprise policy Q&A, legal-document analysis, and compliance knowledge bases.

The system combines:

* Dense vector retrieval
* BM25 keyword retrieval
* Reciprocal Rank Fusion
* Local GPU inference
* Prompt-injection protection
* API authentication
* Rate limiting
* Redis caching
* Distributed tracing
* Prometheus metrics

### Core Pipeline

```text
Documents
    │
    ▼
Parsing / Chunking
    │
    ├───────────────┐
    ▼               ▼
Embeddings         BM25
    │               │
    ▼               ▼
ChromaDB       Keyword Retrieval
    │               │
    └───────┬───────┘
            ▼
   Reciprocal Rank Fusion
            │
            ▼
     Retrieved Evidence
            │
            ▼
      DeepSeek-R1 32B
            │
            ▼
   Evidence-Grounded Answer
```

### Security Pipeline

```text
User Request
     │
     ▼
DeBERTa-v3 Input Guard
     │
     ├── Malicious → BLOCK
     │
     └── Allowed
           │
           ▼
        RAG Engine
           │
           ▼
      Local LLM
           │
           ▼
     Presidio Output
           │
           ▼
        Response
```

### Key Features

* DeepSeek-R1 32B running locally through Ollama
* GPU acceleration
* Hybrid ChromaDB + BM25 retrieval
* Reciprocal Rank Fusion
* PDF / DOCX / TXT ingestion
* Automatic document chunking
* Source-attributed answers
* API-key authentication
* Prompt-injection detection
* PII protection
* Redis query caching
* OpenTelemetry tracing
* Jaeger
* Prometheus
* Nginx reverse proxy
* Docker Compose deployment

### Technology Stack

| Component         | Technology                             |
| ----------------- | -------------------------------------- |
| Language          | Python 3.10, JavaScript                |
| Backend           | FastAPI, Uvicorn                       |
| Frontend          | React, Vite, Tailwind CSS              |
| LLM               | Ollama, DeepSeek-R1 32B                |
| Vector Database   | ChromaDB                               |
| Keyword Retrieval | BM25                                   |
| Embeddings        | sentence-transformers/all-MiniLM-L6-v2 |
| Input Guard       | DeBERTa-v3                             |
| Output Guard      | Microsoft Presidio                     |
| Cache             | Redis                                  |
| Tracing           | OpenTelemetry, Jaeger                  |
| Metrics           | Prometheus                             |
| Deployment        | Docker Compose                         |
| Infrastructure    | Google Cloud GPU VM                    |

### Architecture

```text
                React Frontend
                      │
                      ▼
                    Nginx
                      │
                      ▼
               FastAPI Backend
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
       Redis       Hybrid RAG   Security
       Cache           │         Guards
                       │
                ┌──────┴──────┐
                ▼             ▼
             ChromaDB        BM25
                │             │
                └──────┬──────┘
                       ▼
                 Ollama GPU
                       │
                       ▼
                DeepSeek-R1 32B
```

### Demonstrated Usage

The system was demonstrated against a policy document with questions such as:

* Working-hours policies
* Government-official monetary gift policies
* Other document-specific compliance questions

The system also demonstrated prompt-injection blocking.

### Example Security Test

A malicious request such as:

```text
Ignore all previous instructions...
```

is intercepted by the input security layer.

### Important Test-Document Disclosure

The policy document used for the demonstration was AI-generated for testing purposes. It does not represent an actual corporate policy and should not be treated as an official source.

### Limitations

* No cross-encoder reranking
* Retrieval relies on cosine similarity and BM25
* Ollama must be running for local inference
* DOCX table extraction is not fully supported
* Chunk size creates a recall/precision trade-off
* Screenshots represent real system outputs

### Quick Start

```bash
git clone https://github.com/shubham-61291/magnetar-ai.git
cd magnetar-ai

cp .env.example .env
```

Configure:

```env
API_KEY=
REDIS_PASSWORD=
OLLAMA_URL=
```

Download models:

```bash
python scripts/download_models.py
```

Build frontend:

```bash
cd frontend
npm install
npm run build
cd ..
```

Start:

```bash
docker compose up -d --build
```

Open:

```text
http://<your-vm-ip>
```

---

# 03 — MCP Agentic Control Lab

## Comparative Agentic RAG Architectures: MCP-Style vs MCP-Native Control

MCP Agentic Control Lab is a systems-engineering project that implements the same enterprise policy problem using two fundamentally different control paradigms:

```text
MCP-Style
UI-Orchestrated Control

vs.

MCP-Native
Agent → Tool → Context Control
```

The project asks a deeper engineering question:

> **Where should authority, trust, and control live in an agentic AI system?**

This is not simply a comparison between two chatbots.

It is a **governance and control architecture comparison**.

### Both Systems Provide

* Policy document ingestion
* Role-based access control
* Admin / User / Unknown identities
* Secure policy updates
* Document-grounded answers
* Safe handling of missing information
* Audit trails
* Dynamic policy updates

### Authority Model

#### MCP-Style

```text
User
 │
 ▼
UI
 │
 ▼
Application Logic
 │
 ▼
Retrieval / Update
```

#### MCP-Native

```text
User
 │
 ▼
Agent
 │
 ▼
Authorized Tool
 │
 ▼
Context / Vector Store
```

The key difference is where authorization is enforced.

In the MCP-Native implementation, authorization happens inside tools such as:

```text
retrieve_policy_context
update_policy_context
```

rather than relying exclusively on the interface.

### Key Capabilities

* Conversational policy Q&A
* PDF / DOCX / TXT ingestion
* Semantic chunking
* SentenceTransformer embeddings
* Local DeepSeek-R1 32B inference
* OpenAI fallback
* MCP-native tool server
* Role-based tool authorization
* Admin write permissions
* User read permissions
* Unknown identity denial
* Persistent vector storage
* Full audit logging
* Gradio interface

### Authorization Flow

```text
User
 │
 ▼
Identity / Role
 │
 ├── Unknown ──────────────► DENY
 │
 ├── User ─────────────────► READ
 │
 └── Admin ────────────────► READ + WRITE
```

### Secure Policy Update

```text
Admin
 │
 ▼
update_policy_context
 │
 ▼
Role Verification
 │
 ├── Unauthorized → BLOCK
 │
 └── Authorized
        │
        ▼
    Vector Store
        │
        ▼
   Updated Policy
```

### Audit Trail

Every tool invocation records information including:

* User identity
* User role
* Tool invoked
* Success / blocked status
* Retrieved information
* Unauthorized attempts
* Timestamps

### Technology Stack

| Component        | Technology                             |
| ---------------- | -------------------------------------- |
| Language         | Python 3.10                            |
| UI               | Gradio                                 |
| LLM              | Ollama, DeepSeek-R1 32B                |
| Fallback         | OpenAI API                             |
| Vector Store     | ChromaDB, Pinecone, InMemory           |
| Embeddings       | sentence-transformers/all-MiniLM-L6-v2 |
| Authorization    | Custom email-based RBAC                |
| Document Parsing | PyPDF2, python-docx                    |
| Deployment       | Docker, Docker Compose                 |
| Infrastructure   | Google Cloud GPU VM                    |

### Demonstrated Execution

The MCP-Native system demonstrates:

1. Normal user policy query
2. Authorized admin policy injection
3. Retrieval after dynamic policy update
4. Unauthorized policy update attempt
5. Tool-level authorization failure
6. Complete audit trail

The dynamic update test demonstrates that a newly inserted policy clause becomes available through the retrieval system without restarting the application.

### Engineering Challenges

#### Challenge 1 — Silent Retrieval Failures

Initial 256-token chunks caused important sections to be split across chunks.

**Solution:**

* Increased chunk size to 1200 tokens
* Added 100-token overlap
* Improved retrieval recall

#### Challenge 2 — Similarity Threshold

A 0.45 similarity threshold rejected relevant but semantically different queries.

**Solution:**

The threshold was reduced to 0.2, allowing relevant clauses with lower cosine similarity to be retrieved.

#### Challenge 3 — Embedding Output Format

The embedding engine inconsistently returned NumPy arrays and lists.

**Solution:**

The encoder was standardized to always return a Python list.

#### Challenge 4 — Docker Networking

The container could not access Ollama through localhost.

**Solution:**

The Docker bridge IP was used to connect the container to host Ollama.

### Limitations

* No cross-encoder reranking
* Retrieval relies on cosine similarity
* No persistent conversation memory across container restarts
* Ollama or OpenAI fallback is required
* Chunk size remains a recall/precision trade-off

### Quick Start

```bash
cp .env.example .env
```

Configure:

```env
ADMIN_EMAIL=
USER_EMAIL=
OLLAMA_URL=
```

Start:

```bash
docker compose up -d --build
```

Open:

```text
http://<host>:7860
```

---

# 04 — Magnetar Webstack

## Self-Hosted AI Assistant + RAG + Multi-Agent Legal Compliance Audit

Magnetar Webstack is a self-hosted, security-hardened AI platform combining:

* Conversational AI
* Document-grounded RAG
* Prompt-injection protection
* PII redaction
* API authentication
* Rate limiting
* Redis caching
* Distributed tracing
* Prometheus metrics
* Multi-agent legal compliance auditing

It is designed as a complete AI application rather than a simple chatbot wrapper.

### Core Pipeline

```text
                         User
                          │
                          ▼
                React Frontend
                          │
                          ▼
                Nginx Reverse Proxy
                          │
                          ▼
                   FastAPI Backend
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
       Redis            Qdrant           Ollama
   Cache / Queue     Vector Store      Local LLM
                          │
                          ▼
                         RAG
                          │
                          ▼
                 Multi-Agent Audit
                          │
                          ▼
                   PDF Compliance
                      Report
```

### Security Architecture

```text
User Request
     │
     ▼
DeBERTa-v3 Prompt Guard
     │
     ├── Malicious → BLOCK
     │
     └── Allowed
            │
            ▼
        AI / RAG
            │
            ▼
      Local DeepSeek-R1
            │
            ▼
      Presidio PII Scan
            │
            ▼
         Response
```

### Core Capabilities

#### Conversational AI

Local DeepSeek-R1 32B provides reasoning-based conversational responses.

#### Document RAG

Supported document types include:

* PDF
* DOCX
* TXT
* Markdown

Documents are embedded and indexed in Qdrant.

#### Legal Compliance Audit

The system implements a reflexion-based multi-agent workflow:

```text
Junior Auditor
      │
      ▼
Reflector
      │
      ▼
Researcher
      │
      ▼
Revisor
      │
      ▼
Compliance Report
```

The workflow audits contracts against:

* GDPR
* EU AI Act

The resulting PDF contains:

* Executive summary
* Compliance score
* Flagged clauses
* Supporting analysis

### Security Controls

* DeBERTa-v3 input guard
* Prompt-injection detection
* Microsoft Presidio output protection
* PII redaction
* API-key authentication
* Rate limiting
* Defense in depth
* Secret protection

### Deterministic Behavior

The system is designed for reproducibility through:

* Fixed model configuration
* Deterministic cache keys
* Redis caching
* Consistent RAG retrieval

### Technology Stack

| Component       | Technology                             |
| --------------- | -------------------------------------- |
| Language        | Python 3.10, TypeScript                |
| Backend         | FastAPI, Uvicorn                       |
| Frontend        | React, Vite, Tailwind CSS              |
| LLM             | Ollama, DeepSeek-R1 32B                |
| Vector DB       | Qdrant                                 |
| Embeddings      | sentence-transformers/all-MiniLM-L6-v2 |
| Input Guard     | DeBERTa-v3                             |
| Output Guard    | Microsoft Presidio                     |
| Cache           | Redis                                  |
| Tracing         | OpenTelemetry, Jaeger                  |
| Metrics         | Prometheus                             |
| Agent Workflow  | LangChain, LangGraph                   |
| Optional Search | Tavily                                 |
| Deployment      | Docker Compose                         |
| Infrastructure  | Google Cloud VM                        |

### Adversarial Conditions

The system was designed and tested against:

* Prompt-injection attempts
* Jailbreak-style requests
* Attempts to extract environment variables
* Attempts to extract secrets
* Documents containing sensitive information

PII is automatically redacted from generated output.

### Engineering Challenges

#### Challenge 1 — Dependency Conflicts

Conflicts occurred between packages including:

* spaCy
* Pydantic
* LangChain
* HTTPX

**Solution:**

* Updated pip
* Relaxed dependency bounds
* Locked a compatible package set

#### Challenge 2 — Docker → Host Ollama Networking

Containers could not access Ollama through localhost.

**Solution:**

The Docker bridge IP was used to connect containers to host Ollama.

#### Challenge 3 — Missing spaCy Model

Presidio failed because the required `en_core_web_lg` model was absent.

**Solution:**

The model was downloaded during container setup and incorporated into the Docker build.

#### Challenge 4 — Frontend Blank Page

The browser did not provide `crypto.randomUUID()`.

**Solution:**

A compatibility polyfill was added to the React application.

#### Challenge 5 — Nginx Authentication Header

The API key was sent by the frontend but was not forwarded by Nginx.

**Solution:**

The Nginx configuration was updated to forward:

```nginx
proxy_set_header X-API-Key $http_x_api_key;
```

#### Challenge 6 — Security Edge Case

A Base64-encoded secret was not blocked by the input detector.

The model nevertheless refused to return the secret.

This demonstrated a second security layer:

```text
Input Guard
     ↓
Allowed
     ↓
LLM Safety Behavior
     ↓
Secret Not Returned
```

### Limitations

* No live browsing for normal AI/RAG queries
* Legal audit requires Tavily for the web-research stage
* Large models may require quantization on T4/L4 GPUs
* Legal analysis is informational and not a substitute for human legal advice
* Demonstration screenshots represent real executions on a GCP GPU VM

### Quick Start

```bash
cp .env.example .env
```

Configure:

```env
API_KEY=
TAVILY_API_KEY=
```

Download models:

```bash
python scripts/download_models.py
```

Build frontend:

```bash
cd frontend
npm install
npm run build
cd ..
```

Start:

```bash
docker compose up -d --build
```

Verify:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
```

Open:

```text
http://<your-vm-ip>
```

---

# 05 — Magnetar EXE Builder

## AI-Powered Windows Application Generator with ReAct Agent, Open-Source LLM & GitHub Actions

Magnetar EXE Builder converts natural-language application requirements into compiled native Windows executables.

The system uses a local **Qwen2.5 32B** model through Ollama to generate Python source code, validate it, push the generated project to GitHub, trigger a Windows GitHub Actions runner, and automatically retrieve the resulting executable.

### Complete AI-to-Production Pipeline

```text
Natural Language Prompt
          │
          ▼
      ReAct Agent
          │
          ▼
    Qwen2.5 32B
          │
          ▼
 Generated Python Code
          │
          ▼
     py_compile
          │
     ┌────┴────┐
     │         │
   Failure   Success
     │         │
     ▼         ▼
Patch Round  GitHub
     │         │
     └────┬────┘
          ▼
    GitHub Actions
          │
          ▼
  Windows Runner
          │
          ▼
      PyInstaller
          │
          ▼
     Windows .exe
          │
          ▼
     Auto Download
```

### Key Features

* ReAct agent
* Qwen2.5 32B local inference
* Tool-based code generation
* `src/main.py` generation
* `requirements.txt` generation
* Automatic `py_compile` sanity checks
* Intelligent patch rounds
* GitHub Actions Windows compilation
* WebSocket live logs
* Automatic artifact retrieval
* One-click build interface

### Generated Applications

Demonstrated generated applications include:

* Snake game
* Web browsers
* PDF tools
* Other applications generated from short natural-language requirements

### Technology Stack

| Component       | Technology              |
| --------------- | ----------------------- |
| Language        | Python 3.10, JavaScript |
| Backend         | FastAPI, Uvicorn        |
| Frontend        | React, Vite             |
| AI Inference    | Ollama, Qwen2.5 32B     |
| Agent Framework | LangChain, LangGraph    |
| Windows Build   | PyInstaller             |
| CI/CD           | GitHub Actions          |
| Containers      | Docker, Docker Compose  |
| Infrastructure  | Google Cloud GPU VM     |
| GPU             | NVIDIA L4               |

### Architecture

```text
┌─────────────────┐
│   User Prompt   │
│    Web UI       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ReAct Agent   │
│     Ollama      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Code + Sanity   │
│     Check       │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│    GitHub Actions       │
│    Windows Runner       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│     Windows .exe        │
│       Download          │
└─────────────────────────┘
```

### Demonstrated End-to-End Execution

The system was demonstrated by generating a functional Snake game.

The execution flow included:

1. User enters application requirements
2. ReAct agent generates source files
3. Code passes sanity checking
4. Generated code is pushed to GitHub
5. GitHub Actions Windows runner builds the application
6. Executable is retrieved
7. User downloads and runs the native Windows application

### Engineering Challenges

#### Challenge 1 — Cross-Platform Build Limitations

A Linux Docker container cannot produce a genuine Windows executable using PyInstaller.

**Solution:**

The build stage was moved to a GitHub Actions `windows-latest` runner.

```text
Linux / GPU VM
      │
      ▼
Generated Code
      │
      ▼
GitHub
      │
      ▼
Windows Runner
      │
      ▼
Native .exe
```

#### Challenge 2 — Model Tool-Calling Compatibility

The specialized `qwen2.5-coder:32b` model did not provide the required native tool-calling behavior through Ollama.

This caused the agent to announce completion without actually creating files.

**Solution:**

The system switched to the base:

```text
qwen2.5:32b
```

which reliably invoked the required file-writing and reading tools.

#### Challenge 3 — Docker Cache

Docker caching caused changes to the build engine to be ignored.

The old local PyInstaller workflow continued to execute.

**Solution:**

A clean rebuild was performed using:

```bash
docker compose build --no-cache
```

Additional measures included:

* `docker cp` for container-side file replacement
* Installing Git inside the backend container

#### Challenge 4 — Missing Destination Directory

`shutil.copy()` failed because the destination `src/` directory did not exist.

**Solution:**

The destination directory is created explicitly:

```python
os.makedirs(os.path.dirname(dst), exist_ok=True)
```

#### Challenge 5 — GitHub Workflow Dispatch

GitHub rejected a workflow dispatch request with HTTP 422 because the required branch input was missing.

Incorrect:

```json
{
  "ref": "main"
}
```

Correct:

```json
{
  "ref": "main",
  "inputs": {
    "branch": "main"
  }
}
```

#### Challenge 6 — Nginx Proxy Configuration

Nginx repeatedly reverted to its default configuration after container rebuilds.

This removed the required `/api/` and `/ws/` proxy rules.

**Solution:**

The custom `nginx.conf` was mounted through Docker Compose so the configuration survives rebuilds.

### Limitations

* Windows build time depends on GitHub Actions queue availability
* Typical build time is approximately 2–5 minutes
* GitHub Actions requires an appropriate Personal Access Token
* Native Windows compilation cannot be performed locally inside the Linux container
* Generated executables are unsigned and may trigger Windows SmartScreen
* Output quality depends on the Qwen2.5 32B model
* Demonstration screenshots represent actual executions

### Quick Start

```bash
git clone https://github.com/shubham-61291/magnetar-exe-builder.git
cd magnetar-exe-builder
```

Configure:

```env
OLLAMA_BASE_URL=http://172.17.0.1:11434
OLLAMA_MODEL=qwen2.5:32b
GITHUB_TOKEN=<your-github-token>
```

Start:

```bash
docker compose up -d --build
```

Open:

```text
http://<your-vm-ip>:3000
```

Enter an application description and select **Build EXE**.

Example:

```text
Create a Snake game with arrow key controls, score display,
collision detection, restart functionality, and retro styling.
```

---

# Cross-System Security Architecture

Security is implemented differently depending on the problem being solved.

| Security Requirement       | Aetheris | Magnetar AI | MCP Lab | Webstack | EXE Builder |
| -------------------------- | -------: | ----------: | ------: | -------: | ----------: |
| Prompt Injection Detection |        ✓ |           ✓ |       — |        ✓ |           — |
| Output Protection          |        ✓ |           ✓ |       — |        ✓ |           — |
| API Authentication         |        — |           ✓ |       — |        ✓ |           — |
| RBAC                       |        — |           — |       ✓ |        — |           — |
| Tool-Level Authorization   |        — |           — |       ✓ |        — |           — |
| Rate Limiting              |        ✓ |           ✓ |       — |        ✓ |           — |
| Audit Logging              |        — |           ✓ |       ✓ |        ✓ |           ✓ |
| Local LLM                  |        ✓ |           ✓ |       ✓ |        ✓ |           ✓ |
| GPU Inference              |        ✓ |           ✓ |       ✓ |        ✓ |           ✓ |
| Docker Deployment          |        ✓ |           ✓ |       ✓ |        ✓ |           ✓ |
| GCP Infrastructure         |        ✓ |           ✓ |       ✓ |        ✓ |           ✓ |

---

# Cross-System AI Stack

```text
                    AI APPLICATIONS
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       Agents             RAG            Generation
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                    Local LLM Runtime
                           │
                        Ollama
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Qwen2.5 32B   Qwen2.5-Coder   DeepSeek-R1
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                     GPU Infrastructure
                           │
                     Google Cloud VM
```

---

# Retrieval Architecture

The repository demonstrates multiple retrieval architectures.

## Hybrid Retrieval

Used by Magnetar AI:

```text
             Query
               │
       ┌───────┴───────┐
       ▼               ▼
    Dense             Sparse
   Retrieval          BM25
       │               │
       └───────┬───────┘
               ▼
      Reciprocal Rank Fusion
               │
               ▼
        Relevant Evidence
```

## Vector-Based Agentic Retrieval

Used by MCP Agentic Control Lab:

```text
User
 │
 ▼
Agent
 │
 ▼
Authorized Retrieval Tool
 │
 ▼
Vector Store
 │
 ▼
Policy Context
 │
 ▼
DeepSeek-R1
```

## Qdrant-Based RAG

Used by Magnetar Webstack:

```text
Documents
    │
    ▼
Embeddings
    │
    ▼
Qdrant
    │
    ▼
Retrieved Context
    │
    ▼
DeepSeek-R1
```

---

# Observability

Several systems treat observability as part of the application architecture rather than an external operational concern.

The portfolio includes:

* Structured logging
* WebSocket execution logs
* Audit trails
* OpenTelemetry traces
* Jaeger
* Prometheus
* Redis caching
* Tool invocation records
* Build execution logs
* Security-block events

This makes it possible to inspect not only the final answer, but also how the system arrived there.

---

# Deployment Model

The projects are designed around containerized, GPU-enabled infrastructure.

A representative deployment looks like:

```text
                    Google Cloud VM
                           │
              ┌────────────┴────────────┐
              │                         │
           Docker                    Ollama
              │                         │
       ┌──────┼──────┐                  │
       │      │      │                  ▼
      API   UI    Services          Local LLM
       │      │      │                  │
       └──────┼──────┘                  │
              │                         │
              └──────────┬──────────────┘
                         ▼
                    AI Application
```

Ollama is commonly run directly on the host to provide direct GPU access, while application services run inside Docker containers.

---

# Production Engineering Patterns Demonstrated

Across the five systems, the repository demonstrates practical solutions to problems such as:

### Cross-Platform Compilation

Native Windows builds are delegated to Windows infrastructure rather than incorrectly attempting to compile Windows executables inside Linux containers.

### Model Compatibility

Model selection is based not only on generation quality but also on capabilities such as tool calling.

### Retrieval Quality

Chunk size, overlap, embedding behavior, and similarity thresholds are treated as engineering parameters rather than fixed defaults.

### Container Networking

Host-level GPU inference services are explicitly connected to containerized applications.

### Security Boundaries

Authorization can be enforced at the tool layer rather than relying entirely on frontend controls.

### Dependency Management

Production deployment requires resolving compatibility between rapidly evolving AI libraries.

### Reverse Proxy Behavior

Nginx configuration is explicitly managed so authentication headers and API/WebSocket routes survive rebuilds.

### Defense in Depth

Security does not rely on one detector. Multiple layers can prevent sensitive information from reaching the final response.

---

# Demonstration Philosophy

The systems are backed by actual execution evidence.

Examples include:

* Native Windows `.exe` execution
* Generated web applications
* Live GCP deployment
* Document-grounded RAG answers
* Prompt-injection blocking
* Dynamic policy updates
* Unauthorized tool calls
* Audit logs
* Legal compliance reports
* Real Docker deployments
* Real GPU inference

The objective is to demonstrate working system behavior rather than only present architectural diagrams.

---

# Repository Structure

```text
production-ai-engineering/
│
├── README.md
│
├── 01-aetheris-webforge/
│   ├── source
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md
│
├── 02-magnetar-ai/
│   ├── core/
│   ├── frontend/
│   ├── scripts/
│   ├── docker-compose.yml
│   └── README.md
│
├── 03-mcp-agentic-control-lab/
│   ├── core/
│   ├── mcp_core/
│   ├── screenshots/
│   ├── docker-compose.yml
│   └── README.md
│
├── 04-magnetar-webstack/
│   ├── core/
│   ├── frontend/
│   ├── scripts/
│   ├── docker-compose.yml
│   └── README.md
│
└── 05-magnetar-exe-builder/
    ├── backend/
    ├── frontend/
    ├── Dockerfile
    ├── docker-compose.yml
    └── README.md
```

Each directory remains a **standalone application**.

The monorepo provides a unified engineering view without forcing the five systems into one runtime or dependency environment.

---

# System Comparison

| Capability               | Aetheris | Magnetar AI | MCP Lab | Webstack | EXE Builder |
| ------------------------ | :------: | :---------: | :-----: | :------: | :---------: |
| Local LLM                |     ✓    |      ✓      |    ✓    |     ✓    |      ✓      |
| GPU Inference            |     ✓    |      ✓      |    ✓    |     ✓    |      ✓      |
| RAG                      |     —    |      ✓      |    ✓    |     ✓    |      —      |
| Hybrid Retrieval         |     —    |      ✓      |    —    |     —    |      —      |
| Document Ingestion       |     —    |      ✓      |    ✓    |     ✓    |      —      |
| Agentic Workflow         |     —    |      —      |    ✓    |     ✓    |      ✓      |
| Multi-Agent Workflow     |     —    |      —      |    —    |     ✓    |      —      |
| Code Generation          |     ✓    |      —      |    —    |     —    |      ✓      |
| Web Generation           |     ✓    |      —      |    —    |     —    |      —      |
| Native EXE Generation    |     —    |      —      |    —    |     —    |      ✓      |
| Prompt Injection Guard   |     ✓    |      ✓      |    —    |     ✓    |      —      |
| PII Protection           |     —    |      ✓      |    —    |     ✓    |      —      |
| API Authentication       |     —    |      ✓      |    —    |     ✓    |      —      |
| RBAC                     |     —    |      —      |    ✓    |     —    |      —      |
| Tool-Level Authorization |     —    |      —      |    ✓    |     —    |      —      |
| Redis                    |     —    |      ✓      |    —    |     ✓    |      —      |
| Observability            |     —    |      ✓      |    ✓    |     ✓    |      ✓      |
| Docker                   |     ✓    |      ✓      |    ✓    |     ✓    |      ✓      |
| GCP                      |     ✓    |      ✓      |    ✓    |     ✓    |      ✓      |
| GitHub Actions           |     —    |      —      |    —    |     —    |      ✓      |

---

# Engineering Scope

This repository covers multiple layers of modern AI engineering.

## AI & LLM Engineering

* Local LLM inference
* GPU acceleration
* Qwen2.5
* Qwen2.5-Coder
* DeepSeek-R1
* Ollama
* ReAct agents
* LangChain
* LangGraph
* Tool calling
* Multi-agent workflows

## Retrieval & Knowledge Systems

* Document parsing
* Chunking
* Embeddings
* Dense retrieval
* BM25
* Hybrid retrieval
* Reciprocal Rank Fusion
* ChromaDB
* Qdrant
* Pinecone
* In-memory retrieval
* Evidence-grounded generation

## AI Security

* Prompt-injection detection
* DeBERTa-v3
* Presidio
* PII redaction
* API-key authentication
* RBAC
* Tool-level authorization
* Rate limiting
* Defense in depth
* Secret protection

## Infrastructure

* Docker
* Docker Compose
* Nginx
* Redis
* Google Cloud GPU VMs
* Google Cloud Storage
* GitHub Actions
* Windows runners
* PyInstaller
* Ollama

## Observability

* Structured logs
* Audit trails
* OpenTelemetry
* Jaeger
* Prometheus
* WebSocket execution logs
* Build logs
* Tool invocation logs

---

# Known Limitations

These systems are production-oriented engineering artifacts, but each has explicit technical limitations.

### Aetheris WebForge

* Deployment requires appropriate GCP Storage permissions
* Generated applications depend on LLM output quality
* Public website deployment requires appropriate bucket configuration

### Magnetar AI

* No cross-encoder reranking
* Retrieval depends on cosine similarity and BM25
* Ollama is required for local inference
* DOCX table extraction is incomplete
* Chunk size affects retrieval precision and recall

### MCP Agentic Control Lab

* No cross-encoder reranking
* No persistent conversation memory across restarts
* Requires Ollama or OpenAI fallback
* Retrieval quality depends on chunking and similarity thresholds

### Magnetar Webstack

* Legal audit requires Tavily for its web-research stage
* Large models may require quantization on T4/L4 hardware
* Legal audit output is informational and not a replacement for legal advice
* Normal AI/RAG queries do not provide live browsing

### Magnetar EXE Builder

* Windows builds depend on GitHub Actions availability
* Builds generally take approximately 2–5 minutes
* A GitHub Personal Access Token is required
* Windows executables cannot be compiled natively inside the Linux container
* Generated executables are unsigned and may trigger SmartScreen
* Output quality depends on Qwen2.5 32B

---

# What Makes These Production-Grade Systems?

The focus is not simply model selection.

The engineering work covers the surrounding system required to make AI functionality operational:

```text
                MODEL
                  │
                  ▼
             ORCHESTRATION
                  │
                  ▼
          RETRIEVAL / TOOLS
                  │
                  ▼
             VALIDATION
                  │
                  ▼
              SECURITY
                  │
                  ▼
           AUTHORIZATION
                  │
                  ▼
           OBSERVABILITY
                  │
                  ▼
            DEPLOYMENT
                  │
                  ▼
             OPERATIONS
```

The systems explicitly address:

* How models interact with tools
* How documents become retrievable evidence
* How authority is enforced
* How malicious input is handled
* How sensitive output is protected
* How containers communicate with host GPU services
* How generated software is compiled
* How cloud deployment is performed
* How execution is observed
* How failures are diagnosed
* How limitations are exposed

The repository therefore focuses on **AI systems engineering**, not merely AI model usage.

---

# Author

**Shubham Singh**

---

# License

MIT License
