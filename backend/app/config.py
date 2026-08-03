import os

class Config:
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:32b")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "ollama")  # "ollama" or "openai"
    
    WORKSPACE_DIR: str = os.path.abspath(os.getenv("WORKSPACE_DIR", os.path.join(os.path.dirname(__file__), "..", "workspace")))
    RUNS_DIR: str = os.path.join(WORKSPACE_DIR, "runs")
    
    MAX_REACT_STEPS: int = int(os.getenv("MAX_REACT_STEPS", "18"))
    MAX_PATCH_ROUNDS: int = int(os.getenv("MAX_PATCH_ROUNDS", "4"))
    
    COPYRIGHT_LINE: str = os.getenv("COPYRIGHT_LINE", "© 2026 Shubham Singh. All rights reserved.")

config = Config()
