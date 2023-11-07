from typing import List

from discord import Interaction, app_commands

from src.commands.generic_command_manager import GenericCommandManager

from src.card.card_collection import CardCollection
from src.league.matchmaking import MatchmakingManager
from src.utils.utils import ReallyBigYugiohBot

import src.strings as Strings

class LeagueCommandManager(GenericCommandManager):
    
    def __init__(self, bot:ReallyBigYugiohBot, card_collection:CardCollection):
        super().__init__(bot, card_collection)
        self.add_commands()
        
        
    def add_commands(self):
        
        @self.bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_SET_DEFAULT_OUTPUT_CHANNEL, description="Sets this channel as the default output channel for League-related commands.")
        async def set_default_league_channel(interaction:Interaction):
            server_id = interaction.guild_id
            result = self.can_command_execute(interaction, True)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            
            channel_id = interaction.channel_id
            result = self.config.set_default_league_channel(channel_id, server_id)
            await interaction.response.send_message(result.get_message(), ephemeral=True)

        @self.bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_REGISTER, description="Register a player for a league.")
        async def register_for_league(interaction: Interaction):

            server_id = interaction.guild_id
            player_id = interaction.user.id
            player_name = interaction.user.name
            channel_name = self.get_channel_name(interaction.channel)
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            if forced_format is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
                return
            manager = MatchmakingManager(forced_format, server_id)
            result = manager.register_player(player_id, player_name)
            await interaction.followup.send(result.get_message())


        @self.bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_RATING, description="Checks your score in the leaderboard for the format tied to this channel.")
        async def check_rating(interaction: Interaction):

            server_id = interaction.guild_id
            player_id = interaction.user.id
            channel_name = self.get_channel_name(interaction.channel)
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            if forced_format is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
                return
            manager = MatchmakingManager(forced_format, server_id)
            result = manager.get_score_for_player(player_id)
            if result == -1:
                await interaction.followup.send(Strings.ERROR_MESSAGE_JOIN_LEAGUE_FIRST % forced_format)
            else:
                await interaction.followup.send(Strings.BOT_MESSAGE_YOUR_RATING_IS % (forced_format, result))


        @self.bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_ACTIVE_MATCHES, description="Returns the full list of active matches.")
        async def list_active_matches(interaction: Interaction):

            server_id = interaction.guild_id
            channel_name = self.get_channel_name(interaction.channel)
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            if forced_format is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
                return
            manager = MatchmakingManager(forced_format, server_id)
            result = manager.get_active_matches()
            if len(result) == 0:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_ACTIVE_MATCHES_IN_LEAGUE % forced_format)
            else:
                results = ""
                for active_match in result:
                    player_1 = manager.get_player_for_id(active_match.player1)
                    player_2 = manager.get_player_for_id(active_match.player2)
                    result_line = Strings.BOT_MESSAGE_ACTIVE_MATCH_FORMAT % (player_1.player_name, player_1.score, player_2.player_name, player_2.score)
                    results = f"{results}\n{result_line}"
                await interaction.followup.send(Strings.BOT_MESSAGE_ACTIVE_MATCH_LIST % (forced_format, results))


        @self.bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_GET_MATCH, description="Returns your active ranked match for this league if you have one.")
        async def get_active_match(interaction: Interaction):

            server_id = interaction.guild_id
            player_id = interaction.user.id
            channel_name = self.get_channel_name(interaction.channel)
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            if forced_format is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
                return
            manager = MatchmakingManager(forced_format, server_id)
            match = manager.get_match_for_player(player_id)
            if match is None:
                await interaction.followup.send(Strings.ERROR_MATCHMAKING_NO_ACTIVE_MATCHES)
            else:
                player1 = manager.get_player_for_id(match.player1)
                player2 = manager.get_player_for_id(match.player2)
                response = Strings.BOT_MESSAGE_ACTIVE_MATCH_FORMAT % (player1.player_name, player1.score, player2.player_name, player2.score)
                await interaction.followup.send(response)


        @self.bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_LEADERBOARD, description="Returns the leaderboard for this league.")
        async def print_leaderboard(interaction: Interaction):

            server_id = interaction.guild_id
            channel_name = self.get_channel_name(interaction.channel)
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            if forced_format is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
                return
            manager = MatchmakingManager(forced_format, server_id)
            leaderboard = manager.get_leaderboard()
            if len(leaderboard) == 0:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_PLAYERS_JOINED_LEAGUE % forced_format)
            else:
                lb = ""
                i = 1
                for player in leaderboard:
                    lb = f"{lb}\n{i} - {player.player_name}, {player.score}"
                    i += 1
                await interaction.followup.send(lb)


        @self.bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_JOIN, description="Joins the ranked queue. If another player joins it in 10 minutes, a ranked match starts.")
        async def join_queue(interaction: Interaction):

            server_id = interaction.guild_id
            player_id = interaction.user.id
            channel_name = self.get_channel_name(interaction.channel)
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            if forced_format is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
                return
            manager = MatchmakingManager(forced_format, server_id)
            result = manager.join_queue(player_id)
            if result.was_successful():
                await interaction.followup.send(result.get_message())
                active_match = manager.get_match_for_player(player_id)
                channel_id = interaction.channel_id
                channel_id = self.config.get_default_league_channel(channel_id, server_id)

                channel = self.bot.get_channel(channel_id)
                if active_match is not None:
                    # A match has started! Notify the channel so it"s public knowledge
                    await channel.send(result.get_message())
                else:
                    await channel.send(Strings.BOT_MESSAGE_SOMEONE_JOINED_THE_QUEUE % forced_format)
            else:
                await interaction.followup.send(result.get_message())


        @self.bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_CANCEL, description="Cancels an active match. Use only if your opponent is unresponsive.")
        async def cancel_match(interaction: Interaction):

            server_id = interaction.guild_id
            player_id = interaction.user.id
            channel_name = self.get_channel_name(interaction.channel)
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            if forced_format is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
                return
            manager = MatchmakingManager(forced_format, server_id)
            result = manager.cancel_match(player_id)
            if result.was_successful():
                await interaction.followup.send(result.get_message())
                # A match has been cancelled! Notify the channel so it"s public knowledge.
                await interaction.channel.send(result.get_message())
            else:
                await interaction.followup.send(result.get_message())
            

        @self.bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_LOST, description="Notifies you lost your ranked match.")
        async def notify_ranked_win(interaction: Interaction):

            server_id = interaction.guild_id
            player_id = interaction.user.id
            channel_name = self.get_channel_name(interaction.channel)
            result = self.can_command_execute(interaction, False)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            if forced_format is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
                return
            manager = MatchmakingManager(forced_format, server_id)
            match = manager.get_match_for_player(player_id)
            if match is None:
                await interaction.followup.send(Strings.ERROR_MATCHMAKING_NO_ACTIVE_MATCHES)
                return
            winner_id = 0
            if match.player1 == player_id:
                winner_id = match.player2
            else:
                winner_id = match.player1
            result = manager.end_match(winner_id)
            if result.was_successful():
                await interaction.followup.send(result.get_message())
                # A match has concluded. Notify the channel so it"s public knowledge.
                await interaction.channel.send(result.get_message())
            else:
                await interaction.followup.send(result.get_message())


        @self.bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_FORCE_LOSS, description="Declares a loser for a match. Admin only.")
        async def force_loss(interaction: Interaction, player_name: str):
            result = self.can_command_execute(interaction, True)
            if not result.was_successful():
                await interaction.response.send_message(result.get_message(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            server_id = interaction.guild_id
            channel_name = self.get_channel_name(interaction.channel)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            if forced_format is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
                return

            matchmaking_manager = MatchmakingManager(forced_format, server_id)
            player_id = matchmaking_manager.get_id_for_player_name(player_name)
            if player_id == -1:
                await interaction.followup.send(Strings.ERROR_MESSAGE_PLAYER_HASNT_JOINED_LEAGUE % player_name)
                return
            match = matchmaking_manager.get_match_for_player(player_id)
            if match is None:
                await interaction.followup.send(Strings.ERROR_MESSAGE_PLAYER_HAS_NO_MATCHES_PENDING % player_name)
                return
            winner_id = 0
            if match.player1 == player_id:
                winner_id = match.player2
            else:
                winner_id = match.player1
            result = matchmaking_manager.end_match(winner_id)
            if result.was_successful():
                await interaction.followup.send(result.get_message())
                # A match has concluded. Notify the channel so it"s public knowledge.
                await interaction.channel.send(result.get_message())

        @force_loss.autocomplete("player_name")
        async def player_autocomplete_for_loss(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
            choices: List[app_commands.Choice[str]] = []
            server_id = interaction.guild_id
            channel_name = self.get_channel_name(interaction.channel)
            forced_format = self.config.get_forced_format(channel_name, server_id)
            manager = MatchmakingManager(forced_format, server_id)
            players = manager.get_players()
            for player in players:
                if current.lower() in player.player_name.lower():
                    choice = app_commands.Choice(
                        name=player.player_name, value=player.player_name)
                    choices.append(choice)

            return choices