from abc import ABC, abstractmethod

from discord import Interaction

import discord

from src.config.server_config import ServerConfig
from src.config.config import Config
from src.card.card_collection import CardCollection
from src.deck.deck_validation import DeckValidator
from src.credentials_manager import CredentialsManager
from src.deck.new_deck_images import DeckAsImageGenerator
from src.image_uploader import Uploader

from src.utils.utils import OperationResult, ReallyBigYugiohBot

import src.strings as Strings


DM_CHANNEL_KEY = "dm"
GROUP_CHANNEL_KEY = "group"
THREAD_CHANNEL_KEY = "thread"
OTHER_KEY = "other"

class GenericCommandManager(ABC):
    
    def __init__(self, bot:ReallyBigYugiohBot, card_collection:CardCollection):
        self.server_config = ServerConfig()
        self.bot = bot
        self.card_collection = card_collection
        self.config = Config()
        self.deck_validator = DeckValidator(card_collection)
        self.credentials = CredentialsManager()
        self.deck_images = DeckAsImageGenerator(card_collection)
        self.uploader = Uploader(self.credentials.get_cloudinary_cloud_name(), self.credentials.get_cloudinary_key(), self.credentials.get_cloudinary_secret())
    
    def get_channel_name(self, channel:discord.channel):
        if isinstance(channel, discord.channel.DMChannel):
            return DM_CHANNEL_KEY
        if isinstance(channel, discord.channel.GroupChannel):
            return GROUP_CHANNEL_KEY
        if isinstance(channel, discord.channel.Thread):
            return THREAD_CHANNEL_KEY
        if isinstance(channel, discord.channel.PartialMessageable):
            return OTHER_KEY
        return channel.name
    
    def identify_command(self, interaction: Interaction, command_name: str, *args):
        guild = interaction.guild.name
        author = interaction.user.name
        screen_name = interaction.user.display_name
        server_id = interaction.guild_id
        authorized = self.can_command_execute(interaction, False).success
        if authorized:
            # Print basic command information
            print(f"\nUser @{author} (@{screen_name}) called /{command_name} on server \"{guild}\" ({server_id}, server authorized)")
        else:
            print(f"\nUser @{author} (@{screen_name}) called /{command_name} on server \"{guild}\" ({server_id}, server unauthorized)")
        
        # Print positional arguments
        if args:
            print("    Positional arguments:")
            for arg in args:
                print(f"    - {arg}")
        print("")
    
    def can_command_execute(self, interaction: Interaction, admin_only):
        server_id = interaction.guild_id
        result = self.server_config.check_server_enabled(server_id)
        if not result.was_successful():
            return result

        role = discord.utils.get(interaction.guild.roles, name="Tournament Staff")
        is_staff = role in interaction.user.roles

        channel_name = self.get_channel_name(interaction.channel)
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
        return OperationResult(True, "")
    
    
    @abstractmethod
    def add_commands(self):
        pass