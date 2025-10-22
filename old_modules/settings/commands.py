import discord
from discord.ext import commands as ext_commands
from managers import settings_manager, SettingsManager
from managers.settings.guild_settings import SettingKey
from modules.leveling.utils import process_message_with_params
from modules.settings.modals import JoinLogModal


class SettingsCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    settings = discord.SlashCommandGroup("settings", "Setting commands", default_member_permissions=discord.Permissions(manage_guild=True))
    level = settings.create_subgroup("level", "Leveling settings")
    logs = settings.create_subgroup("logs", "Log settings")

    @level.command()
    @discord.option("enabled", bool, description="Enable or disable leveling")
    async def toggle(self, ctx: discord.ApplicationContext, enabled):
        await settings_manager.set(scope_type=SettingsManager.SCOPES_GUILD, scope_id=ctx.guild_id, setting_key=SettingKey.LEVEL_UP_ENABLED, value=enabled)
        await ctx.respond(f"Leveling has been {'enabled' if enabled else 'disabled'}!")

    @level.command()
    @discord.option("message", str, description="The new level-up message")
    async def message(self, ctx: discord.ApplicationContext, message):
        await settings_manager.set(scope_type=SettingsManager.SCOPES_GUILD, scope_id=ctx.guild_id, setting_key=SettingKey.LEVEL_UP_MESSAGE, value=message)
        parsed_message = await process_message_with_params(message, user=ctx.author, guild=ctx.guild)
        await ctx.respond(f"Level-up message updated to:\n\n{message}\n\nExample: {parsed_message}")

    @logs.command()
    @discord.option("channel", discord.TextChannel, required=False, description="Channel for join logs")
    async def join(self, ctx: discord.ApplicationContext, channel: discord.TextChannel = None):
        """
        Optional channel selection via command.
        Enable/disable and message are handled via the JoinLogModal.
        """

        modal = await JoinLogModal.create(ctx.guild, channel)
        await ctx.send_modal(modal)

def setup(bot: discord.Bot):
    bot.add_cog(SettingsCog(bot))
