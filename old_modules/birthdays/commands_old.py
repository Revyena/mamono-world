import discord
from discord import SlashCommandGroup

from ORM.models.Birthday import Birthday
from modules.birthdays.modals import BirthdayModal


class BirthdayCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    birthday = SlashCommandGroup("birthday", "Manage your birthday")

    @birthday.command(name="set", description="Set your birthday")
    async def set_birthday(self, ctx: discord.ApplicationContext):
        modal = BirthdayModal()
        await ctx.send_modal(modal)

    @birthday.command(name="get", description="Get your birthday")
    async def get_birthday(self, ctx: discord.ApplicationContext):
        birthday = await Birthday.objects.filter(guild=ctx.guild.id).get(user=ctx.user.id)
        if birthday:
            await ctx.respond(
                f"Your birthday is set to {birthday.date.strftime('%B %-d, %Y')}",
                ephemeral=True,
            )
        else:
            await ctx.respond("You have not set a birthday yet.", ephemeral=True)

    @birthday.command(name="delete", description="Delete your birthday")
    async def delete_birthday(self, ctx: discord.ApplicationContext):
        birthday = await Birthday.objects.filter(guild=ctx.guild.id).get(user=ctx.user.id)
        if birthday:
            await birthday.delete()
            await ctx.respond("Your birthday has been deleted.", ephemeral=True)
        else:
            await ctx.respond("You have not set a birthday yet.", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(BirthdayCog(bot))
