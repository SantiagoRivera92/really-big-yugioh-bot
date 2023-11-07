from src.utils import ReallyBigYugiohBot

from src.commands.card_commands import CardCommandManager
from src.commands.format_commands import FormatCommandManager
from src.commands.tournament_commands import TournamentCommandManager
from src.commands.deck_commands import DeckCommandManager
from src.commands.league_commands import LeagueCommandManager

from src.card_collection import CardCollection

class CommandManager:

    def __init__(self, bot:ReallyBigYugiohBot, card_collection:CardCollection):
        self.card_command_manager = CardCommandManager(bot, card_collection)
        self.format_command_manager = FormatCommandManager(bot, card_collection)
        self.tournament_command_manager = TournamentCommandManager(bot, card_collection)
        self.deck_command_manager = DeckCommandManager(bot, card_collection)
        self.league_command_manager = LeagueCommandManager(bot, card_collection)