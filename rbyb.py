# Pycache stuff

import sys

sys.dont_write_bytecode = True

# Imports

import os
import asyncio

from typing import List

import discord

from discord import app_commands
from discord import File
from discord import Embed

from src.deck_validation import DeckValidator
from src.banlist_validation import BanlistValidator
from src.card_collection import CardCollection
from src.utils import ReallyBigYugiohBot, OperationResult, get_channel_name
from src.views import PaginationView
from src.config.config import Config
from src.config.server_config import ServerConfig
from src.credentials_manager import CredentialsManager
from src.league.matchmaking import MatchmakingManager
from src.deck_collection import DeckCollectionManager
from src.deck_validation import Ydk, Deck
from src.deck_images import DeckAsImageGenerator
from src.tournaments import TournamentManager
from src.user_manager import UserManager
from src.cloudinary import Uploader
from src.command_manager import CommandManager
import src.strings as Strings

# Configuration

REGULAR_HELP_FILE = "docs/regular_help.txt"
ADMIN_HELP_FILE = "docs/admin_help.txt"

cardCollection = CardCollection()

config = Config(cardCollection)
deckValidator = DeckValidator(cardCollection)
deckImages = DeckAsImageGenerator(cardCollection)

credentials = CredentialsManager()
serverConfig = ServerConfig()
uploader = Uploader(credentials.getCloudinaryCloudName(), credentials.getCloudinaryApiKey(), credentials.getCloudinaryApiSecret())

banlistValidator = BanlistValidator()

intents = discord.Intents.default()
intents.message_content = True
bot = ReallyBigYugiohBot(intents=intents)

decay: bool = False

commandManager = CommandManager(bot, cardCollection, banlistValidator)


def start_bot():
	bot.run(credentials.getDiscordAPIKey())


def banlist_to_discord_file(banlist_file: str, format_name: str):
	file_name = f"{format_name}.lflist.conf"
	return File(filename=file_name, fp=banlist_file)


def ydk_to_discord_file(ydk_file: str, player_name: str):
	file_name = f"{player_name}.ydk"
	return File(filename=file_name, fp=ydk_file)


def validate_ydk(format_name, ydk_file: str, server_id: int):
	banlist_file = config.get_banlist_for_format(format_name, server_id)
	if config.is_format_supported(format_name, server_id):
		result = deckValidator.validate_deck(ydk_file, banlist_file)
		if result.was_successful():
			return Strings.BOT_MESSAGE_DECK_VALID % format_name
		return Strings.ERROR_MESSAGE_DECK_INVALID % (format_name, result.get_message())
	return Strings.ERROR_MESSAGE_FORMAT_UNSUPPORTED % format_name

def get_readable_list(readable_decklist:Deck) -> str:
	readable = "Main deck:\n\n"
	for card in readable_decklist.main:
		card_name = cardCollection.getCardNameFromId(card.card_id)
		readable = f"{readable}{card.copies}x {card_name}\n"
	readable = f"{readable}\nExtra Deck:\n\n"
	for card in readable_decklist.extra:
		card_name = cardCollection.getCardNameFromId(card.card_id)
		readable = f"{readable}{card.copies}x {card_name}\n"
	readable = f"{readable}\nSide Deck:\n\n"
	for card in readable_decklist.side:
		card_name = cardCollection.getCardNameFromId(card.card_id)
		readable = f"{readable}{card.copies}x {card_name}\n"
	return readable

# Callbacks


class FormatForBanlistCallback:

	def __init__(self, server_id):
		self.server_id = server_id

	def set_message(self, message: discord.WebhookMessage):
		self.message = message

	async def execute_callback(self, format_name, attachment):
		ydk_file = await attachment.read()
		ydk_file = ydk_file.decode("utf-8")
		validation = validate_ydk(format_name, ydk_file, self.server_id)
		await self.message.edit(content=validation, view=None)


