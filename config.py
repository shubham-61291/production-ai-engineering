import os

# Server-side Generation Defaults
DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" or "openai"
DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:32b")

DEFAULT_OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

SITE_DIR = os.getenv("SITE_DIR", "./generated_site")
ZIP_PATH = os.getenv("ZIP_PATH", "./generated_site.zip")
APP_NAME = "AETHERIS-WEBFORGE"
