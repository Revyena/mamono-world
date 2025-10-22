import discord
from discord import commands
from discord.ext import commands as ext_commands
from modules.leveling.cards import generate_rank_card, generate_leaderboard
from modules.leveling.views import LeaderboardView
from resources.levels import Level


class LevelingCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = Level(bot)
        self.__cog_name__ = "Leveling"

    # async def cog_check(self, ctx):
    #     """Ensure the module is enabled."""
    #     is_module_enabled = await settings_manager.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=ctx.guild.id, setting_key=SettingKey.LEVEL_UP_ENABLED)
    #     return is_module_enabled

    level = commands.SlashCommandGroup("level", "Leveling commands")

    @level.command()
    async def rank(self, ctx):
        """Display your current rank and XP."""
        await ctx.defer(ephemeral=True)
        user_id = ctx.author.id
        level = await self.levels.get(ctx.user.id, ctx.guild.id)
        card = await generate_rank_card(ctx.author, level)
        await ctx.respond(file=card)

    @level.command()
    async def leaderboard(self, ctx):
        await ctx.defer(ephemeral=True)
        all_levels = await Level.objects.filter(guild=ctx.guild.id)
        if not all_levels:
            return await ctx.followup.send("No one has any XP yet!", ephemeral=True)

        sorted_users = sorted(all_levels, key=lambda l: l.xp, reverse=True)

        view = LeaderboardView(self.bot, sorted_users, current_user_id=ctx.author.id)
        first_slice = sorted_users[:view.page_size]
        embed = await generate_leaderboard(
            self.bot, first_slice, current_user_id=ctx.author.id, page=1,
            total_pages=(len(sorted_users) - 1) // view.page_size + 1
        )

        return await ctx.respond(embed=embed, view=view)

    @level.command()
    @ext_commands.has_guild_permissions(manage_guild=True)
    @discord.option("member", discord.Member, description="The member to change XP for")
    @discord.option("xp", int, description="The amount of XP to add (positive) or remove (negative)")
    async def change_xp(self, ctx, member: discord.Member, xp: int):
        """Change a user's XP by a specified amount."""
        level_data, _ = await Level.objects.get_or_create(user=member.id, guild=ctx.guild.id)
        level_data.xp += xp
        if level_data.xp < 0:
            level_data.xp = 0
        await level_data.save()

        await ctx.respond(f"{'added' if xp >= 0 else 'removed'} {abs(xp)} XP {'to' if xp >= 0 else 'from'} {member.display_name}. They now have {level_data.xp} XP.", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(LevelingCog(bot))