class FormatToDownloadBanlistCallback:

	def __init__(self, server_id):
		self.server_id = server_id

	def set_message(self, message: discord.WebhookMessage):
		self.message = message

	async def execute_callback(self, format_name, attachment):
		banlist_files = config.get_banlist_for_format(format_name, self.server_id)
		await self.message.edit(content=None, embed=None, view=None, attachments=[banlist_to_discord_file(banlist_files, format_name)])

# Events and commands


@bot.event
async def on_ready():
	print('Bot is ready')
	bot.loop.create_task(decay_scores())


async def decay_scores():
	global decay
	if decay:
		servers: List[int] = serverConfig.getEnabledServers()
		for server_id in servers:
			# Get list of formats for that server
			formats = config.get_supported_formats(server_id)
			for _format in formats:
				matchmaking = MatchmakingManager(_format, server_id)
				matchmaking.decay()
	else:
		decay = True
			
	await asyncio.sleep(86400)


def can_command_execute(interaction: discord.Interaction, admin_only):
	server_id = interaction.guild_id
	result = serverConfig.check_server_enabled(server_id)
	if not result.was_successful():
		return result

	role = discord.utils.get(interaction.guild.roles, name="Tournament Staff")
	is_staff = role in interaction.user.roles

	channel_name = get_channel_name(interaction.channel)
	enabled = config.is_channel_enabled(channel_name, server_id)

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


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_SET_DEFAULT_OUTPUT_CHANNEL, description="Sets this channel as the default output channel for League-related commands.")
async def set_default_league_channel(interaction:discord.Interaction):
	server_id = interaction.guild_id
	result = can_command_execute(interaction, True)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	
	channel_id = interaction.channel_id
	result = config.set_default_league_channel(channel_id, server_id)
	await interaction.response.send_message(result.get_message(), ephemeral=True)


@bot.tree.command(name=Strings.COMMAND_NAME_DECK_VALIDATE, description="Validates a deck")
async def validate_deck(interaction: discord.Interaction, ydk: discord.Attachment):

	server_id = interaction.guild_id
	result = can_command_execute(interaction, False)
	if result.was_successful():
		supported_formats = config.get_supported_formats(server_id)
		if len(supported_formats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		if ydk.filename.endswith(".ydk"):
			channel_name = get_channel_name(interaction.channel)
			forced_format = config.get_forced_format(channel_name, server_id)
			if forced_format is None:
				supported_formats = config.get_supported_formats(server_id)
				if len(supported_formats) > 0:
					pagination = PaginationView(
						Strings.BOT_MESSAGE_CHOOSE_A_FORMAT)
					callback = FormatForBanlistCallback(server_id)
					pagination.setup(config.get_supported_formats(
						server_id), interaction, callback, ydk)
					message = await interaction.followup.send(Strings.BOT_MESSAGE_CHOOSE_FORMAT_TO_VALIDATE_DECK, view=pagination, wait=True)
					callback.set_message(message)
				else:
					await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			else:
				ydk_as_string = await ydk.read()
				ydk_as_string = ydk_as_string.decode("utf-8")
				validation = validate_ydk(forced_format, ydk_as_string, server_id)
				await interaction.followup.send(validation)
		else:
			await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_DECK_FORMAT)
	else:
		await interaction.response.send_message(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_BANLIST, description="Get an EDOPRO banlist")
