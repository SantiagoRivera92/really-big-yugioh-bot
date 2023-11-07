
from typing import List

from discord import app_commands
from discord import Interaction

from src.utils import ReallyBigYugiohBot
from src.card_collection import CardCollection
from src.card_embeds import cardToEmbed

from src.commands.generic_command_manager import GenericCommandManager

import src.strings as Strings

class CardCommandManager(GenericCommandManager):

    def __init__(self, bot:ReallyBigYugiohBot, card_collection:CardCollection):
        super().__init__(card_collection)
        self.bot = bot
        self.add_commands()

    def add_commands(self):
        @self.bot.tree.command(name=Strings.COMMAND_NAME_CARD, description="Displays card text for any given card name")
        async def card(interaction: Interaction, cardname: str):
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message())
                return
            await interaction.response.defer()
            channel_name = self.get_channel_name(interaction.channel)
            server_id = interaction.guild_id
            supported_formats = self.config.get_supported_formats(server_id)
            if len(supported_formats) == 0:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
                return
            forced_format = self.config.get_forced_format(channel_name, server_id)
            card = self.card_collection.getCardFromCardName(cardname)
            if card is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_CARDS_WITH_NAME % cardname)
            else:
                if forced_format is not None:
                    banlist_file = self.config.get_banlist_for_format(forced_format, server_id)
                    embed = cardToEmbed(card, banlist_file, forced_format, self.bot)
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)

        @self.bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_CHANGE_CARD_STATUS, description="Changes the status of a card in the banlist tied to this channel.")
        async def change_status(interaction: Interaction, cardname: str, status: int):
            result = self.can_command_execute(interaction, True)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            server_id = interaction.guild_id
            channel_name = self.get_channel_name(interaction.channel)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            if forced_format is None:
                await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMAT_TIED, ephemeral=True)
                return
            card = self.card_collection.getCardFromCardName(cardname)
            if card is None:
                await interaction.response.send_message(Strings.ERROR_MESSAGE_ABSOLUTE_SEARCH_FAILED % cardname, ephemeral=True)
                return
            if status < -1 or status > 3:
                await interaction.response.send_message(Strings.ERROR_MESSAGE_WRONG_STATUS, ephemeral=True)
                return
            result = self.config.change_status(forced_format, interaction.guild_id, card.get("id"), card.get("name"), status)
            await interaction.response.send_message(result.get_message(), ephemeral=True)
            
        @card.autocomplete("cardname")
        @change_status.autocomplete("cardname")
        async def card_autocomplete(interaction: Interaction, current: str) -> List[app_commands.Choice[str]]:
            choices: List[app_commands.Choice[str]] = []
            if len(current) >= 3:
                self.card_collection.refreshCards()
                cards = self.card_collection.getCardsFromPartialCardName(current)
                for card in cards:
                    if len(choices) < 25:
                        choice = app_commands.Choice(name=card, value=card)
                        choices.append(choice)
                    else:
                        continue
            return choices
        @change_status.autocomplete("status")
        async def status_autocomplete(interaction:Interaction, current:int) -> List[app_commands.Choice[int]]:
            choices: List[app_commands.Choice[int]] = []
            for i in range(-1, 4):
                choices.append(app_commands.Choice(name=f"{i}",value=i))
            return choices