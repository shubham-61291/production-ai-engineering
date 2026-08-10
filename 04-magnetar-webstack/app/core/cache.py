import hashlib
import json
import redis.asyncio as redis
from app.core.config import settings

class RedisCache:
    def __init__(self):
        kwargs = {"decode_responses": True}
        if settings.REDIS_PASSWORD:
            kwargs["password"] = settings.REDIS_PASSWORD
        self.client = redis.from_url(settings.REDIS_URL, **kwargs)

    async def get(self, key: str) -> str:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int = settings.CACHE_TTL):
        await self.client.setex(key, ttl, value)

    async def setex(self, key: str, ttl: int, value: str):
        await self.client.setex(key, ttl, value)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) == 1

    def make_key(self, question: str, context_chunks: list, temperature: float) -> str:
        context_str = json.dumps(context_chunks, sort_keys=True)
        raw = f"{question}|{context_str}|{temperature}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def audit_job_key(self, job_id: str) -> str:
        return f"audit:{job_id}"

    async def set_audit_job(self, job_id: str, data: dict, ttl: int = 3600):
        key = self.audit_job_key(job_id)
        await self.client.setex(key, ttl, json.dumps(data))

    async def get_audit_job(self, job_id: str) -> dict:
        key = self.audit_job_key(job_id)
        val = await self.client.get(key)
        if val:
            return json.loads(val)
        return None

redis_cache = RedisCache()
