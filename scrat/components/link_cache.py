from uuid import uuid4

from aioredis import create_redis_pool
from redis import Redis

TOKEN_KEY_PREFIX = "link_token_"


class LinkCache:

    def __init__(self, redis_url: str):
        self._redis_url = redis_url

    async def store_discord_user_id(self, discord_user_id: int) -> str:
        client = await create_redis_pool(self._redis_url)
        token = str(uuid4())
        key = TOKEN_KEY_PREFIX + token
        await client.set(key, discord_user_id, expire = 3600)
        return token

    def get_discord_user_id(self, token) -> int:
        client = Redis.from_url(self._redis_url)
        key = TOKEN_KEY_PREFIX + token
        discord_user_id = client.get(key)
        # client.delete(key)
        return int(discord_user_id)
