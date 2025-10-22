import discord

from controllers.redis_controller import setup_redis
from controllers.utility import Config

from discord import Intents, Status, Activity, ActivityType, Bot

# from modules.leveling.utils import process_leveling_for_message, process_member_join, process_message_with_params

intents = Intents(messages=True, guilds=True, members=True, message_content=True)
config = Config()
redis = None

bot = Bot(
    intents=intents,
    status=Status.online,
    activity=Activity(type=ActivityType.streaming, name="Starting..."),
    debug_guilds=config.get("guild_id") if config.get("debug") else None,  # Replace with your debug guild ID
    allowed_mentions=discord.AllowedMentions(
        everyone=False,  # Disable @everyone mentions
        users=True,  # Enable @user mentions
        roles=False,  # Disable @role mentions
    )
)



@bot.listen()
async def on_connect() -> None:
    print("Connecting to discord...")

@bot.listen()
async def on_reconnect() -> None:
    print("Reconnecting to discord...")


@bot.listen()
async def on_ready() -> None:
    print(f"Authenticating as {bot.user}")
    print(f"------------------{len(str(bot.user)) * '-'}")
    await bot.change_presence(
        activity=Activity(type=ActivityType.streaming, name="Watching Mamono")
    )
    print(f'Authenticated with modules:\n{"\n".join(bot.extensions).replace('.', '/')}')
    bot.redis_client = await setup_redis()
    # await start_birthday_tasks(bot)


@bot.listen()
async def on_disconnect() -> None:
    print("Disconnecting from discord...")
    await bot.close()

@bot.listen()
async def on_message(message):
    if message.author.bot:
        return

    # leveled_up, level = await process_leveling_for_message(message)

    # if not leveled_up:
    #     return

    # TODO: Fetch level up message from settings
    # await message.channel.send(parsed_leveling_message)

@bot.listen()
async def on_member_join(member: discord.Member):
    if member.bot:
        return

    # enabled, embed = await process_member_join(member)

    # if not enabled or not embed:
    #     return

    # channel = embed.get("channel")
    # embed = embed.get("embed")

    # await channel.send(embed=embed)

@bot.listen()
async def on_guild_join(guild: discord.Guild):
    # TODO: Save guild to database
    print(f"Joined guild: {guild.name} (ID: {guild.id})")

if __name__ == "__main__":
    config.load_extensions(bot)
    bot.run(config.get("bot_token"))
