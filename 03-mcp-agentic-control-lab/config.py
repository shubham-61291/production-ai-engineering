import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# ------------------------------------------------------------------------------
# AI BRAIN / LLM CONFIGURATION
# ------------------------------------------------------------------------------
# Supports Ollama (e.g., http://localhost:11434/v1 or http://<GPU_VM_IP>:11434/v1)
# or standard OpenAI API endpoints.
AI_BRAIN_BASE_URL = os.getenv("AI_BRAIN_BASE_URL", "http://localhost:11434/v1")
AI_BRAIN_MODEL = os.getenv("AI_BRAIN_MODEL", "deepseek-r1:32b")
AI_BRAIN_API_KEY = os.getenv("AI_BRAIN_API_KEY", "ollama")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ------------------------------------------------------------------------------
# VECTOR STORE CONFIGURATION
# ------------------------------------------------------------------------------
# Options: "chroma" (default, zero-config local), "pinecone"
VECTOR_STORE_PROVIDER = os.getenv("VECTOR_STORE_PROVIDER", "chroma").lower()
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db"))

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "mcp-rag-index")

# ------------------------------------------------------------------------------
# EMBEDDINGS CONFIGURATION
# ------------------------------------------------------------------------------
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "256"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "32"))

# ------------------------------------------------------------------------------
# ACCESS CONTROL / ROLES CONFIGURATION
# ------------------------------------------------------------------------------
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "xyz@gmail.com").strip().lower()
USER_EMAIL = os.getenv("USER_EMAIL", "abc@gmail.com").strip().lower()
