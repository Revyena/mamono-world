"""
Central file for all modals relating to birthday commands.
"""

from datetime import datetime
import discord

from ORM.models.Birthday import Birthday


class BirthdayModal(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="Set your birthday!")

        self.add_item(discord.ui.InputText(label="Day (1-31)"))
        self.add_item(discord.ui.InputText(label="Month (1-12)"))
        self.add_item(discord.ui.InputText(label="Year (e.g. 1990)"))

    async def callback(self, interaction: discord.Interaction):
        try:
            day = int(self.children[0].value.strip())
            month = int(self.children[1].value.strip())
            year = int(self.children[2].value.strip())

            birthday_date = datetime(year, month, day).date()
        except ValueError:
            await interaction.response.send_message(
                "Invalid date entered."
                "Make sure day is a number,"
                "month is full/short name, year is a number.",
                ephemeral=True,
            )
            return

        birthday = Birthday()
        birthday.date = birthday_date
        birthday.user = interaction.user.id
        birthday.guild = interaction.guild.id
        await birthday.save()

        await interaction.response.send_message(
            f"Birthday set to {birthday_date.strftime('%B %-d, %Y')}", ephemeral=True
        )
