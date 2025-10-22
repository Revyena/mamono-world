import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

import discord

from ORM.models.Birthday import Birthday
from controllers import setup_logger
from managers import settings_manager, SettingsManager
from managers.settings.bot_settings import SettingKey


async def handle_traceback(bot: discord.Bot, command, error):
    logger = setup_logger()
    exception_log = await settings_manager.get(
        scope_type=SettingsManager.SCOPES_BOT,
        scope_id=1,
        setting_key=SettingKey.EXCEPTION_LOG,
    )

    guild = bot.get_guild(exception_log.get("guild"))
    channel = guild.get_channel(exception_log.get("channel")) if guild else None

    if not channel:
        logger.warning(
            f"Guild for exception log not found: {exception_log.get('guild')}. "
            "Set a guild for exception logs using /developer exceptions"
        )
        logger.error(f"Exception in command {command}: {error}")
        return "`[500]` **An error occurred while processing your request.**"

    tb_str = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    chunks = [tb_str[i:i + 4000] for i in range(0, len(tb_str), 4000)]

    for i, chunk in enumerate(chunks, start=1):
        embed = discord.Embed(
            title="⚠️ Exception Occurred" if i == 1 else f"⚠️ Exception (part {i})",
            description=f"```py\n{chunk}\n```",
            color=discord.Color.red(),
        )
        if i == 1:
            embed.set_footer(text=f"Command: {command}")
        await channel.send(embed=embed)

    return "`[500]` **An error occurred while processing your request.**"

async def check_user_birthday(user):
    birthdays = await Birthday.objects.get(user.id)
    for birthday in birthdays:
        if not birthday:
            return

        today = datetime.now(ZoneInfo("America/New_York")).date()
        if birthday.date.day == today.day and birthday.date.month == today.month:
            return True, birthday.guild