from discord import Interaction
import discord

from src.config.server_config import ServerConfig
from src.config.config import Config
from src.card_collection import CardCollection

from src.utils import get_channel_name, OperationResult

import src.strings as Strings

class GenericCommandManager:
    
    def __init__(self, card_collection:CardCollection):
        self.server_config = ServerConfig()
        self.card_collection = card_collection
        self.config = Config(card_collection)
    
    def can_command_execute(self, interaction: Interaction, admin_only):
        server_id = interaction.guild_id
        result = self.server_config.check_server_enabled(server_id)
        if not result.was_successful():
            return result

        role = discord.utils.get(interaction.guild.roles, name="Tournament Staff")
        is_staff = role in interaction.user.roles

        channel_name = get_channel_name(interaction.channel)
        enabled = self.config.is_channel_enabled(channel_name, server_id)

        if not enabled:
            return OperationResult(False, Strings.ERROR_MESSAGE_BOT_DISABLED_IN_CHANNEL)
        if admin_only:
            is_admin = interaction.user.guild_permissions.administrator
            if not is_admin:
                # God-like powers
                if interaction.user.id == 164008587171987467:
                    return OperationResult(True, "")
                if is_staff:
                    return OperationResult(True, "")
                return OperationResult(False, Strings.ERROR_MESSAGE_NOT_AN_ADMIN)
        return OperationResult(True, "")
    
    def is_valid_filename(self, filename: str):
        if len(filename) == 0:
            return OperationResult(False, Strings.ERROR_FORMAT_NAME_EMPTY)
        invalid_characters = "#%&\{\}\\<>*?/$!\'\":@+`|="
        for char in invalid_characters:
            if char in filename:
                return OperationResult(False, Strings.ERROR_FORMAT_NAME_INVALID_CHARACTER % char)
        if filename == "Advanced":
            return OperationResult(False, Strings.ERROR_FORMAT_NAME_ADVANCED)
        return OperationResult(True, "")