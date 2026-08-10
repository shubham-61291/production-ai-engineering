import hashlib
import redis.asyncio as redis
from app.core.config import settings

class RedisCache:
    def __init__(self):
        self.client = redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )

    async def get(self, key: str) -> str:
        try:
            return await self.client.get(key)
        except Exception:
            return None

    async def set(self, key: str, value: str, ttl: int = settings.CACHE_TTL):
        try:
            await self.client.setex(key, ttl, value)
        except Exception:
            pass

    def make_key(self, question: str, context_chunks: list, temperature: float, max_tokens: int) -> str:
        if context_chunks:
            sorted_texts = sorted([c.get("text", "") for c in context_chunks])
            context_hash = hashlib.md5("".join(sorted_texts).encode()).hexdigest()
        else:
            context_hash = "none"
        raw = f"{question}|{context_hash}|{temperature}|{max_tokens}"
        return hashlib.sha256(raw.encode()).hexdigest()

redis_cache = RedisCache()
