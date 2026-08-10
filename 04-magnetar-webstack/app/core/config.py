from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import json

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    API_KEY: str = "change_this_in_production"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    GCP_PROJECT_ID: Optional[str] = None
    GCS_BUCKET_NAME: Optional[str] = None
    REDIS_URL: str = "redis://redis:6379"
    REDIS_PASSWORD: Optional[str] = None
    QDRANT_URL: str = "http://qdrant:6333"
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "deepseek-r1:32b"
    INPUT_GUARD_MODEL_PATH: str = "./models/deberta-v3-base-prompt-injection"
    RATE_LIMIT_PER_MINUTE: int = 50
    DEFAULT_TEMPERATURE: float = 0.0
    DEFAULT_SEED: int = 42
    DEFAULT_MAX_TOKENS: int = 512
    CACHE_TTL: int = 3600
    TAVILY_API_KEY: Optional[str] = None
    AUDIT_MAX_RETRIES: int = 2
    AUDIT_TIMEOUT: int = 300
    REPORT_STORAGE: str = "local"
    REPORTS_DIR: str = "./reports"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(',')]
        return v

settings = Settings()
