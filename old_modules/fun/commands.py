import discord, random
from discord import commands

class FunCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    fun = commands.SlashCommandGroup("fun", "Fun commands")

    @fun.command()
    async def magic8ball(self, ctx: discord.ApplicationContext, question: str):
        responses = [
            "Yes", "No", "Maybe", "Ask again later", "Definitely",
            "Absolutely not", "It is certain", "Very doubtful"
        ]

        response = random.choice(responses)

        await ctx.respond(f"**To the question:** {question}\n🎱 **Magic 8-Ball says:** {response}")

def setup(bot: discord.Bot):
    bot.add_cog(FunCog(bot))