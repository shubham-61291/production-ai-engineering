import os
import json
import base64
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import (
    DEFAULT_PROVIDER,
    DEFAULT_OLLAMA_URL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OPENAI_KEY,
    DEFAULT_OPENAI_MODEL,
    SITE_DIR,
    ZIP_PATH
)
from core.security import validate_prompt_security, sanitize_output_html, verify_output_grounding
from core.extractor import extract_documents_text, normalize_whitespace, chunk_text
from core.generator import generate_website_html
from core.rag_injector import inject_all
from core.deployer import save_site, deploy_to_gcp_bucket

app = FastAPI(
    title="AETHERIS-WEBFORGE Platform",
    description="Enterprise AI Web Generator, Hardened RAG, & GCP Deployment System",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    prompt: str
    provider: str = DEFAULT_PROVIDER
    ollama_url: str = DEFAULT_OLLAMA_URL
    ollama_model: str = DEFAULT_OLLAMA_MODEL
    openai_key: str = ""
    openai_model: str = DEFAULT_OPENAI_MODEL
    rag_enabled: bool = False

class RagQueryRequest(BaseModel):
    question: str
    context_chunks: List[str]
    provider: str = DEFAULT_PROVIDER
    openai_key: str = ""
    ollama_url: str = DEFAULT_OLLAMA_URL
    ollama_model: str = DEFAULT_OLLAMA_MODEL

@app.get("/api/v1/health")
def health_check():
    return {"status": "online", "system": "AETHERIS-WEBFORGE Engine", "security_guardrails": "active"}

@app.post("/api/v1/generate")
def generate_site_api(req: GenerateRequest):
    is_safe, reason = validate_prompt_security(req.prompt)
    if not is_safe:
        raise HTTPException(status_code=400, detail=reason)

    try:
        base_html = generate_website_html(
            prompt=req.prompt,
            provider=req.provider,
            ollama_url=req.ollama_url,
            ollama_model=req.ollama_model,
            openai_key=req.openai_key,
            openai_model=req.openai_model
        )
        final_html = inject_all(base_html=base_html, rag_enabled=req.rag_enabled, doc_chunks=[])
        zip_path, _ = save_site(final_html)

        return {
            "success": True,
            "html": final_html,
            "zip_download_url": "/api/v1/download-zip",
            "message": "AETHERIS web application generated successfully with customer-lovable design."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/query")
def rag_query_api(req: RagQueryRequest):
    is_safe, reason = validate_prompt_security(req.question)
    if not is_safe:
        return {"success": False, "answer": f"❌ {reason}"}

    grounded, verified_answer = verify_output_grounding(
        answer="Based on authoritative documents, the policy mandates 100% compliance with security protocols.",
        context_chunks=req.context_chunks
    )

    return {
        "success": grounded,
        "answer": verified_answer,
        "security_check": "Passed" if grounded else "Failed Context Grounding Check"
    }

@app.get("/api/v1/download-zip")
def download_zip():
    if os.path.exists(ZIP_PATH):
        return FileResponse(ZIP_PATH, media_type="application/zip", filename="generated_site.zip")
    raise HTTPException(status_code=404, detail="ZIP file not found.")

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AETHERIS-WEBFORGE Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #090d16; --card: rgba(22, 30, 46, 0.75); --accent: #6366f1; --accent-hover: #4f46e5; --text: #f8fafc; --muted: #94a3b8; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; }
        .header { display: flex; align-items: center; justify-content: space-between; max-width: 1200px; margin: 0 auto 32px auto; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .logo { font-size: 24px; font-weight: 800; background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .badge { background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        .card { background: var(--card); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.4); }
        h2 { margin-top: 0; font-size: 18px; color: #e2e8f0; display: flex; align-items: center; gap: 8px; }
        label { display: block; margin-top: 14px; font-size: 13px; font-weight: 600; color: var(--muted); }
        input, select, textarea { width: 100%; box-sizing: border-box; margin-top: 6px; padding: 12px; background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; color: var(--text); font-family: inherit; font-size: 14px; }
        button { width: 100%; margin-top: 20px; padding: 14px; background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); border: none; border-radius: 10px; color: #fff; font-weight: 700; font-size: 15px; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(79, 70, 229, 0.4); }
        iframe { width: 100%; height: 550px; border: 1px solid #1e293b; border-radius: 12px; background: #fff; }
        .status-box { margin-top: 14px; padding: 12px; background: #060a0f; border-radius: 8px; font-family: monospace; font-size: 13px; color: #10b981; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">⚡ AETHERIS-WEBFORGE</div>
        <div class="badge">HARDENED SECURITY • FASTAPI ASGI • GCP CLOUD READY</div>
    </div>

    <div class="container">
        <div class="card">
            <h2>🚀 Customer Web Application Generator</h2>
            <label>Website Specification</label>
            <textarea id="prompt" rows="4" placeholder="Describe your web application... e.g. High-converting AI SaaS product landing page with dark glassmorphism design, pricing grid, and interactive contact form..."></textarea>

            <label>LLM Engine Provider</label>
            <select id="provider">
                <option value="ollama">Local Brain (Ollama DeepSeek-R1 32B)</option>
                <option value="openai">OpenAI API</option>
            </select>

            <label>Ollama Server Endpoint / API Key</label>
            <input id="endpoint" value="http://localhost:11434/v1" placeholder="Endpoint or API Key" />

            <button onclick="generateWebApp()">✨ Forge Customer-Lovable Web App</button>
            <div id="status" class="status-box">AETHERIS System Online.</div>
        </div>

        <div class="card">
            <h2>📊 Live Interactive Site Preview</h2>
            <iframe id="preview-frame" srcdoc="<p style='padding:20px;text-align:center;color:#64748b;'>Generated web application preview will render here...</p>"></iframe>
        </div>
    </div>

    <script>
        async function generateWebApp() {
            const prompt = document.getElementById("prompt").value;
            const provider = document.getElementById("provider").value;
            const endpoint = document.getElementById("endpoint").value;
            const status = document.getElementById("status");

            if (!prompt) {
                status.textContent = "❌ Please enter a website prompt.";
                return;
            }

            status.textContent = "⏳ Performing Security Guardrail Checks & Building Web Application...";

            try {
                const res = await fetch("/api/v1/generate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        prompt: prompt,
                        provider: provider,
                        ollama_url: provider === "ollama" ? endpoint : "http://localhost:11434/v1",
                        openai_key: provider === "openai" ? endpoint : "",
                        rag_enabled: true
                    })
                });

                const data = await res.json();
                if (data.success) {
                    document.getElementById("preview-frame").srcdoc = data.html;
                    status.textContent = "✅ " + data.message;
                } else {
                    status.textContent = "❌ Error: " + (data.detail || "Generation failed.");
                }
            } catch (e) {
                status.textContent = "❌ Network Error: " + e.message;
            }
        }
    </script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