async def get_banlist(interaction: discord.Interaction):

	server_id = interaction.guild_id
	result = can_command_execute(interaction, False)
	if result.was_successful():
		await interaction.response.defer(ephemeral=True)
		channel_name = get_channel_name(interaction.channel)
		forced_format = config.get_forced_format(channel_name, server_id)
		banlist_file = config.get_banlist_for_format(forced_format, server_id)
		if forced_format is None:
			supported_formats = config.get_supported_formats(server_id)
			if len(supported_formats) > 0:
				pagination = PaginationView(
					Strings.BOT_MESSAGE_CHOOSE_A_FORMAT)
				callback = FormatToDownloadBanlistCallback(server_id)
				pagination.setup(supported_formats, interaction, callback, None)
				message = await interaction.followup.send(Strings.BOT_MESSAGE_CHOOSE_A_FORMAT_TO_DOWNLOAD_BANLIST, view=pagination, wait=True, ephemeral=True)
				callback.set_message(message)
			else:
				await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
		else:
			await interaction.followup.send(file=banlist_to_discord_file(banlist_file, forced_format))
	else:
		await interaction.response.send_message(result.get_message(), ephemeral=True)


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_REGISTER, description="Register a player for a league.")
async def register_for_league(interaction: discord.Interaction):

	server_id = interaction.guild_id
	player_id = interaction.user.id
	player_name = f"{interaction.user.name}"
	channel_name = get_channel_name(interaction.channel)
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forced_format = config.get_forced_format(channel_name, server_id)
	if forced_format is None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return
	manager = MatchmakingManager(forced_format, server_id)
	result = manager.register_player(player_id, player_name)
	await interaction.followup.send(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_RATING, description="Checks your score in the leaderboard for the format tied to this channel.")
async def check_rating(interaction: discord.Interaction):

	server_id = interaction.guild_id
	player_id = interaction.user.id
	channel_name = get_channel_name(interaction.channel)
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forced_format = config.get_forced_format(channel_name, server_id)
	if forced_format is None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return
	manager = MatchmakingManager(forced_format, server_id)
	result = manager.get_score_for_player(player_id)
	if result == -1:
		await interaction.followup.send(Strings.ERROR_MESSAGE_JOIN_LEAGUE_FIRST % forced_format)
	else:
		await interaction.followup.send(Strings.BOT_MESSAGE_YOUR_RATING_IS % (forced_format, result))


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_ACTIVE_MATCHES, description="Returns the full list of active matches.")
async def list_active_matches(interaction: discord.Interaction):

	server_id = interaction.guild_id
	channel_name = get_channel_name(interaction.channel)
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forced_format = config.get_forced_format(channel_name, server_id)
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


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_GET_MATCH, description="Returns your active ranked match for this league if you have one.")
async def get_active_match(interaction: discord.Interaction):

	server_id = interaction.guild_id
	player_id = interaction.user.id
	channel_name = get_channel_name(interaction.channel)
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forced_format = config.get_forced_format(channel_name, server_id)
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
		response = Strings.BOT_MESSAGE_ACTIVE_MATCH_FORMAT % (player1.getPlayerName(
		), player1.score, player2.player_name, player2.score)
		await interaction.followup.send(response)


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_LEADERBOARD, description="Returns the leaderboard for this league.")
async def print_leaderboard(interaction: discord.Interaction):

	server_id = interaction.guild_id
	channel_name = get_channel_name(interaction.channel)
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forced_format = config.get_forced_format(channel_name, server_id)
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


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_JOIN, description="Joins the ranked queue. If another player joins it in 10 minutes, a ranked match starts.")
async def join_queue(interaction: discord.Interaction):

	server_id = interaction.guild_id
	player_id = interaction.user.id
	channel_name = get_channel_name(interaction.channel)
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forced_format = config.get_forced_format(channel_name, server_id)
	if forced_format is None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return
	manager = MatchmakingManager(forced_format, server_id)
	result = manager.join_queue(player_id)
	if result.was_successful():
		await interaction.followup.send(result.get_message())
		active_match = manager.get_match_for_player(player_id)
		channel_id = interaction.channel_id
		channel_id = config.get_default_league_channel(channel_id, server_id)

		channel = bot.get_channel(channel_id)
		if active_match is not None:
			# A match has started! Notify the channel so it"s public knowledge
			await channel.send(result.get_message())
		else:
			await channel.send(Strings.BOT_MESSAGE_SOMEONE_JOINED_THE_QUEUE % forced_format)
	else:
		await interaction.followup.send(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_CANCEL, description="Cancels an active match. Use only if your opponent is unresponsive.")
