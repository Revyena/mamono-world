import random
import discord
import re
from typing import Tuple

import settings
from controllers.utility import Config

config = Config()

async def process_leveling_for_message(message) -> Tuple[bool, str | None]:
    leveling_enabled = await settings_manager.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=message.guild.id, setting_key=SettingKey.LEVEL_UP_ENABLED)
    if not leveling_enabled:
        return False, None

    user_id = message.author.id
    user, _ = await Level.objects.get_or_create(user=user_id, guild=message.guild.id)

    if not await user.can_gain_xp(cooldown_seconds=60):
        return False, None # User is on cooldown for gaining XP

    gained_xp = random.randint(10, 20)
    leveled_up = await user.add_xp(gained_xp)

    if not leveled_up:
        return False, None

    return True, user.level

async def process_member_join(member: discord.Member) -> tuple[bool, None] | tuple[
    bool, dict[str, discord.TextChannel | discord.Embed]]:
    guild = member.guild
    join_logs_enabled = await settings_manager.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=guild.id, setting_key=SettingKey.LOGS_JOIN_ENABLED)
    if not join_logs_enabled:
        return False, None

    join_logs_channel = await settings_manager.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=guild.id, setting_key=SettingKey.LOGS_JOIN_CHANNEL_ID)
    join_logs_channel = guild.get_channel(join_logs_channel) if join_logs_channel else None
    if not join_logs_channel:
        return False, None

    join_logs_message = await settings_manager.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=guild.id, setting_key=SettingKey.LOGS_JOIN_MESSAGE)

    embed = discord.Embed()
    embed.set_author(name=f"{member.display_name} joined the server", icon_url=guild.icon.url if guild.icon else None)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.description = await process_message_with_params(join_logs_message, user=member, guild=guild)
    embed.colour = member.colour

    return True, {"channel": join_logs_channel, "embed": embed}


async def message_params_processor(
    message: str,
    user: discord.User | discord.Member = None,
    guild: discord.Guild = None,
    level: Level = None,  # your Level ORM object
) -> str:
    """
    Replaces whitelisted placeholders for supported objects in the message string.
    Supports: {user.name}, {user.display_name}, {user.id}, {guild.name}, {guild.id},
              {user.level}, {user.xp}.
    """

    obj_map = {
        "user": user,
        "guild": guild,
    }

    def replace(match: re.Match) -> str:
        obj_type = match.group(1)
        attr = match.group(2)
        obj = obj_map.get(obj_type)

        # 1. Check normal user/guild attributes
        if obj is not None and hasattr(obj, attr):
            return str(getattr(obj, attr))

        # 2. Check level object for xp/level
        if obj_type == "user" and level is not None and hasattr(level, attr):
            return str(getattr(level, attr))

        # 3. Fallback: leave placeholder as-is
        return match.group(0)

    return settings.PARSER_PATTERN.sub(replace, message)


async def process_message_with_params(
        message: str,
        user: discord.User | discord.Member = None,
        guild: discord.Guild = None,
) -> str:
    """
    Conditionally fetches Level object only if {user.level} or {user.xp} exist,
    then calls the parser.
    """
    level_placeholder_pattern = re.compile(r"{user\.(level|xp)}")
    level_obj = None

    if level_placeholder_pattern.search(message) and user and guild:
        level_obj = await Level.objects.get(user=user.id, guild=guild.id)

    return await message_params_processor(message, level=level_obj, user=user, guild=guild)

def truncate_text(draw, text, font, max_width):
    ellipsis = "..."
    if draw.textlength(text, font=font) <= max_width:
        return text
    else:
        while draw.textlength(text + ellipsis, font=font) > max_width and len(text) > 0:
            text = text[:-1]
        return text + ellipsis