import os
import asyncio
import requests
from typing import Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import config
from .agent.utils import now_run_id, read_text
from .agent.engine import ReActExeAgent

app = FastAPI(
    title="Magnetar Agentic EXE Builder API",
    description="Backend API powering Qwen2.5-Coder ReAct Agent & In-Code PyInstaller Compilation Engine",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory run status & WebSocket subscribers state
RUNS_STATE: Dict[str, Dict[str, Any]] = {}
ACTIVE_WEBSOCKETS: Dict[str, list[WebSocket]] = {}

class BuildRequest(BaseModel):
    requirements: str
    provider: Optional[str] = "ollama"
    model: Optional[str] = "qwen2.5-coder:32b"
    base_url: Optional[str] = "http://localhost:11434"
    api_key: Optional[str] = ""

@app.get("/api/health")
def health_check():
    ollama_online = False
    available_models = []
    try:
        r = requests.get(f"{config.OLLAMA_BASE_URL.rstrip('/')}/api/tags", timeout=3)
        if r.status_code == 200:
            ollama_online = True
            data = r.json()
            available_models = [m.get("name") for m in data.get("models", [])]
    except Exception:
        ollama_online = False

    return {
        "status": "healthy",
        "ollama_online": ollama_online,
        "ollama_url": config.OLLAMA_BASE_URL,
        "available_models": available_models,
        "default_model": config.OLLAMA_MODEL,
        "workspace_dir": config.WORKSPACE_DIR
    }

async def broadcast_ws(run_id: str, data: dict):
    if run_id in ACTIVE_WEBSOCKETS:
        dead_ws = []
        for ws in ACTIVE_WEBSOCKETS[run_id]:
            try:
                await ws.send_json(data)
            except Exception:
                dead_ws.append(ws)
        for ws in dead_ws:
            ACTIVE_WEBSOCKETS[run_id].remove(ws)

def execute_agent_task(run_id: str, req: BuildRequest):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def agent_callback(status: str, logs: str, exe_path: Optional[str]):
        run_data = RUNS_STATE.get(run_id, {})
        run_data["status"] = status
        run_data["logs"] = logs
        run_data["exe_path"] = exe_path
        RUNS_STATE[run_id] = run_data

        # Fetch source code snippets if written
        run_dir = os.path.join(config.RUNS_DIR, run_id)
        main_py = ""
        req_txt = ""
        try:
            main_py = read_text(os.path.join(run_dir, "src", "main.py"))
        except Exception:
            pass
        try:
            req_txt = read_text(os.path.join(run_dir, "requirements.txt"))
        except Exception:
            pass

        ws_payload = {
            "type": "update",
            "run_id": run_id,
            "status": status,
            "logs": logs,
            "main_py": main_py,
            "requirements_txt": req_txt,
            "exe_ready": bool(exe_path and os.path.exists(exe_path))
        }
        loop.run_until_complete(broadcast_ws(run_id, ws_payload))

    try:
        agent = ReActExeAgent(
            provider=req.provider,
            model=req.model,
            base_url=req.base_url,
            api_key=req.api_key
        )
        final_state = agent.run_pipeline(
            requirements=req.requirements,
            run_id=run_id,
            callback=agent_callback
        )
        RUNS_STATE[run_id]["status"] = "DONE: EXE ready"
        RUNS_STATE[run_id]["exe_path"] = final_state.get("exe_path")
    except Exception as e:
        RUNS_STATE[run_id]["status"] = f"ERROR: {str(e)}"
        loop.run_until_complete(broadcast_ws(run_id, {
            "type": "error",
            "run_id": run_id,
            "error": str(e),
            "status": f"ERROR: {str(e)}"
        }))

@app.post("/api/build")
def start_build(req: BuildRequest, background_tasks: BackgroundTasks):
    run_id = now_run_id()
    RUNS_STATE[run_id] = {
        "run_id": run_id,
        "requirements": req.requirements,
        "status": "Initializing...",
        "logs": "Workspace initialized.\nWaiting for agent stream...",
        "exe_path": None
    }
    background_tasks.add_task(execute_agent_task, run_id, req)
    return {"run_id": run_id, "status": "Build initiated."}

@app.get("/api/runs/{run_id}")
def get_run_status(run_id: str):
    if run_id not in RUNS_STATE:
        raise HTTPException(status_code=404, detail="Run ID not found.")
    
    run_data = RUNS_STATE[run_id]
    run_dir = os.path.join(config.RUNS_DIR, run_id)
    
    main_py = ""
    req_txt = ""
    try:
        main_py = read_text(os.path.join(run_dir, "src", "main.py"))
    except Exception:
        pass
    try:
        req_txt = read_text(os.path.join(run_dir, "requirements.txt"))
    except Exception:
        pass

    exe_path = run_data.get("exe_path")
    exe_ready = bool(exe_path and os.path.exists(exe_path))

    return {
        **run_data,
        "main_py": main_py,
        "requirements_txt": req_txt,
        "exe_ready": exe_ready
    }

@app.get("/api/download/{run_id}")
def download_executable(run_id: str):
    run_dir = os.path.join(config.RUNS_DIR, run_id)
    release_dir = os.path.join(run_dir, "release")
    
    exe_file = None
    if os.path.exists(release_dir):
        files = os.listdir(release_dir)
        for f in files:
            if f.endswith(".exe") or f == "app":
                exe_file = os.path.join(release_dir, f)
                break

    if not exe_file or not os.path.exists(exe_file):
        raise HTTPException(status_code=404, detail="Executable file not found or build not complete.")

    filename = os.path.basename(exe_file)
    return FileResponse(
        path=exe_file,
        filename=filename,
        media_type="application/octet-stream"
    )

@app.websocket("/ws/build/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await websocket.accept()
    if run_id not in ACTIVE_WEBSOCKETS:
        ACTIVE_WEBSOCKETS[run_id] = []
    ACTIVE_WEBSOCKETS[run_id].append(websocket)

    # Send current snapshot on connect
    if run_id in RUNS_STATE:
        r_data = RUNS_STATE[run_id]
        await websocket.send_json({
            "type": "update",
            "run_id": run_id,
            "status": r_data.get("status"),
            "logs": r_data.get("logs"),
            "exe_ready": bool(r_data.get("exe_path") and os.path.exists(r_data.get("exe_path")))
        })

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if run_id in ACTIVE_WEBSOCKETS and websocket in ACTIVE_WEBSOCKETS[run_id]:
            ACTIVE_WEBSOCKETS[run_id].remove(websocket)
