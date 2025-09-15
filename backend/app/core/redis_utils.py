import redis.asyncio as redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def store_refresh_token(user_id: str, refresh_token: str, expire_days: int = 30):
    key = f"refresh_token:{refresh_token}"
    await redis_client.setex(key, expire_days * 86400, user_id)

async def get_refresh_token(refresh_token: str):
    return await redis_client.get(f"refresh_token:{refresh_token}")

async def revoke_refresh_token(refresh_token: str):
    await redis_client.delete(f"refresh_token:{refresh_token}")

async def store_oauth_state(state: str, provider: str, expire_seconds: int = 600):
    key = f"oauth_state:{state}"
    return await redis_client.setex(key, expire_seconds, provider)  

async def get_oauth_state(state: str) -> str | None:
    key = f"oauth_state:{state}"
    provider = await redis_client.get(key)
    return provider if provider else None
    
async def delete_oauth_state(state:str):
    key = f"oauth_state:{state}"
    await redis_client.delete(key)