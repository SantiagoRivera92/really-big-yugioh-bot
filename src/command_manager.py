from typing import List

from src.utils.utils import ReallyBigYugiohBot

from src.commands.generic_command_manager import GenericCommandManager

from src.commands.card_commands import CardCommandManager
from src.commands.format_commands import FormatCommandManager
from src.commands.tournament_commands import TournamentCommandManager
from src.commands.deck_commands import DeckCommandManager
from src.commands.league_commands import LeagueCommandManager


from src.card.card_collection import CardCollection

class CommandManager:

    def __init__(self, bot:ReallyBigYugiohBot, card_collection:CardCollection):
        managers: List[GenericCommandManager] = [
            CardCommandManager(bot, card_collection),
            FormatCommandManager(bot, card_collection),
            TournamentCommandManager(bot, card_collection),
            DeckCommandManager(bot, card_collection),
            LeagueCommandManager(bot, card_collection)
            ]
        for manager in managers:
            manager.add_commands()