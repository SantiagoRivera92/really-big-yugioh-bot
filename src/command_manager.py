from src.utils import ReallyBigYugiohBot
from src.commands.card_commands import CardCommandManager
from src.commands.format_commands import FormatCommandManager
from src.card_collection import CardCollection
from src.banlist_validation import BanlistValidator

class CommandManager:

    def __init__(self, 
                bot:ReallyBigYugiohBot, 
                card_collection:CardCollection, 
                banlist_validator:BanlistValidator):
        self.bot = bot
        self.card_command_manager = CardCommandManager(bot, card_collection)
        self.format_command_manager = FormatCommandManager(bot, card_collection, banlist_validator)
