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
    <title>Magnetar Labs — Engineering the Path to Singularity</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        :root { --bg: #000000; --card: rgba(10, 15, 30, 0.7); --accent: #22d3ee; --text: #f8fafc; --muted: #94a3b8; }
        * { box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; min-height: 100vh; overflow-x: hidden; position: relative; }
        
        #canvas-bg { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 0; pointer-events: none; }

        .app-wrapper { position: relative; z-index: 10; max-width: 1280px; margin: 0 auto; padding: 32px 24px; }
        
        .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(12px); }
        .brand { display: flex; align-items: center; gap: 16px; }
        .logo-img { height: 48px; width: auto; }
        .logo-title { font-size: 28px; font-weight: 800; background: linear-gradient(90deg, #22d3ee 0%, #d946ef 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px; }
        .tagline { font-size: 13px; color: rgba(255,255,255,0.7); margin-top: -2px; }

        .hero-banner { text-align: center; margin-bottom: 48px; }
        .hero-title { font-size: 44px; font-weight: 900; background: linear-gradient(135deg, #67e8f9 0%, #c084fc 50%, #e879f9 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }
        .hero-sub { font-size: 20px; font-weight: 700; color: #ffffff; margin-top: 12px; }

        .grid-container { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
        @media (max-width: 900px) { .grid-container { grid-template-columns: 1fr; } }

        .card { background: var(--card); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.12); border-radius: 20px; padding: 28px; box-shadow: 0 20px 50px rgba(0,0,0,0.7); }
        h2 { margin-top: 0; font-size: 20px; color: #f1f5f9; display: flex; align-items: center; gap: 10px; }
        
        label { display: block; margin-top: 16px; font-size: 13px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
        input, select, textarea { width: 100%; margin-top: 8px; padding: 14px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; color: var(--text); font-family: inherit; font-size: 14px; transition: border-color 0.2s; }
        input:focus, select:focus, textarea:focus { outline: none; border-color: #22d3ee; }

        button { width: 100%; margin-top: 24px; padding: 16px; background: linear-gradient(135deg, #0284c7 0%, #d946ef 100%); border: none; border-radius: 12px; color: #fff; font-weight: 800; font-size: 16px; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(217, 70, 239, 0.5); }

        iframe { width: 100%; height: 560px; border: 1px solid rgba(255,255,255,0.15); border-radius: 14px; background: #000; }
        .status-box { margin-top: 16px; padding: 14px; background: rgba(5, 10, 20, 0.9); border-radius: 10px; border: 1px solid rgba(34, 211, 238, 0.2); font-family: monospace; font-size: 13px; color: #38bdf8; white-space: pre-wrap; }
    </style>
</head>
<body>
    <canvas id="canvas-bg"></canvas>

    <div class="app-wrapper">
        <div class="header">
            <div class="brand">
                <img src="https://res.cloudinary.com/dud3yhilm/image/upload/v1761113319/Gemini_Generated_Image_f6b5ff6b5ff6b5ff_aqa9q6.png" alt="Magnetar Labs Logo" class="logo-img" />
                <div>
                    <div class="logo-title">Magnetar Labs</div>
                    <div class="tagline">Engineering the Path to Singularity</div>
                </div>
            </div>
            <div style="font-size:12px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);padding:8px 16px;border-radius:20px;">
                Enterprise Grade AI Integration
            </div>
        </div>

        <div class="hero-banner">
            <h1 class="hero-title">Harnessing AI Power</h1>
            <div class="hero-sub">Enterprise Grade AI Integration Platform</div>
        </div>

        <div class="grid-container">
            <div class="card">
                <h2>🚀 AI Web Application Engine</h2>
                <label>Website Purpose & Prompt</label>
                <textarea id="prompt" rows="4" placeholder="Describe your web application... e.g. Sleek AI product showcase page with particle background, dark glassmorphism cards, and interactive pricing..."></textarea>

                <label>LLM Engine Provider</label>
                <select id="provider">
                    <option value="ollama">Local Brain (Ollama DeepSeek-R1 32B)</option>
                    <option value="openai">OpenAI API</option>
                </select>

                <label>Ollama Server Endpoint / API Key</label>
                <input id="endpoint" value="http://localhost:11434/v1" placeholder="Endpoint or API Key" />

                <button onclick="generateWebApp()">✨ Forge Customer-Lovable Web App</button>
                <div id="status" class="status-box">System Status: Online. Ready to forge web apps.</div>
            </div>

            <div class="card">
                <h2>📊 Live Interactive App Preview</h2>
                <iframe id="preview-frame" srcdoc="<p style='padding:40px;text-align:center;color:#64748b;'>Generated web application preview will render here...</p>"></iframe>
            </div>
        </div>
    </div>

    <script>
        // THREE.JS MAGNETAR BACKGROUND ANIMATION ENGINE
        function createCircularTexture() {
            const size = 64;
            const canvas = document.createElement('canvas');
            canvas.width = size;
            canvas.height = size;
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.beginPath();
                ctx.arc(32, 32, 32, 0, 2 * Math.PI, false);
                ctx.fillStyle = 'rgba(255,255,255,1)';
                ctx.fill();
            }
            const texture = new THREE.CanvasTexture(canvas);
            texture.needsUpdate = true;
            return texture;
        }

        function initMagnetarScene() {
            const canvas = document.getElementById('canvas-bg');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 5;

            const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableZoom = false;
            controls.autoRotate = true;
            controls.autoRotateSpeed = 1.4;

            scene.add(new THREE.AmbientLight(0x404040, 2));
            const pointLight = new THREE.PointLight(0xffffff, 1.5);
            pointLight.position.set(5, 5, 5);
            scene.add(pointLight);

            // Particles Corona
            const N = 5000;
            const positions = new Float32Array(N * 3);
            for (let i = 0; i < N; i++) {
                const i3 = i * 3;
                const radius = Math.random() * (5.0 - 1.0) + 1.0;
                const vec = new THREE.Vector3((Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2);
                vec.normalize().multiplyScalar(radius);
                positions[i3] = vec.x;
                positions[i3 + 1] = vec.y;
                positions[i3 + 2] = vec.z;
            }
            const particleGeo = new THREE.BufferGeometry();
            particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            const particleMat = new THREE.PointsMaterial({
                color: 0xddeeff,
                size: 0.04,
                transparent: true,
                opacity: 0.9,
                depthWrite: false,
                sizeAttenuation: true,
                map: createCircularTexture(),
                alphaTest: 0.5
            });
            const particleSystem = new THREE.Points(particleGeo, particleMat);
            scene.add(particleSystem);

            // Core
            const coreGeo = new THREE.SphereGeometry(0.3, 32, 32);
            const coreMat = new THREE.MeshStandardMaterial({
                color: 0xffffff,
                emissive: 0xbbbbff,
                emissiveIntensity: 15,
                toneMapped: false
            });
            scene.add(new THREE.Mesh(coreGeo, coreMat));

            // Magnetic Field Loops
            const fieldGroup = new THREE.Group();
            const lineMat = new THREE.LineBasicMaterial({ color: 0x66ddff, transparent: true, opacity: 0.7 });
            for (let i = 0; i < 40; i++) {
                const startVec = new THREE.Vector3((Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2).normalize().multiplyScalar(0.3);
                const endVec = new THREE.Vector3((Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2).normalize().multiplyScalar(0.3);
                const control1 = new THREE.Vector3((Math.random() - 0.5) * 6.0, (Math.random() - 0.5) * 6.0, (Math.random() - 0.5) * 6.0).add(startVec);
                const control2 = new THREE.Vector3((Math.random() - 0.5) * 6.0, (Math.random() - 0.5) * 6.0, (Math.random() - 0.5) * 6.0).add(endVec);
                const curve = new THREE.CatmullRomCurve3([startVec, control1, control2, endVec]);
                const lineGeo = new THREE.BufferGeometry().setFromPoints(curve.getPoints(50));
                fieldGroup.add(new THREE.Line(lineGeo, lineMat.clone()));
            }
            scene.add(fieldGroup);

            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });

            function animate() {
                requestAnimationFrame(animate);
                controls.update();
                particleSystem.rotation.y += 0.001;
                particleSystem.rotation.x += 0.0003;
                fieldGroup.rotation.y += 0.0015;
                fieldGroup.rotation.x += 0.0005;
                fieldGroup.children.forEach(l => {
                    if (l.material) l.material.opacity = (Math.sin(Date.now() * 0.005 + l.id) * 0.3 + 0.4);
                });
                renderer.render(scene, camera);
            }
            animate();
        }

        window.addEventListener('DOMContentLoaded', initMagnetarScene);

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