async def cancel_match(interaction: discord.Interaction):

	server_id = interaction.guild_id
	player_id = interaction.user.id
	channel_name = get_channel_name(interaction.channel)
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forced_format = config.get_forced_format(channel_name, server_id)
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
	

@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_LOST, description="Notifies you lost your ranked match.")
async def notify_ranked_win(interaction: discord.Interaction):

	server_id = interaction.guild_id
	player_id = interaction.user.id
	channel_name = get_channel_name(interaction.channel)
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forced_format = config.get_forced_format(channel_name, server_id)
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


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_TXT_DECK, description="Gets a decklist in readable form")
async def get_readable_decklist(interaction: discord.Interaction, player_name: str):
	server_id = interaction.guild_id
	result = can_command_execute(interaction, True)
	if result.was_successful():
		supported_formats = config.get_supported_formats(server_id)
		if len(supported_formats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		channel_name = get_channel_name(interaction.channel)
		forced_format = config.get_forced_format(channel_name, server_id)
		deck_collection_manager = DeckCollectionManager(forced_format, server_id)
		players = deck_collection_manager.getRegisteredPlayers()
		found = False
		for player in players:
			if player_name.lower() in player.lower():
				found = True
				player_name = player
				break
		if not found:
			await interaction.followup.send(Strings.ERROR_MESSAGE_NO_SUBMITTED_DECKLIST % player_name)
			return
		readable_decklist = deck_collection_manager.getReadableDecklistForPlayer(player_name)
		readable = get_readable_list(readable_decklist)
		await interaction.followup.send(readable)
	else:
		await interaction.response.send_message(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_CLEANUP_CHALLONGE, description="Removes every player that is present in challonge but not locally")
async def cleanup_challonge(interaction:discord.Interaction):

	server_id = interaction.guild_id
	result = can_command_execute(interaction, True)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return

	await interaction.response.defer(ephemeral=True)
	manager = TournamentManager(credentials, server_id)
	players = manager.getTournamentPlayers()
	challonge_players = manager.getChallongePlayers()
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


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_YDK_DECK, description="Gets a decklist as a YDK file")
async def get_ydk_decklist(interaction: discord.Interaction, player_name: str):
	server_id = interaction.guild_id
	player_name = f"{interaction.user.name}"
	result = can_command_execute(interaction, True)
	if result.was_successful():
		supported_formats = config.get_supported_formats(server_id)
		if len(supported_formats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		channel_name = get_channel_name(interaction.channel)
		forced_format = config.get_forced_format(channel_name, server_id)
		deck_collection_manager = DeckCollectionManager(forced_format, server_id)
		players = deck_collection_manager.getRegisteredPlayers()
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
		file = ydk_to_discord_file(filename, player_name)
		await interaction.followup.send(file=file)
	else:
		await interaction.response.send_message(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_IMG_DECK, description="Gets a decklist as an image")
async def get_img_deck(interaction: discord.Interaction, player_name: str):
	server_id = interaction.guild_id
	result = can_command_execute(interaction, True)
	if result.was_successful():
		supported_formats = config.get_supported_formats(server_id)
		if len(supported_formats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		channel_name = get_channel_name(interaction.channel)
		forced_format = config.get_forced_format(channel_name, server_id)
		deck_collection_manager = DeckCollectionManager(forced_format, server_id)
		players = deck_collection_manager.getRegisteredPlayers()
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

			image = deckImages.buildImageFromDeck(ydk.get_deck(), player_name, player_name)
			image_url = uploader.upload_image(image)

			embed = Embed(title=player_name)
			embed.set_image(url="attachment://deck.jpg")
			embed.add_field(name="", value=f"[See high resolution decklist]({image_url})")

			with open(image, "rb") as fp:
				image_file = File(fp, filename="deck.jpg")
		
			await interaction.followup.send(embed=embed, file=image_file)

			os.remove(image)
	else:
		await interaction.response.send_message(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_GET_ALL_LISTS, description="Returns a .zip file with all registered decks")
async def download_zip(interaction: discord.Interaction):
	server_id = interaction.guild_id
	result = can_command_execute(interaction, True)
	if result.was_successful():
		supported_formats = config.get_supported_formats(server_id)
		if len(supported_formats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		channel_name = get_channel_name(interaction.channel)
		forced_format = config.get_forced_format(channel_name, server_id)
		deck_collection_manager = DeckCollectionManager(forced_format, server_id)
		decks = deck_collection_manager.zipAllDecks()

		await interaction.followup.send(file=File(filename="decks.zip", fp=decks))
		os.remove(decks)
	else:
		await interaction.response.send_message(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_CONFIRM_DECK, description="Shows the deck you have currently registered")
async def confirm_deck(interaction: discord.Interaction):
	server_id = interaction.guild_id
	result = can_command_execute(interaction, False)
	if result.was_successful():
		supported_formats = config.get_supported_formats(server_id)
		if len(supported_formats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		player_name = f"{interaction.user.name}"
		channel_name = get_channel_name(interaction.channel)
		forced_format = config.get_forced_format(channel_name, server_id)
		deck_collection_manager = DeckCollectionManager(forced_format, server_id)
		players = deck_collection_manager.getRegisteredPlayers()
		found = False
		for player in players:
			if player_name.lower() in player.lower():
				found = True
				player_name = player
				break
		if not found:
			await interaction.followup.send("You haven't submitted a decklist. Do so by using /t_join_db or /t_join_ydk. If you have already joined, please ping Diamond Dude for troubleshooting.")
			return
		filename = deck_collection_manager.get_decklist_for_player(player_name)
		with open(filename, encoding="utf-8") as deck_file:
			deck = deck_file.read()
			ydk = Ydk(deck)

			image = deckImages.buildImageFromDeck(ydk.get_deck(), player_name, player_name)
			image_url = uploader.upload_image(image)

			embed = Embed(title=player_name)
			embed.set_image(url="attachment://deck.jpg")
			embed.add_field(name="", value=f"[See high resolution decklist]({image_url})")

			with open(image, "rb") as fp:
				image_file = File(fp, filename="deck.jpg")
		
			await interaction.followup.send(embed=embed, file=image_file)

			os.remove(image)
	else:
		await interaction.response.send_message(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_HELP, description="Displays every command and its use")
async def display_help(interaction: discord.Interaction):
	result = can_command_execute(interaction, False)
	if result.was_successful():
		result = can_command_execute(interaction, True)
		if result.was_successful():
			filename = ADMIN_HELP_FILE
		else:
			filename = REGULAR_HELP_FILE
		with open(filename, encoding="utf-8") as file:
			readable_help = file.read()
			await interaction.response.send_message(readable_help, ephemeral=True)
	else:
		await interaction.response.send_message(result.get_message(), ephemeral=True)


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_FORCE_LOSS, description="Declares a loser for a match. Admin only.")
async def force_loss(interaction: discord.Interaction, player_name: str):
	result = can_command_execute(interaction, True)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	server_id = interaction.guild_id
	channel_name = get_channel_name(interaction.channel)
	forced_format = config.get_forced_format(channel_name, server_id)
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

# Tournament commands


def get_tournament_manager(interaction: discord.Interaction):
	server_id = interaction.guild_id
	return TournamentManager(credentials, server_id)


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_CREATE, description="Creates a new tournament. This deletes any previous tournaments and decklists!")
async def create_tournament(interaction: discord.Interaction, tournament_name: str, format_name: str, tournament_type: str):

	server_id = interaction.guild_id

	result = can_command_execute(interaction, True)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return

	supported_formats = config.get_supported_formats(server_id)

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

	deck_collection_manager.beginCollection()
	
	manager = get_tournament_manager(interaction)
	result = manager.createTournament(
		tournament_name, format_name, tournament_type)
	await interaction.followup.send(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_START, description="Starts the tournament.")
async def start_tournament(interaction: discord.Interaction):
	server_id = interaction.guild_id
	result = can_command_execute(interaction, True)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=False)

	manager = get_tournament_manager(interaction)
	format_name = manager.getTournamentFormat()
	DeckCollectionManager(format_name, server_id).endCollection()

	await interaction.followup.send(manager.startTournament().get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_END, description="Ends the tournament.")
async def end_tournament(interaction: discord.Interaction):
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)

	manager = get_tournament_manager(interaction)

	await interaction.followup.send(manager.endTournament().get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_INFO, description="Gets the tournament url")
