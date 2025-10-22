import discord
from discord.ext import commands

from ORM import User
from main import config
from modules.checks.utility import handle_traceback


class CommandChecks(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        bot.add_check(self.global_check)  # Register the check

    def cog_unload(self):
        self.bot.remove_check(self.global_check)  # Clean up when cog is unloaded

    async def global_check(self, ctx: discord.ApplicationContext):
        """Check if the user is active."""
        user, _ = await User.objects.get_or_create(id=ctx.user.id)

        if not user.is_active:
            await ctx.respond(
                "`[403]` **Your account has been deactivated.**", ephemeral=True
            )
            return False

        return True

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error):
        """Handle command errors globally."""
        if isinstance(error, commands.CheckFailure):
            return await ctx.respond(
                "`[403]` **You do not have permission to use this command.**",
                ephemeral=True,
            )
        elif isinstance(error, discord.errors.CheckFailure):
            return await ctx.respond(
                f"The {ctx.command.cog.qualified_name.lower()} module is currently disabled."
            )

        if config.get("debug"):
            return await ctx.respond(
                f"`[500]` **{error.__class__.__name__}**\n{error}",
                ephemeral=True,
            )

        command = ctx.command or "Unknown command"
        message_response = await handle_traceback(self.bot, command, error)

        return await ctx.respond(message_response, ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(CommandChecks(bot))
