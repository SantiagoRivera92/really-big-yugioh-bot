import os

from typing import List

from discord import Interaction, Attachment, app_commands, File, Embed

from src.commands.generic_command_manager import GenericCommandManager
from src.tournament.tournaments import TournamentManager
from src.utils.utils import ReallyBigYugiohBot, OperationResult
from src.card.card_collection import CardCollection
from src.deck.deck_validation import Ydk
from src.deck.deck_collection import DeckCollectionManager
from src.user_manager import UserManager
from src.league.matchmaking import MatchmakingManager
from src.duelingbook.duelingbook import DuelingbookManager

import src.strings as Strings
class TournamentCommandManager(GenericCommandManager):

    def __init__(self, bot:ReallyBigYugiohBot, card_collection:CardCollection):
        super().__init__(bot, card_collection)
        self.add_commands()
        
    def get_tournament_manager(self, interaction: Interaction):
        server_id = interaction.guild_id
        return TournamentManager(self.credentials, server_id)
        
    def add_commands(self):
    
        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_CREATE, description="Creates a new tournament. This deletes any previous tournaments and decklists!")
        async def create_tournament(interaction: Interaction, tournament_name: str, format_name: str, tournament_type: str):

            server_id = interaction.guild_id

            result = self.can_command_execute(interaction, True)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return

            supported_formats = self.config.get_supported_formats(server_id)

            if len(supported_formats) == 0:
                await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
                return

            found = False
            for _format in supported_formats:
                if _format.lower() == format_name.lower():
                    format_name = _format
                    found = True

            if not found:
                await interaction.response.send_message(Strings.ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET)
                return

            await interaction.response.defer(ephemeral=True)

            deck_collection_manager = DeckCollectionManager(format_name, server_id)

            deck_collection_manager.begin_collection()
            
            manager = self.get_tournament_manager(interaction)
            result = manager.create_tournament(
                tournament_name, format_name, tournament_type)
            await interaction.followup.send(result.get_message())

        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_START, description="Starts the tournament.")
        async def start_tournament(interaction: Interaction):
            server_id = interaction.guild_id
            result = self.can_command_execute(interaction, True)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=False)

            manager = self.get_tournament_manager(interaction)
            format_name = manager.get_tournament_format()
            DeckCollectionManager(format_name, server_id).end_collection()

            await interaction.followup.send(manager.start_tournament().get_message())

        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_END, description="Ends the tournament.")
        async def end_tournament(interaction: Interaction):
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)

            manager = self.get_tournament_manager(interaction)

            await interaction.followup.send(manager.end_tournament().get_message())

        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_INFO, description="Gets the tournament url")
        async def tournament_info(interaction: Interaction):
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=False)

            manager = self.get_tournament_manager(interaction)

            await interaction.followup.send(manager.get_tournament_info().get_message())

        def register_list(interaction: Interaction, _format: str, decklist:str):
            server_id = interaction.guild_id
            player_name = interaction.user.name
            player_id = interaction.user.id
            banlist_file = self.config.get_banlist_for_format(_format, server_id)
            path = None
            if self.config.is_format_supported(_format, server_id):
                result = self.deck_validator.validate_deck(decklist, banlist_file)
                if result.was_successful():
                    deck_collection_manager = DeckCollectionManager(_format, server_id)
                    result = deck_collection_manager.add_deck(player_name, decklist)
                    if result.was_successful():
                        path = deck_collection_manager.get_decklist_for_player(player_name)
                else:
                    print(f"{player_name}'s deck did not validate")
                    print(f"Reason: {result.get_message()}")
                    return result

            # At this point, decklist is updated.

            if path is not None:
                return self.get_tournament_manager(interaction).register_to_tournament(player_name, player_id, path)
            
            print(f"{player_name}'s decklist path is None.")
            return OperationResult(False, "Something went wrong while registering your list. Please contact Diamond Dude or try again.")

        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_JOIN_YDK, description="Registers to an open tournament using a .ydk, or updates your deck if already registered")
        async def register_ydk(interaction: Interaction, ydk: Attachment):
            result = self.can_command_execute(interaction, False)
            server_id = interaction.guild_id
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)

            manager = self.get_tournament_manager(interaction)
            forced_format = manager.get_tournament_format()
            if forced_format is None:
                await interaction.followup.send("There is no ongoing tournament in this server")
                return

            if ydk.filename.endswith(".ydk"):
                channel_name = self.get_channel_name(interaction.channel)
                forced_format = self.config.get_forced_format(channel_name, server_id)
                if self.config.is_format_supported(forced_format, server_id):
                    ydk_file = await ydk.read()
                    ydk_file = ydk_file.decode("utf-8")
                    await interaction.followup.send(register_list(interaction, forced_format, ydk_file).get_message())
            else:
                await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_DECK_FORMAT)
                
        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_JOIN_DB, description="Registers to a tournament using a db url, or updates your deck if already registered.")
        async def register_ydk_db(interaction: Interaction, duelingbook_link: str):
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)

            manager = self.get_tournament_manager(interaction)
            forced_format = manager.get_tournament_format()
            if forced_format is None:
                await interaction.followup.send("There is no ongoing tournament in this server")
                return

            manager = DuelingbookManager()
            player_name = interaction.user.name
            result = manager.is_valid_url(duelingbook_link)
            if not result.was_successful():
                await interaction.followup.send(result.get_message())
                return

            deck = manager.get_ydk_from_db(player_name, duelingbook_link)
            
            await interaction.followup.send(register_list(interaction, forced_format, deck).getMessage())

        @self.bot.tree.command(name=Strings.COMMAND_NAME_SET_DB_NAME, description="Sets your Duelingbook name for a tournament")
        async def set_db_name(interaction:Interaction, db_name:str):
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message())
                return

            await interaction.response.defer(ephemeral=True)
            if len(db_name) == 0:
                await interaction.followup.send("Username can't be empty")
                return
            
            manager = UserManager(interaction.guild_id)
            player_name = interaction.user.name
            manager.set_db_username(player_name, db_name)
            await interaction.followup.send(f"Duelingbook username set successfully to {db_name}")

        @self.bot.tree.command(name=Strings.COMMAND_NAME_GET_DB_NAME, description="Gets the Duelinbgook username for an user.")
        async def get_db_name(interaction:Interaction, player_name:str):
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message())
                return
            
            await interaction.response.defer(ephemeral=True)
            manager = UserManager(interaction.guild_id)
            db_name = manager.get_db_username(player_name)
            if db_name is None:
                await interaction.followup.send(f"{player_name} does not have a Duelingbook username set")
                return
            await interaction.followup.send(db_name)

        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_REPORT_LOSS, description="Reports you lost a tournament match")
        async def report_tournament_loss(interaction: Interaction):
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=False)
            server_id = interaction.guild_id
            player_name = interaction.user.name

            manager = TournamentManager(self.credentials, server_id)

            channel_name = self.get_channel_name(interaction.channel)
            forced_format = self.config.get_forced_format(channel_name, server_id)

            matchmaking_manager = MatchmakingManager(forced_format, server_id)

            t_winner = manager.get_winner_from_loser(player_name)

            if t_winner is not None:
                winner = matchmaking_manager.get_player_for_id(t_winner.discordId)
                loser = matchmaking_manager.get_player_for_id(interaction.user.id)
                if winner is None:
                    matchmaking_manager.register_player(t_winner.discordId, t_winner.username)
                if loser is None:
                    matchmaking_manager.register_player(interaction.user.id, player_name)
                matchmaking_manager.create_match(t_winner.discordId, interaction.user.id, True)
                matchmaking_manager.end_match(t_winner.discordId)

            result = manager.report_loss(player_name)
            await interaction.followup.send(result.get_message())

        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_FORCE_LOSS, description="Forces a player to lose a match")
        async def force_tournament_loss(interaction: Interaction, player_name: str):
            result = self.can_command_execute(interaction, True)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=False)
            server_id = interaction.guild_id
            manager = TournamentManager(self.credentials, server_id)
            channel_name = self.get_channel_name(interaction.channel)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            matchmaking_manager = MatchmakingManager(forced_format, server_id)
            t_winner = manager.get_winner_from_loser(player_name)
            if t_winner is not None:
                winner = matchmaking_manager.get_player_for_id(t_winner.discordId)
                loser = matchmaking_manager.get_player_for_id(interaction.user.id)
                if winner is None:
                    matchmaking_manager.register_player(t_winner.discordId, t_winner.username)
                if loser is None:
                    matchmaking_manager.register_player(interaction.user.id, player_name)
                matchmaking_manager.create_match(t_winner.discordId, interaction.user.id, True)
                matchmaking_manager.end_match(t_winner.discordId)
            result = manager.report_loss(player_name)
            await interaction.followup.send(result.get_message())

        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_DROP, description="Drop from the tournament")
        async def drop(interaction: Interaction):
            drop_enabled = False
            if not drop_enabled and interaction.guild_id == 459826576536764426:
                await interaction.response.send_message("Manual dropping is currently disabled. Please ask _tournament Staff to drop you.")
                return
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            server_id = interaction.guild_id
            player_name = interaction.user.name
            manager = TournamentManager(self.credentials, server_id)
            result = manager.drop(player_name)
            await interaction.followup.send(result.get_message())

        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_DQ, description="Removes a player from the tournament")
        async def dq(interaction: Interaction, player_name: str):
            result = self.can_command_execute(interaction, True)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=False)
            server_id = interaction.guild_id
            manager = TournamentManager(self.credentials, server_id)
            result = manager.drop(player_name)
            await interaction.followup.send(result.get_message())

        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_PRINT_ACTIVE_MATCHES, description="Gets a list of unfinished matches")
        async def active_matches(interaction: Interaction):
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=False)
            server_id = interaction.guild_id
            manager = TournamentManager(self.credentials, server_id)
            result = manager.get_readable_active_matches()
            await interaction.followup.send(result.get_message())
            
        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_CONFIRM_DECK, description="Shows the deck you have currently registered")
        async def confirm_deck(interaction: Interaction):
            server_id = interaction.guild_id
            result = self.can_command_execute(interaction, False)
            if result.was_successful():
                supported_formats = self.config.get_supported_formats(server_id)
                if len(supported_formats) == 0:
                    await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
                    return
                await interaction.response.defer(ephemeral=True)
                player_name = interaction.user.name
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
                    await interaction.followup.send("You haven't submitted a decklist. Do so by using /t_join_db or /t_join_ydk.")
                    return
                filename = deck_collection_manager.get_decklist_for_player(player_name)
                with open(filename, encoding="utf-8") as deck_file:
                    deck = deck_file.read()
                    ydk = Ydk(deck)

                    image = self.deck_images.build_image_from_deck(ydk.get_deck(), player_name, player_name)
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


        @self.bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_CLEANUP_CHALLONGE, description="Removes every player that is present in challonge but not locally")
        async def cleanup_challonge(interaction:Interaction):

            server_id = interaction.guild_id
            result = self.can_command_execute(interaction, True)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True)
            manager = TournamentManager(self.credentials, server_id)
            players = manager.get_tournament_players()
            challonge_players = manager.get_challonge_players()
            unsynced = []
            for challonge_player in challonge_players:
                unsynced.append(challonge_player)

            for challonge_player in challonge_players:
                for player in players:
                    if player.username == challonge_player:
                        unsynced.remove(challonge_player)

            for playername in unsynced:
                manager.drop(playername)
            
            if len(unsynced) > 0:
                message = "The following players have been removed from the tournament: \n\n"
                for player in unsynced:
                    last_message = message
                    message = message + player + "\n"
                    if len(message) > 2000:
                        await interaction.followup.send(last_message)
                        message = player + "\n"
                await interaction.followup.send(message)
            else:
                await interaction.followup.send("No players were unsynced")

            
        @create_tournament.autocomplete("tournament_type")
        async def tournament_type_autocomplete(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
            choices: List[app_commands.Choice[str]] = []
            choices.append(app_commands.Choice(
                name="Double Elimination", value="double elimination"))
            choices.append(app_commands.Choice(
                name="Single Elimination", value="single elimination"))
            choices.append(app_commands.Choice(
                name="Round Robin", value="round robin"))
            choices.append(app_commands.Choice(name="Swiss", value="swiss"))
            return choices

        @dq.autocomplete("player_name")
        @force_tournament_loss.autocomplete("player_name")
        async def player_autocomplete_for_tournament(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
            choices: List[app_commands.Choice[str]] = []
            manager = TournamentManager(self.credentials, interaction.guild_id)
            players = manager.get_tournament_players()
            for player in players:
                if current.lower() in player.username.lower():
                    if len(choices) < 25:
                        choice = app_commands.Choice(name=player.username, value=player.username)
                        choices.append(choice)

            return choices

        @get_db_name.autocomplete("player_name")
        async def player_autocomplete_for_db(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
            choices: List[app_commands.Choice[str]] = []
            manager = UserManager(interaction.guild_id)
            players = manager.get_partial_username_matches(current)
            for player in players:
                if len(choices) < 25:
                    choice = app_commands.Choice(name=player, value=player)
                    choices.append(choice)
            
            return choices

        @create_tournament.autocomplete("format_name")
        async def format_autocomplete(interaction: Interaction, current: str) -> List[app_commands.Choice[str]]:
            choices: List[app_commands.Choice[str]] = []
            formats = self.config.get_supported_formats(interaction.guild_id)
            for _format in formats:
                if current.lower() in _format.lower():
                    if len(choices) < 25:
                        choice = app_commands.Choice(name=_format, value=_format)
                        choices.append(choice)
            return choices