async def tournament_info(interaction: discord.Interaction):
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=False)

	manager = get_tournament_manager(interaction)

	await interaction.followup.send(manager.getTournamentInfo().get_message())


def register_list(interaction: discord.Interaction, _format: str, decklist:str):
	server_id = interaction.guild_id
	player_name = f"{interaction.user.name}"
	player_id = interaction.user.id
	banlist_file = config.get_banlist_for_format(_format, server_id)
	path = None
	if config.is_format_supported(_format, server_id):
		result = deckValidator.validate_deck(decklist, banlist_file)
		if result.was_successful():
			deck_collection_manager = DeckCollectionManager(_format, server_id)
			result = deck_collection_manager.addDeck(player_name, decklist)
			if result.was_successful():
				path = deck_collection_manager.get_decklist_for_player(player_name)
		else:
			print(f"{player_name}'s deck did not validate")
			print(f"Reason: {result.get_message()}")
			return result

	# At this point, decklist is updated.

	if path is not None:
		return get_tournament_manager(interaction).registerToTournament(player_name, player_id, path)
	
	print(f"{player_name}'s decklist path is None.")
	return OperationResult(False, "Something went wrong while registering your list. Please contact Diamond Dude or try again.")
		

@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_JOIN_YDK, description="Registers to an open tournament using a .ydk, or updates your deck if already registered")
async def register_ydk(interaction: discord.Interaction, ydk: discord.Attachment):
	result = can_command_execute(interaction, False)
	server_id = interaction.guild_id
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)

	manager = get_tournament_manager(interaction)
	forced_format = manager.getTournamentFormat()
	if forced_format is None:
		await interaction.followup.send("There is no ongoing tournament in this server")
		return

	if ydk.filename.endswith(".ydk"):
		channel_name = get_channel_name(interaction.channel)
		forced_format = config.get_forced_format(channel_name, server_id)
		if config.is_format_supported(forced_format, server_id):
			ydk_file = await ydk.read()
			ydk_file = ydk_file.decode("utf-8")
			await interaction.followup.send(register_list(interaction, forced_format, ydk_file).get_message())
	else:
		await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_DECK_FORMAT)


