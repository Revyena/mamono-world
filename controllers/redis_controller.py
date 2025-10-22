from enum import Enum

import aiohttp
from redis.asyncio import Redis

from .utility import Config

class ModelType(Enum):
    USER = "DiscordUser"
    GUILD = "DiscordGuild"

async def setup_redis():
    config = Config()
    client = Redis.from_url(config.get("redis_url"), encoding="utf-8", decode_responses=True)
    print("Connected to Redis")

    return client

class RedisController:
    """
    Controller for managing Redis operations, including fetching and caching UUIDs.
    This class interacts with a Redis instance to cache UUIDs for users and guilds,
    reducing the need for repeated API calls.

    Attributes:
        redis (Redis): An instance of the Redis client.
    """
    def __init__(self, client: Redis):
        self.client = client

    async def fetch_uuid(self, model: ModelType, entity_id: int) -> str:
        """
        Fetch UUID for a given model type, optionally by user_id or guild_id.
        This function is a fallback for when a UUID is not cached in Redis.

        Args:
            model (ModelType): The type of model (USER or GUILD).
            entity_id (int): The user_id or guild_id based on the model type.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://localhost:8000/api/uuid/{entity_id}/", params={'model': model.value}) as resp:
                data = await resp.json()
                return data["uuid"]

    async def get_user(self, user_id: str|int) -> str:
        """
        Get UUID for a user, using Redis as a cache. If not found in Redis, fetch from API and cache it.
        Args:
            user_id (str|int): The user ID to fetch the UUID for. Defaults to None.
        """
        # Try Redis first
        redis_key = f'user:{int(user_id)}'
        uuid_val = await self.client.get(name=redis_key)

        if uuid_val:
            return uuid_val

        uuid_val = await self.fetch_uuid(ModelType.USER, user_id)

        # Cache in Redis
        await self.client.set(name=redis_key, value=uuid_val, ex=3600)
        return uuid_val

    async def get_guild(self, guild_id: str|int) -> str:
        """
        Get UUID for a guild, using Redis as a cache. If not found in Redis, fetch from API and cache it.
        Args:
            guild_id (str|int): The guild ID to fetch the UUID for. Defaults to None.
        """
        # Try Redis first
        redis_key = f'guild:{int(guild_id)}'
        uuid_val = await self.client.get(name=redis_key)
        if uuid_val:
            return uuid_val

        uuid_val = await self.fetch_uuid(ModelType.GUILD, guild_id)

        # Cache in Redis
        await self.client.set(name=redis_key, value=uuid_val, ex=3600)
        return uuid_val

