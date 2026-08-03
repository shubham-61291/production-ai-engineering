import os
import time
import threading
from datetime import datetime
from typing import TypedDict, List, Optional, Callable

from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

from ..config import config
from .utils import now_run_id, ensure_dir, safe_relpath, write_text, read_text
from .sanity import run_sanity_check
from .exe_builder import build_executable_in_code

thread_local = threading.local()

# =========================================================
# TOOLS
# =========================================================
@tool
def write_file(filename: str, content: str) -> str:
    """Write a file inside the current run directory. Example: src/main.py or requirements.txt"""
    try:
        run_dir = getattr(thread_local, "current_run_dir", None)
        if not run_dir:
            return "ERROR(write_file): current_run_dir context missing"
        filename = safe_relpath(filename)
        full_path = os.path.join(run_dir, filename)
        write_text(full_path, content)
        return f"OK: wrote {filename}"
    except Exception as e:
        return f"ERROR(write_file): {str(e)}"

@tool
def read_file(filename: str) -> str:
    """Read a file inside the current run directory. Example: src/main.py or requirements.txt"""
    try:
        run_dir = getattr(thread_local, "current_run_dir", None)
        if not run_dir:
            return "ERROR(read_file): current_run_dir context missing"
        filename = safe_relpath(filename)
        full_path = os.path.join(run_dir, filename)
        return read_text(full_path)
    except Exception as e:
        return f"ERROR(read_file): {str(e)}"

TOOLS_LIST = [write_file, read_file]


# =========================================================
# LLM FACTORY
# =========================================================
def get_llm(provider: str = None, model: str = None, base_url: str = None, api_key: str = None):
    provider = provider or config.DEFAULT_PROVIDER
    
    if provider == "ollama":
        base_url = base_url or config.OLLAMA_BASE_URL
        model_name = model or config.OLLAMA_MODEL
        # Use OpenAI compatibility endpoint for robust tool calling with Qwen2.5-Coder
        v1_url = base_url.rstrip('/') + '/v1' if not base_url.endswith('/v1') else base_url
        return ChatOpenAI(
            base_url=v1_url,
            api_key=api_key or "ollama",
            model=model_name,
            temperature=0
        ).bind_tools(TOOLS_LIST)
    else:
        api_key = api_key or config.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        model_name = model or config.OPENAI_MODEL
        return ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=api_key
        ).bind_tools(TOOLS_LIST)


# =========================================================
# STATE
# =========================================================
class AgentState(TypedDict):
    requirements: str
    run_dir: str
    status: str
    logs: List[str]
    messages: List[BaseMessage]
    patch_round: int
    exe_path: Optional[str]