@bot.tree.command(name=Strings.COMMAND_NAME_SET_DB_NAME, description="Sets your Duelingbook name for a tournament")
async def set_db_name(interaction:discord.Interaction, db_name:str):
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message())
		return

	await interaction.response.defer(ephemeral=True)
	if len(db_name) == 0:
		await interaction.followup.send("Username can't be empty")
		return
	
	manager = UserManager(interaction.guild_id)
	player_name = f"{interaction.user.name}"
	manager.setDBUsername(player_name, db_name)
	await interaction.followup.send(f"Duelingbook username set successfully to {db_name}")


@bot.tree.command(name=Strings.COMMAND_NAME_GET_DB_NAME, description="Gets the Duelinbgook username for an user.")
async def get_db_name(interaction:discord.Interaction, player_name:str):
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message())
		return
	
	await interaction.response.defer(ephemeral=True)
	manager = UserManager(interaction.guild_id)
	db_name = manager.getDBUsername(player_name)
	if db_name is None:
		await interaction.followup.send(f"{player_name} does not have a Duelingbook username set")
		return
	await interaction.followup.send(db_name)


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_REPORT_LOSS, description="Reports you lost a tournament match")
async def report_tournament_loss(interaction: discord.Interaction):
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=False)
	server_id = interaction.guild_id
	player_name = f"{interaction.user.name}"

	manager = TournamentManager(credentials, server_id)

	channel_name = get_channel_name(interaction.channel)
	forced_format = config.get_forced_format(channel_name, server_id)

	matchmaking_manager = MatchmakingManager(forced_format, server_id)

	t_winner = manager.getWinnerFromLoser(player_name)

	if t_winner is not None:
		winner = matchmaking_manager.get_player_for_id(t_winner.discordId)
		loser = matchmaking_manager.get_player_for_id(interaction.user.id)
		if winner is None:
			matchmaking_manager.register_player(t_winner.discordId, t_winner.username)
		if loser is None:
			matchmaking_manager.register_player(interaction.user.id, player_name)
		matchmaking_manager.create_match(t_winner.discordId, interaction.user.id, True)
		matchmaking_manager.end_match(t_winner.discordId)

	result = manager.reportLoss(player_name)
	await interaction.followup.send(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_FORCE_LOSS, description="Forces a player to lose a match")
