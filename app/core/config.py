import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    API_KEY: str = "your-strong-api-key-here"
    CORS_ORIGINS: Union[List[str], str] = ["*"]
    REGION: str = "asia-south1"
    GCP_PROJECT_ID: str = "your-project-id"
    GCS_BUCKET_NAME: str = "your-bucket-name"
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str = ""
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-r1:32b"
    INPUT_GUARD_MODEL_PATH: str = "./models/deberta-v3-base-prompt-injection"
    RATE_LIMIT_PER_MINUTE: int = 50
    DEFAULT_TEMPERATURE: float = 0.0
    DEFAULT_SEED: int = 42
    DEFAULT_MAX_TOKENS: int = 512
    CACHE_TTL: int = 3600
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    BM25_DATA_DIR: str = "./bm25_data"
    MAX_UPLOAD_SIZE_MB: int = 10
    DOMAIN: str = "localhost"
    CERTBOT_EMAIL: str = "admin@example.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [orig.strip() for orig in v.split(",") if orig.strip()]
        return v

settings = Settings()