# =========================================================
# AGENT PIPELINE RUNNER
# =========================================================
class ReActExeAgent:
    def __init__(self, provider: str = None, model: str = None, base_url: str = None, api_key: str = None):
        self.provider = provider or config.DEFAULT_PROVIDER
        self.model = model or (config.OLLAMA_MODEL if self.provider == "ollama" else config.OPENAI_MODEL)
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.api_key = api_key
        self.llm = get_llm(self.provider, self.model, self.base_url, self.api_key)

    def init_run_dir(self, custom_run_id: str = None) -> str:
        ensure_dir(config.WORKSPACE_DIR)
        ensure_dir(config.RUNS_DIR)

        run_id = custom_run_id or now_run_id()
        run_dir = os.path.join(config.RUNS_DIR, run_id)

        ensure_dir(run_dir)
        ensure_dir(os.path.join(run_dir, "src"))
        ensure_dir(os.path.join(run_dir, "logs"))
        ensure_dir(os.path.join(run_dir, "release"))
        return run_dir

    def run_pipeline(self, requirements: str, run_id: str = None, callback: Optional[Callable[[str, str, Optional[str]], None]] = None):
        run_dir = self.init_run_dir(run_id)
        thread_local.current_run_dir = run_dir

        state: AgentState = {
            "requirements": requirements,
            "run_dir": run_dir,
            "status": "Initializing...",
            "logs": [],
            "messages": [],
            "patch_round": 0,
            "exe_path": None
        }

        def log_and_notify(msg: str, status: str = None):
            ts = datetime.now().strftime("%H:%M:%S")
            log_line = f"[{ts}] {msg}"
            state["logs"].append(log_line)
            if status:
                state["status"] = status
            if callback:
                callback(state["status"], "\n".join(state["logs"][-600:]), state.get("exe_path"))

        log_and_notify(f"Workspace initialized at {run_dir}", "Workspace ready.")
        log_and_notify(f"Using Model: {self.model} via {self.provider.upper()}")

        # ---------------------------------------------------------
        # STEP 1: REACT CODEGEN
        # ---------------------------------------------------------
        log_and_notify("ReAct Agent: Generating code + requirements via tool actions...", "Codegen in progress...")

        system_prompt = f"""
You are Qwen2.5-Coder ReAct Agent.

GOAL:
Generate a complete, fully functional Windows Python application in:
- src/main.py
- requirements.txt

MANDATORY RULES:
1) Use ONLY these tools: write_file, read_file.
2) You MUST write src/main.py and requirements.txt using write_file.
3) requirements.txt must include ONLY required external packages (e.g. requests, pillow). If no external packages are needed, leave requirements.txt empty or specify only standard packages.
4) The app MUST run cleanly with: python src/main.py
5) The app MUST support: --help (print usage and exit).
6) The application MUST show this exact line somewhere visible to the user:
{config.COPYRIGHT_LINE}
7) NEVER include null bytes. Output must be plain UTF-8 text.
8) After you finish writing files, STOP calling tools.

User Requirement:
{requirements}
""".strip()

        state["messages"] = [SystemMessage(content=system_prompt)]

        codegen_done = False
        for step in range(1, config.MAX_REACT_STEPS + 1):
            log_and_notify(f"ReAct step {step}: Thinking + Acting...")

            try:
                resp = self.llm.invoke(state["messages"])
                state["messages"].append(resp)
            except Exception as err:
                log_and_notify(f"LLM Invoke Error: {str(err)}", "LLM Error")
                break

            tool_calls = getattr(resp, "tool_calls", None)
            if not tool_calls:
                log_and_notify("ReAct: Code generation complete.", "Files written.")
                codegen_done = True
                break

            for tc in tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]

                log_and_notify(f"Tool call: {tool_name}({list(tool_args.keys())})")

                tool_fn = next((t for t in TOOLS_LIST if t.name == tool_name), None)
                if tool_fn is None:
                    out = f"ERROR: unknown tool {tool_name}"
                else:
                    out = tool_fn.invoke(tool_args)

                state["messages"].append(ToolMessage(tool_call_id=tc["id"], content=str(out)))
                log_and_notify(f"Tool result: {str(out)[:150]}")

        # ---------------------------------------------------------
        # STEP 2: SANITY CHECK & PATCH LOOP
        # ---------------------------------------------------------
        while True:
            log_and_notify("Sanity check: python -m py_compile src/main.py", "Sanity check...")
            passed, sanity_msg = run_sanity_check(run_dir)

            if passed:
                log_and_notify("Sanity check passed!", "Sanity passed.")
                break

            if state["patch_round"] >= config.MAX_PATCH_ROUNDS:
                log_and_notify(f"FAILED: Max patch rounds ({config.MAX_PATCH_ROUNDS}) reached.", "Sanity failed.")
                raise RuntimeError("Sanity check failed after maximum patch iterations:\n" + sanity_msg)

            state["patch_round"] += 1
            log_and_notify(f"Sanity failed: {sanity_msg[:300]}. Starting Patch Round {state['patch_round']}...", "Patching...")

            logs_tail = "\n".join(state["logs"][-100:])
            patch_prompt = f"""
You are Qwen2.5-Coder Debugger.

Sanity check failed. Error logs:
{sanity_msg}

Recent activity logs:
{logs_tail}

Fix src/main.py (and requirements.txt if needed) using write_file.
Ensure python -m py_compile src/main.py will pass cleanly.
Ensure app still includes: {config.COPYRIGHT_LINE}

Stop calling tools when done.
""".strip()

            state["messages"] = [SystemMessage(content=patch_prompt)]

            for step in range(1, config.MAX_REACT_STEPS + 1):
                log_and_notify(f"Patch Step {step}...")
                resp = self.llm.invoke(state["messages"])
                state["messages"].append(resp)

                tool_calls = getattr(resp, "tool_calls", None)
                if not tool_calls:
                    log_and_notify("Patch applied.", "Patch completed.")
                    break

                for tc in tool_calls:
                    tool_name = tc["name"]
                    tool_args = tc["args"]
                    log_and_notify(f"Patch Tool Call: {tool_name}({list(tool_args.keys())})")
                    tool_fn = next((t for t in TOOLS_LIST if t.name == tool_name), None)
                    out = tool_fn.invoke(tool_args) if tool_fn else f"ERROR: unknown tool {tool_name}"
                    state["messages"].append(ToolMessage(tool_call_id=tc["id"], content=str(out)))
                    log_and_notify(f"Patch Tool Result: {str(out)[:150]}")

        # ---------------------------------------------------------
        # STEP 3: IN-CODE PYINSTALLER BUILD
        # ---------------------------------------------------------
        log_and_notify("Compiling executable with PyInstaller in-code engine...", "Compiling EXE...")

        try:
            exe_path = build_executable_in_code(run_dir, log_fn=lambda m: log_and_notify(m))
            state["exe_path"] = exe_path
            log_and_notify(f"SUCCESS: Executable ready at {exe_path}", "EXE ready.")
        except Exception as e:
            log_and_notify(f"PyInstaller compilation error: {str(e)}", "Build failed.")
            raise

        return state
