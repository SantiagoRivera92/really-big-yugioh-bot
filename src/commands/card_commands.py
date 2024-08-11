
from typing import List
from typing import Literal

from discord import app_commands
from discord import Interaction

from src.card.card_embeds import card_to_embed

from src.commands.generic_command_manager import GenericCommandManager

import src.strings as Strings

class CardCommandManager(GenericCommandManager):

    def add_commands(self):
        @self.bot.tree.command(name=Strings.COMMAND_NAME_CARD, description="Displays card text for any given card name")
        async def card(interaction: Interaction, cardname: str):
            self.identify_command(interaction, Strings.COMMAND_NAME_CARD, cardname)
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
            if "Edison" in forced_format:
                card = self.card_collection.get_card_from_card_name_edison(cardname)
            else:
                card = self.card_collection.get_card_from_card_name(cardname)
            if card is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_CARDS_WITH_NAME % cardname)
            else:
                if forced_format is not None:
                    banlist_file = self.config.get_banlist_for_format(forced_format, server_id)
                    embed = card_to_embed(card, banlist_file, forced_format, self.bot)
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)

        @self.bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_CHANGE_CARD_STATUS, description="Changes the status of a card in the banlist tied to this channel.")
        async def change_status(interaction: Interaction, cardname: str, card_status: Literal["Illegal", "Forbidden", "Limited", "Semi-Limited", "Unlimited"]):
            self.identify_command(interaction, Strings.COMMAND_NAME_FORMAT_CHANGE_CARD_STATUS, cardname, card_status)
            result = self.can_command_execute(interaction, True)
            if card_status == "Illegal":
                status = -1
            elif card_status == "Forbidden":
                status = 0
            elif card_status == "Limited":
                status = 1
            elif card_status == "Semi-Limited":
                status = 2
            else:
                status = 3
            
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            server_id = interaction.guild_id
            channel_name = self.get_channel_name(interaction.channel)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            if forced_format is None:
                await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMAT_TIED, ephemeral=True)
                return
            if "Edison" in forced_format:
                card = self.card_collection.get_card_from_card_name_edison(cardname)
            else:
                card = self.card_collection.get_card_from_card_name(cardname)
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
                cards = self.card_collection.get_cards_from_partial_card_name(current)
                for card in cards:
                    if len(choices) < 25:
                        choice = app_commands.Choice(name=card, value=card)
                        choices.append(choice)
                    else:
                        continue
            return choices