async def force_tournament_loss(interaction: discord.Interaction, player_name: str):
	result = can_command_execute(interaction, True)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=False)
	server_id = interaction.guild_id
	manager = TournamentManager(credentials, server_id)
	channel_name = get_channel_name(interaction.channel)
	forced_format = config.get_forced_format(channel_name, server_id)
	matchmaking_manager = MatchmakingManager(forced_format, server_id)
	t_winner = manager.getWinnerFromLoser(player_name)
	if t_winner is not None:
		winner = matchmaking_manager.get_player_for_id(t_winner.discordId)
		loser = matchmaking_manager.get_player_for_id(interaction.user.id)
		if winner is None:
			matchmaking_manager.register_player(t_winner.discordId, t_winner.username)
		if loser is None:
			matchmaking_manager.register_player(interaction.user.id, player_name)
		matchmaking_manager.create_match(t_winner.discordId, interaction.user.id, True)
		matchmaking_manager.end_match(t_winner.discordId)
	result = manager.reportLoss(player_name)
	await interaction.followup.send(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_DROP, description="Drop from the tournament")
async def drop(interaction: discord.Interaction):
	drop_enabled = False
	if not drop_enabled and interaction.guild_id == 459826576536764426:
		await interaction.response.send_message("Manual dropping is currently disabled. Please ask Tournament Staff to drop you.")
		return
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	server_id = interaction.guild_id
	player_name = f"{interaction.user.name}"
	manager = TournamentManager(credentials, server_id)
	result = manager.drop(player_name)
	await interaction.followup.send(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_DQ, description="Removes a player from the tournament")
async def dq(interaction: discord.Interaction, player_name: str):
	result = can_command_execute(interaction, True)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=False)
	server_id = interaction.guild_id
	manager = TournamentManager(credentials, server_id)
	result = manager.drop(player_name)
	await interaction.followup.send(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_PRINT_ACTIVE_MATCHES, description="Gets a list of unfinished matches")
async def active_matches(interaction: discord.Interaction):
	result = can_command_execute(interaction, False)
	if not result.was_successful():
		await interaction.response.send_message(result.get_message(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=False)
	server_id = interaction.guild_id
	manager = TournamentManager(credentials, server_id)
	result = manager.getReadableActiveMatches()
	await interaction.followup.send(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_SHARE_DECK_YDK_TXT, description="Shares a deck as text")
async def share_ydk_txt(interaction:discord.Interaction, ydk: discord.Attachment):
	server_id = interaction.guild_id
	result = can_command_execute(interaction, False)
	if result.was_successful():
		supported_formats = config.get_supported_formats(server_id)
		if len(supported_formats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=False)
		if ydk.filename.endswith(".ydk"):
			ydk_as_string = await ydk.read()
			ydk_as_string = ydk_as_string.decode("utf-8")
			readable_decklist = Ydk(ydk_as_string).get_deck()
			readable = get_readable_list(readable_decklist)
			await interaction.followup.send(readable)
		else:
			await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_DECK_FORMAT)
	else:
		await interaction.response.send_message(result.get_message())


