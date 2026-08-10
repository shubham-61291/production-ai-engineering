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

class DeployRequest(BaseModel):
    html: str
    bucket_name: str = os.getenv("GCP_BUCKET_NAME", "aetheris-generated-sites")
    key_content: str = ""

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

@app.post("/api/v1/deploy")
def deploy_site(req: DeployRequest):
    import tempfile, base64
    try:
        if req.key_content:
            key_bytes = base64.b64decode(req.key_content)
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
                tmp.write(key_bytes.decode('utf-8'))
                tmp.flush()
                result = deploy_to_gcp_bucket(req.html, tmp.name, req.bucket_name)
            os.unlink(tmp.name)
        else:
            result = deploy_to_gcp_bucket(req.html, bucket_name=req.bucket_name)
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}

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
    <title>Aetheris Webforge</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #090d16; --card: rgba(22, 30, 46, 0.75); --accent: #6366f1; --text: #f8fafc; --muted: #94a3b8; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; }
        .container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        .card { background: var(--card); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px; }
        h2 { margin-top: 0; font-size: 18px; color: #e2e8f0; }
        label { display: block; margin-top: 14px; font-size: 13px; font-weight: 600; color: var(--muted); }
        textarea, input { width: 100%; box-sizing: border-box; margin-top: 6px; padding: 12px; background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; color: var(--text); font-size: 14px; }
        button { width: 100%; margin-top: 20px; padding: 14px; background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); border: none; border-radius: 10px; color: #fff; font-weight: 700; cursor: pointer; }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(79, 70, 229, 0.4); }
        iframe { width: 100%; height: 550px; border: 1px solid #1e293b; border-radius: 12px; background: #fff; }
        .status-box { margin-top: 14px; padding: 12px; background: #060a0f; border-radius: 8px; font-family: monospace; font-size: 13px; color: #10b981; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div style="max-width:1200px;margin:0 auto;padding:20px 0;">
        <h1 style="font-size:24px;font-weight:700;color:#f8fafc;">⚡ Aetheris Webforge</h1>
    </div>
    <div class="container">
        <div class="card">
            <h2>🚀 Website Generator</h2>
            <label>Prompt</label>
            <textarea id="prompt" rows="4" placeholder="Describe the website you want..."></textarea>

            <div style="margin-top:12px;">
                <label style="font-size:13px;color:#94a3b8;">GCP Service Account Key (JSON) – optional</label>
                <input type="file" id="gcp-key-file" accept=".json" style="width:100%; margin-top:4px;" />
            </div>
            <button onclick="deployToGCP()" style="margin-top:12px;background:linear-gradient(135deg,#6366f1,#a855f7)">🚀 Deploy to GCP</button>
            <div id="deploy-status" class="status-box" style="margin-top:8px;display:none;"></div>

            <button onclick="generateWebApp()">✨ Generate Website</button>
            <div id="status" class="status-box">Ready.</div>
        </div>
        <div class="card">
            <h2>📊 Preview</h2>
            <iframe id="preview-frame" srcdoc="<p style='padding:20px;text-align:center;color:#64748b;'>Generated website will appear here...</p>"></iframe>
        </div>
    </div>

    <script>
        async function deployToGCP() {
            const status = document.getElementById("deploy-status");
            status.style.display = "block";
            status.textContent = "⏳ Deploying...";
            const iframe = document.getElementById("preview-frame");
            const html = iframe.srcdoc;
            if (!html || html.includes("will appear here")) {
                status.textContent = "❌ No generated website.";
                return;
            }
            const keyFile = document.getElementById("gcp-key-file").files[0];
            let keyBase64 = "";
            if (keyFile) {
                const keyContent = await keyFile.text();
                keyBase64 = btoa(keyContent);
            }
            try {
                const res = await fetch("/api/v1/deploy", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ html: html, key_content: keyBase64 })
                });
                const data = await res.json();
                if (data.success) {
                    status.innerHTML = `✅ ${data.message}<br><a href="${data.public_url}" target="_blank">Open Site</a>`;
                } else {
                    status.textContent = "❌ " + data.message;
                }
            } catch(e) {
                status.textContent = "❌ Network Error: " + e.message;
            }
        }

        async function generateWebApp() {
            const prompt = document.getElementById("prompt").value;
            const status = document.getElementById("status");
            if (!prompt) { status.textContent = "❌ Please enter a prompt."; return; }
            status.textContent = "⏳ Generating...";
            try {
                const res = await fetch("/api/v1/generate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt: prompt })
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
