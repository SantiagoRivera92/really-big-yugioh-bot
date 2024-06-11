import os

from typing import List

from discord import Interaction, Attachment, File, Embed, app_commands

from src.commands.generic_command_manager import GenericCommandManager
from src.deck.deck_validation import Deck, Ydk
from src.deck.deck_collection import DeckCollectionManager
from src.duelingbook.duelingbook import DuelingbookManager

import src.strings as Strings


class DeckCommandManager(GenericCommandManager):

    def ydk_to_discord_file(self, ydk_file: str, player_name: str):
        file_name = f"{player_name}.ydk"
        return File(filename=file_name, fp=ydk_file)

    def validate_ydk(self, format_name, ydk_file: str, server_id: int):
        banlist_file = self.config.get_banlist_for_format(format_name, server_id)
        if self.config.is_format_supported(format_name, server_id):
            result = self.deck_validator.validate_deck(ydk_file, banlist_file)
            if result.was_successful():
                return Strings.BOT_MESSAGE_DECK_VALID % format_name
            return Strings.ERROR_MESSAGE_DECK_INVALID % (format_name, result.get_message())
        return Strings.ERROR_MESSAGE_FORMAT_UNSUPPORTED % format_name

    def get_readable_list(self, readable_decklist: Deck) -> str:
        readable = "Main deck:\n\n"
        for card in readable_decklist.main:
            card_name = self.card_collection.get_card_name_from_id(card.card_id)
            readable = f"{readable}{card.copies}x {card_name}\n"
        readable = f"{readable}\nExtra Deck:\n\n"
        for card in readable_decklist.extra:
            card_name = self.card_collection.get_card_name_from_id(card.card_id)
            readable = f"{readable}{card.copies}x {card_name}\n"
        readable = f"{readable}\nSide Deck:\n\n"
        for card in readable_decklist.side:
            card_name = self.card_collection.get_card_name_from_id(card.card_id)
            readable = f"{readable}{card.copies}x {card_name}\n"
        return readable


    def add_commands(self):
        
        @self.bot.tree.command(name=Strings.COMMAND_NAME_DECK_VALIDATE, description="Validates a deck")
        async def validate_deck(interaction: Interaction, ydk: Attachment):
            self.identify_command(interaction, Strings.COMMAND_NAME_DECK_VALIDATE)
            server_id = interaction.guild_id
            result = self.can_command_execute(interaction, False)
            if result.was_successful():
                supported_formats = self.config.get_supported_formats(server_id)
                if len(supported_formats) == 0:
                    await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
                    return
                await interaction.response.defer(ephemeral=True)
                if ydk.filename.endswith(".ydk"):
                    channel_name = self.get_channel_name(interaction.channel)
                    forced_format = self.config.get_forced_format(channel_name, server_id)
                    if forced_format is None:
                        supported_formats = self.config.get_supported_formats(server_id)
                        if len(supported_formats) > 0:
                            await interaction.followup.send(Strings.ERROR_MESSAGE_NO_DEFAULT_FORMAT)
                        else:
                            await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
                    else:
                        ydk_as_string = await ydk.read()
                        ydk_as_string = ydk_as_string.decode("utf-8")
                        validation = self.validate_ydk(forced_format, ydk_as_string, server_id)
                        await interaction.followup.send(validation)
                else:
                    await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_DECK_FORMAT)
            else:
                await interaction.response.send_message(result.get_message())

        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_YDK_DECK, description="Gets a decklist as a YDK file")
        async def get_ydk_decklist(interaction: Interaction, player_name: str):
            self.identify_command(interaction, Strings.COMMAND_NAME_TOURNAMENT_YDK_DECK, player_name)
            server_id = interaction.guild_id
            player_name = f"{interaction.user.name}"
            result = self.can_command_execute(interaction, True)
            if result.was_successful():
                supported_formats = self.config.get_supported_formats(server_id)
                if len(supported_formats) == 0:
                    await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
                    return
                await interaction.response.defer(ephemeral=True)
                channel_name = self.get_channel_name(interaction.channel)
                forced_format = self.config.get_forced_format(channel_name, server_id)
                deck_collection_manager = DeckCollectionManager(forced_format, server_id)
                players = deck_collection_manager.get_registered_players()
                found = False
                for player in players:
                    if player_name.lower() in player.lower():
                        found = True
                        player_name = player
                        break
                if not found:
                    await interaction.followup.send(f"{player_name} doesn't have a submitted decklist")
                    return
                filename = deck_collection_manager.get_decklist_for_player(player_name)
                file = self.ydk_to_discord_file(filename, player_name)
                await interaction.followup.send(file=file)
            else:
                await interaction.response.send_message(result.get_message())


        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_IMG_DECK, description="Gets a decklist as an image")
        async def get_img_deck(interaction: Interaction, player_name: str):
            self.identify_command(interaction, Strings.COMMAND_NAME_TOURNAMENT_IMG_DECK, player_name)
            server_id = interaction.guild_id
            result = self.can_command_execute(interaction, True)
            if result.was_successful():
                supported_formats = self.config.get_supported_formats(server_id)
                if len(supported_formats) == 0:
                    await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
                    return
                await interaction.response.defer(ephemeral=True)
                channel_name = self.get_channel_name(interaction.channel)
                forced_format = self.config.get_forced_format(channel_name, server_id)
                deck_collection_manager = DeckCollectionManager(forced_format, server_id)
                players = deck_collection_manager.get_registered_players()
                found = False
                for player in players:
                    if player_name.lower() in player.lower():
                        found = True
                        player_name = player
                        break
                if not found:
                    await interaction.followup.send(f"{player_name} doesn't have a submitted decklist")
                    return
                filename = deck_collection_manager.get_decklist_for_player(player_name)
                with open(filename, encoding="utf-8") as deck_file:
                    deck = deck_file.read()
                    ydk = Ydk(deck)

                    channel_name = self.get_channel_name(interaction.channel)
                    forced_format = self.config.get_forced_format(channel_name, server_id)
                    banlist_file = self.config.get_banlist_for_format(forced_format, server_id)
                    image = self.deck_images.build_image_with_format(ydk.get_deck(), "temp", player_name, forced_format, banlist_file)
                    image_url = self.uploader.upload_image(image)

                    embed = Embed(title=player_name)
                    embed.set_image(url="attachment://deck.jpg")
                    embed.add_field(name="", value=f"[See high resolution decklist]({image_url})")

                    with open(image, "rb") as fp:
                        image_file = File(fp, filename="deck.jpg")
                
                    await interaction.followup.send(embed=embed, file=image_file)

                    os.remove(image)
            else:
                await interaction.response.send_message(result.get_message())

        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_TXT_DECK, description="Gets a decklist in readable form")
        async def get_readable_decklist(interaction: Interaction, player_name: str):
            self.identify_command(interaction, Strings.COMMAND_NAME_TOURNAMENT_TXT_DECK, player_name)
            server_id = interaction.guild_id
            result = self.can_command_execute(interaction, True)
            if result.was_successful():
                supported_formats = self.config.get_supported_formats(server_id)
                if len(supported_formats) == 0:
                    await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
                    return
                await interaction.response.defer(ephemeral=True)
                channel_name = self.get_channel_name(interaction.channel)
                forced_format = self.config.get_forced_format(channel_name, server_id)
                deck_collection_manager = DeckCollectionManager(forced_format, server_id)
                players = deck_collection_manager.get_registered_players()
                found = False
                for player in players:
                    if player_name.lower() in player.lower():
                        found = True
                        player_name = player
                        break
                if not found:
                    await interaction.followup.send(Strings.ERROR_MESSAGE_NO_SUBMITTED_DECKLIST % player_name)
                    return
                readable_decklist = deck_collection_manager.get_readable_decklist_for_player(player_name)
                readable = self.get_readable_list(readable_decklist)
                await interaction.followup.send(readable)
            else:
                await interaction.response.send_message(result.get_message())
                
        @self.bot.tree.command(name=Strings.COMMAND_NAME_SHARE_DECK_YDK_TXT, description="Shares a deck as text")
        async def share_ydk_txt(interaction:Interaction, ydk: Attachment):
            self.identify_command(interaction, Strings.COMMAND_NAME_SHARE_DECK_YDK_TXT)
            server_id = interaction.guild_id
            result = self.can_command_execute(interaction, False)
            if result.was_successful():
                supported_formats = self.config.get_supported_formats(server_id)
                if len(supported_formats) == 0:
                    await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
                    return
                await interaction.response.defer(ephemeral=False)
                if ydk.filename.endswith(".ydk"):
                    ydk_as_string = await ydk.read()
                    ydk_as_string = ydk_as_string.decode("utf-8")
                    readable_decklist = Ydk(ydk_as_string).get_deck()
                    readable = self.get_readable_list(readable_decklist)
                    await interaction.followup.send(readable)
                else:
                    await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_DECK_FORMAT)
            else:
                await interaction.response.send_message(result.get_message())


        @self.bot.tree.command(name=Strings.COMMAND_NAME_SHARE_DECK_YDK, description="Shares an image of a YDK deck")
        async def share_ydk(interaction: Interaction, ydk: Attachment):
            self.identify_command(interaction, Strings.COMMAND_NAME_SHARE_DECK_YDK)
            server_id = interaction.guild_id
            result = self.can_command_execute(interaction, False)
            if result.was_successful():
                supported_formats = self.config.get_supported_formats(server_id)
                if len(supported_formats) == 0:
                    await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
                    return
                await interaction.response.defer(ephemeral=False)
                if ydk.filename.endswith(".ydk"):
                    ydk_as_string = await ydk.read()
                    ydk_as_string = ydk_as_string.decode("utf-8")
                    decklist = Ydk(ydk_as_string).get_deck()
                    filename = ydk.filename.replace("_", " ")[:-4]
                    channel_name = self.get_channel_name(interaction.channel)
                    forced_format = self.config.get_forced_format(channel_name, server_id)
                    banlist_file = self.config.get_banlist_for_format(forced_format, server_id)
                    image = self.deck_images.build_image_with_format(decklist, "temp", filename, forced_format, banlist_file)
                    with open("img/decks/temp.ydk", 'w', encoding="utf-8") as file:
                        deck_as_lines = ydk_as_string.split("\n")
                        for line in deck_as_lines:
                            line = line.replace("\n", "").replace("\r", "")
                            if len(line) > 0:
                                file.write(line)
                                file.write("\n")

                    image_url = self.uploader.upload_image(image)
                    embed = Embed(title=filename)
                    embed.set_image(url="attachment://deck.jpg")
                    embed.add_field(name="", value=f"[See high resolution decklist]({image_url})")

                    with open(image, "rb") as fp:
                        image_file = File(fp, filename="deck.jpg")
                        await interaction.followup.send(embed=embed, file=image_file)
                else:
                    await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_DECK_FORMAT)
            else:
                await interaction.response.send_message(result.get_message())
                
        @self.bot.tree.command(name=Strings.COMMAND_NAME_SHARE_DECK_DB, description="Shares an image of a Duelingbook deck")
        async def share_ydk_db(interaction: Interaction, db_url:str):
            self.identify_command(interaction, Strings.COMMAND_NAME_SHARE_DECK_DB, db_url)
            server_id = interaction.guild_id
            result = self.can_command_execute(interaction, False)
            if result.was_successful():
                formats = self.config.get_supported_formats(server_id)
                if len(formats) == 0:
                    await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
                    return
                await interaction.response.defer(ephemeral=False)

                manager = DuelingbookManager()
                result = manager.is_valid_url(db_url)
                if not result.was_successful():
                    await interaction.followup.send(result.get_message())
                    return

                deck = manager.get_ydk_from_db("temp", db_url)
                deck_name = manager.get_deck_name_from_db(db_url)
                ydk = Ydk(deck)
                
                channel_name = self.get_channel_name(interaction.channel)
                forced_format = self.config.get_forced_format(channel_name, server_id)
                banlist_file = self.config.get_banlist_for_format(forced_format, server_id)
                image = self.deck_images.build_image_with_format(ydk.get_deck(), "temp", deck_name, forced_format, banlist_file)
                image_url = self.uploader.upload_image(image)

                embed = Embed(title=deck_name)
                embed.set_image(url="attachment://deck.jpg")
                embed.add_field(name="", value=f"[See high resolution decklist]({image_url})", inline=False)
                embed.add_field(name="", value=f"[See deck in Duelingbook]({db_url})", inline=False)

                with open(image, "rb") as fp:
                    image_file = File(fp, filename="deck.jpg")

                await interaction.followup.send(embed=embed, file=image_file)

            else:
                await interaction.response.send_message(result.get_message())
                        
        @get_img_deck.autocomplete("player_name")
        @get_ydk_decklist.autocomplete("player_name")
        @get_readable_decklist.autocomplete("player_name")
        async def player_autocomplete_for_decklist(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
            choices: List[app_commands.Choice[str]] = []
            server_id = interaction.guild_id
            channel_name = self.get_channel_name(interaction.channel)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            deck_collection_manager = DeckCollectionManager(forced_format, server_id)
            registered_players = deck_collection_manager.get_registered_players()
            for player in registered_players:
                if current.lower() in player.lower():
                    if len(choices) < 25:
                        choice = app_commands.Choice(name=player, value=player)
                        choices.append(choice)
            return choices