@bot.tree.command(name=Strings.COMMAND_NAME_SHARE_DECK_YDK, description="Shares an image of a YDK deck")
async def share_ydk(interaction: discord.Interaction, ydk: discord.Attachment):
	server_id = interaction.guild_id
	result = can_command_execute(interaction, False)
	if result.was_successful():
		supported_formats = config.get_supported_formats(server_id)
		if len(supported_formats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=False)
		if ydk.filename.endswith(".ydk"):
			ydk_as_string = await ydk.read()
			ydk_as_string = ydk_as_string.decode("utf-8")
			ydk_native = Ydk(ydk_as_string)
			filename = ydk.filename.replace("_", " ")[:-4]
			image = deckImages.buildImageFromDeck(ydk_native.get_deck(), "temp", filename)
			with open("img/decks/temp.ydk", 'w', encoding="utf-8") as file:
				deck_as_lines = ydk_as_string.split("\n")
				for line in deck_as_lines:
					line = line.replace("\n", "").replace("\r", "")
					if len(line) > 0:
						file.write(line)
						file.write("\n")

			image_url = uploader.upload_image(image)
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

# Autocomplete functions


@force_loss.autocomplete("player_name")
async def player_autocomplete_for_loss(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	choices: List[app_commands.Choice[str]] = []
	server_id = interaction.guild_id
	channel_name = get_channel_name(interaction.channel)
	forced_format = config.get_forced_format(channel_name, server_id)
	manager = MatchmakingManager(forced_format, server_id)
	players = manager.get_players()
	for player in players:
		if current.lower() in player.player_name.lower():
			choice = app_commands.Choice(
				name=player.player_name, value=player.player_name)
			choices.append(choice)

	return choices


@create_tournament.autocomplete("tournament_type")
async def tournament_type_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
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
async def player_autocomplete_for_tournament(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	choices: List[app_commands.Choice[str]] = []
	manager = TournamentManager(credentials, interaction.guild_id)
	players = manager.getTournamentPlayers()
	for player in players:
		if current.lower() in player.username.lower():
			if len(choices) < 25:
				choice = app_commands.Choice(name=player.username, value=player.username)
				choices.append(choice)

	return choices


@get_db_name.autocomplete("player_name")
async def player_autocomplete_for_db(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	choices: List[app_commands.Choice[str]] = []
	manager = UserManager(interaction.guild_id)
	players = manager.getPartialUsernameMatches(current)
	for player in players:
		if len(choices) < 25:
			choice = app_commands.Choice(name=player, value=player)
			choices.append(choice)
	
	return choices


@get_img_deck.autocomplete("player_name")
@get_ydk_decklist.autocomplete("player_name")
@get_readable_decklist.autocomplete("player_name")
async def player_autocomplete_for_decklist(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	choices: List[app_commands.Choice[str]] = []
	server_id = interaction.guild_id
	channel_name = get_channel_name(interaction.channel)
	forced_format = config.get_forced_format(channel_name, server_id)
	deck_collection_manager = DeckCollectionManager(forced_format, server_id)
	registered_players = deck_collection_manager.getRegisteredPlayers()
	for player in registered_players:
		if current.lower() in player.lower():
			if len(choices) < 25:
				choice = app_commands.Choice(name=player, value=player)
				choices.append(choice)
	return choices


@create_tournament.autocomplete("format_name")
async def format_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
	choices: List[app_commands.Choice[str]] = []
	formats = config.get_supported_formats(interaction.guild_id)
	for _format in formats:
		if current.lower() in _format.lower():
			if len(choices) < 25:
				choice = app_commands.Choice(name=_format, value=_format)
				choices.append(choice)
	return choices


start_bot()
