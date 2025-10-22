import discord
from discord.ui import Modal, InputText
from managers import settings_manager, SettingsManager
from managers.settings.guild_settings import SettingKey

def is_truthy(value):
    return str(value).strip().lower() in ("true", "1", "yes", "on", "y", "t", "enabled", "enable")

class JoinLogModal(Modal):
    def __init__(self, guild: discord.Guild, channel: discord.TextChannel = None, enabled: str = "", message: str = ""):
        super().__init__(title="Join Log Settings")
        self.guild = guild
        self.channel = channel

        self.enabled_status = InputText(label="Enable Join Logs", value=enabled)
        self.message = InputText(label="Join Log Message", value=message)
        self.add_item(self.enabled_status)
        self.add_item(self.message)

    @classmethod
    async def create(cls, guild: discord.Guild, channel: discord.TextChannel = None):
        """Async factory to fetch current settings before creating the modal."""
        enabled_value = await settings_manager.get(SettingsManager.SCOPES_GUILD, guild.id, SettingKey.LOGS_JOIN_ENABLED)
        message_value = await settings_manager.get(SettingsManager.SCOPES_GUILD, guild.id, SettingKey.LOGS_JOIN_MESSAGE)

        enabled_str = "yes" if enabled_value else "no"
        return cls(guild, channel, enabled=enabled_str, message=message_value)

    async def callback(self, interaction: discord.Interaction):
        enabled_input = self.enabled_status.value.strip()
        message_input = self.message.value.strip() or None

        enabled = is_truthy(enabled_input) if enabled_input else False

        # Validate channel if enabling logs
        current_channel = self.channel or await settings_manager.get(
            SettingsManager.SCOPES_GUILD,
            self.guild.id,
            SettingKey.LOGS_JOIN_CHANNEL_ID
        )
        if enabled and not current_channel:
            return await interaction.response.send_message(
                "You must provide a channel if join logs are enabled.",
                ephemeral=True
            )

        # Save updated settings
        await settings_manager.set(SettingsManager.SCOPES_GUILD, self.guild.id, SettingKey.LOGS_JOIN_ENABLED, enabled)
        if self.channel:
            await settings_manager.set(SettingsManager.SCOPES_GUILD, self.guild.id, SettingKey.LOGS_JOIN_CHANNEL_ID, self.channel.id)
        await settings_manager.set(SettingsManager.SCOPES_GUILD, self.guild.id, SettingKey.LOGS_JOIN_MESSAGE, message_input)

        return await interaction.response.send_message("Join logs settings updated successfully!", ephemeral=True)
