import os
import re
import subprocess
from datetime import datetime

def now_run_id() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def safe_relpath(path: str) -> str:
    path = path.replace("\\", "/").strip()
    path = path.lstrip("/")
    path = path.replace("..", "")
    path = re.sub(r"^[.]+", "", path)
    return path

def write_text(path: str, content: str):
    ensure_dir(os.path.dirname(path))
    if isinstance(content, str):
        content = content.replace("\x00", "")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def run_cmd(cmd: str, cwd: str, timeout: int = 900):
    try:
        p = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout} seconds."
    except Exception as e:
        return -1, "", str(e)
