import os
from io import BytesIO
from typing import List, TypeVar

import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from discord import NotFound, HTTPException
from resources.resources import Level as LevelObject
from resources.levels import Level

here = os.path.dirname(os.path.abspath(__file__))  # projectroot/modules/leveling
font_path = os.path.normpath(os.path.join(here, "..", "..", "files", "PressStart2P-Regular.ttf"))


async def generate_rank_card(user: discord.User, level_data: LevelObject):
    # Card setup
    card_width, card_height = 800, 240
    card = Image.new("RGBA", (card_width, card_height), (13, 13, 13, 255))  # Shadow's black
    draw = ImageDraw.Draw(card)

    font_big = ImageFont.truetype(font_path, 30)  # Bigger for username
    font_small = ImageFont.truetype(font_path, 28)
    font_xp = ImageFont.truetype(font_path, 24)

    # Avatar
    avatar_asset = user.display_avatar.replace(static_format="png")
    avatar_bytes = await avatar_asset.read()
    avatar = Image.open(BytesIO(avatar_bytes)).resize((160, 160)).convert("RGBA")
    avatar = ImageOps.expand(avatar, border=4, fill=(200, 0, 0))
    card.paste(avatar, (30, 40), avatar)

    # User info position
    info_x = 210
    top_y = 50

    # Draw username
    draw.text((info_x, top_y), f"{user.display_name}", font=font_big, fill=(255, 255, 255))

    # Level and XP
    level = level_data.level
    xp = level_data.experience
    next_level_xp = Level.total_xp_for_level(level + 1)
    current_level_xp = Level.total_xp_for_level(level)
    progress = (xp - current_level_xp) / (next_level_xp - current_level_xp)
    progress = max(0.0, min(progress, 1.0))

    draw.text((info_x, top_y + 50), f"Level {level}", font=font_small, fill=(220, 0, 0))
    draw.text((info_x, top_y + 90), f"{xp} / {next_level_xp} XP", font=font_xp, fill=(180, 180, 180))

    # XP bar
    bar_x = info_x
    bar_y = top_y + 130
    bar_width = 560
    bar_height = 25

    draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=(40, 40, 40))

    glow = Image.new("RGBA", (bar_width, bar_height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rectangle([0, 0, int(bar_width * progress), bar_height], fill=(255, 0, 0, 200))
    glow = glow.filter(ImageFilter.GaussianBlur(4))
    card.paste(glow, (bar_x, bar_y), glow)

    draw.rectangle(
        [bar_x, bar_y, bar_x + int(bar_width * progress), bar_y + bar_height],
        fill=(255, 0, 0)
    )

    # Finalize
    buffer = BytesIO()
    card.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="shadow_rank_card.png")


async def generate_leaderboard(
    bot: discord.Bot,
    users: List[TypeVar("LevelT", bound=Level)],
    start_index=0,
    current_user_id=None,
    page=1,
    total_pages=1
) -> discord.Embed:
    """
    Generates a Discord embed representing the leaderboard.
    Check versions below 4.0.0 for PIL-based card generation.

    :param bot: The Discord bot instance
    :param users: List of Level ORM objects
    :param start_index: The starting index for numbering
    :param current_user_id: The ID of the user viewing the leaderboard
    :param page: Current page number
    :param total_pages: Total number of pages
    :return: A Discord Embed object
    """
    embed = discord.Embed(
        title="🏆 Server Leaderboard",
        colour=discord.Color.blurple(),
        description="Top members by XP!"
    )

    lines = []
    max_name_len = 0

    for idx, level in enumerate(users, start=start_index + 1):
        if level.xp <= 0:
            continue

        try:
            discord_user = bot.get_user(level.user) or await bot.fetch_user(level.user)
        except (NotFound, HTTPException):
            print(f"Could not fetch user {level.user}. Skipping...")
            continue

        display_name = f"➡{discord_user.display_name}" if level.user == current_user_id else discord_user.display_name
        max_name_len = max(max_name_len, len(display_name))

        lines.append((idx, display_name, level.level, level.xp))

    # Apply padding & formatting
    formatted_lines = [
        f"{str(idx).zfill(2)} {name:<{max_name_len + 4}} Lvl {lvl:<3} | {xp} XP"
        for idx, name, lvl, xp in lines
    ]

    if not formatted_lines:
        formatted_lines.append("No users with XP yet.")

    embed.add_field(
        name="Members",
        value=f"```{chr(10).join(formatted_lines)}```",
        inline=False
    )

    embed.set_footer(text=f"Page {page} / {total_pages}")

    return embed