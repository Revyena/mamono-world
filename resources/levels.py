from controllers.redis_controller import RedisController
from .api import get, post
from .resources import Level as LevelObject

class Level:
    def __init__(self, bot):
        self.bot = bot
        self.path = "levels/{}"

    @property
    def redis_client(self):
        client = getattr(self.bot, "redis_client", None)
        if client is None:
            raise RuntimeError("Redis client not initialized yet")
        return client

    @property
    def redis_ctrl(self):
        return RedisController(client=self.redis_client)

    @staticmethod
    def xp_required(level: int) -> int:
        return int(100 * level ** 1.5)

    @staticmethod
    def total_xp_for_level(level: int) -> int:
        # Total XP required to reach a specific level
        return sum(Level.xp_required(lvl) for lvl in range(1, level + 1))

    async def get(self, user_id: int, guild_id: int) -> LevelObject:
        """
        Fetch a user's level from the API.
        Returns a Level dataclass (supports dot-access).
        """

        print(f'redis client in Level resource: {self.redis_client}')
        user = await self.redis_ctrl.get_user(user_id)
        guild = await self.redis_ctrl.get_guild(guild_id)
        print(f'Fetched user UUID: {user}')
        return await get(self.path.format(user), params={"guild": guild}, model=LevelObject)

    async def update(self, discord_id: int, new_level: int) -> LevelObject:
        """
        Update a user's level on the API.
        Returns the updated Level dataclass.
        """
        return await post(f"/levels/{discord_id}", json={"level": new_level}, model=LevelObject)
