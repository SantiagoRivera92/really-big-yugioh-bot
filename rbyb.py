# Pycache stuff

import sys

sys.dont_write_bytecode = True

# Imports

import discord
import os

from typing import List

from discord import app_commands
from discord import File
from discord import Embed

from src.deck_validation import DeckValidator
from src.banlist_validation import BanlistValidator
from src.banlist_generation import BanlistGenerator
from src.card_embeds import cardToEmbed
from src.card_collection import CardCollection
from src.utils import MyClient, OperationResult, getChannelName
from src.views import PaginationView
from src.config import Config
from src.server_config import ServerConfig
from src.credentials_manager import CredentialsManager
from src.matchmaking import MatchmakingManager
from src.deck_collection import DeckCollectionManager
from src.deck_validation import Ydk
from src.deck_images import DeckAsImageGenerator
from src.tournaments import TournamentManager
from src.duelingbook_deck_download import DuelingbookManager
from src.usermanager import UserManager
from src.file_uploader import FileUploader
from src.cloudinary import Uploader
import src.strings as Strings


# Configuration

CREDENTIALS_FILE = "json/credentials.json"
ENABLED_SERVERS = "json/enabledServers.json"
REGULAR_HELP_FILE = "docs/regular_help.txt"
ADMIN_HELP_FILE = "docs/admin_help.txt"

cardCollection = CardCollection()

config = Config(cardCollection)
deckValidator = DeckValidator(cardCollection)
deckImages = DeckAsImageGenerator(cardCollection)

credentials = CredentialsManager(CREDENTIALS_FILE)
serverConfig = ServerConfig(ENABLED_SERVERS)
uploader = Uploader(credentials.getCloudinaryCloudName(), credentials.getCloudinaryApiKey(), credentials.getCloudinaryApiSecret())

banlistValidator = BanlistValidator()

intents = discord.Intents.default()
intents.message_content = True
bot = MyClient(intents=intents)


def startBot():
	bot.run(credentials.getDiscordAPIKey())


def isValidFilename(filename: str):
	if len(filename) == 0:
		return OperationResult(False, Strings.ERROR_FORMAT_NAME_EMPTY)
	invalidCharacters = "#%&\{\}\\<>*?/$!\'\":@+`|="
	for char in invalidCharacters:
		if char in filename:
			return OperationResult(False, Strings.ERROR_FORMAT_NAME_INVALID_CHARACTER % char)
	if filename == "Advanced":
		return OperationResult(False, Strings.ERROR_FORMAT_NAME_ADVANCED)
	return OperationResult(True, "")


def decodeFile(bytes: bytes):
	return bytes.decode("utf-8", "ignore")


def banlistToDiscordFile(banlistFile: str, formatName: str):
	fileName = "%s.lflist.conf" % formatName
	return File(filename=fileName, fp=banlistFile)


def ydkToDiscordFile(ydkFile: str, playerName: str):
	fileName = "%s.ydk" % playerName
	return File(filename=fileName, fp=ydkFile)


def validateYDK(formatName, ydkFile: str, serverId: int):

	banlistFile = config.getBanlistForFormat(formatName, serverId)

	if config.isFormatSupported(formatName, serverId):
		result = deckValidator.validateDeck(ydkFile, banlistFile)
		if result.wasSuccessful():
			return Strings.BOT_MESSAGE_DECK_VALID % formatName
		else:
			return Strings.ERROR_MESSAGE_DECK_INVALID % (formatName, result.getMessage())
	else:
		return Strings.ERROR_MESSAGE_FORMAT_UNSUPPORTED % formatName


# Callbacks

class FormatForBanlistCallback:

	def __init__(self, serverId):
		self.serverId = serverId

	def setMessage(self, message: discord.WebhookMessage):
		self.message = message

	async def executeCallback(self, formatName, attachment):
		ydkFile = await attachment.read()
		ydkFile = ydkFile.decode("utf-8")
		validation = validateYDK(formatName, ydkFile, self.serverId)
		await self.message.edit(content=validation, view=None)


class FormatForCardLegalityCallback:

	def __init__(self, serverId):
		self.serverId = serverId

	def setMessage(self, message: discord.WebhookMessage):
		self.message = message

	async def executeCallback(self, formatName, card):
		banlistFile = config.getBanlistForFormat(formatName, self.serverId)
		embed = cardToEmbed(card, banlistFile, formatName, bot)

		await self.message.edit(embed=embed, view=None)


class FormatToDownloadBanlistCallback:

	def __init__(self, serverId):
		self.serverId = serverId

	def setMessage(self, message: discord.WebhookMessage):
		self.message = message

	async def executeCallback(self, formatName, attachment):
		banlistFiles = config.getBanlistForFormat(formatName, self.serverId)
		await self.message.edit(content=None, embed=None, view=None, attachments=[banlistToDiscordFile(banlistFiles, formatName)])


class PartialCardnameCallback:

	def __init__(self, serverId):
		self.serverId = serverId

	def setMessage(self, message: discord.WebhookMessage):
		self.message = message

	async def executeCallback(self, cardName, formatName):
		card = cardCollection.getCardFromCardName(cardName)
		banlistfile = config.getBanlistForFormat(formatName, self.serverId)
		embed = cardToEmbed(card, banlistfile, formatName, bot)
		await self.message.edit(content="", embed=embed, view=None)


class FormatForPartialCardnameCallback:

	def __init__(self, serverId, interaction: discord.Interaction):
		self.serverId = serverId
		self.interaction = interaction

	def setMessage(self, message: discord.WebhookMessage):
		self.message = message

	async def executeCallback(self, formatName, cards):
		callback = PartialCardnameCallback(self.serverId)
		pagination = PaginationView(Strings.BOT_MESSAGE_CHOOSE_A_CARD)
		pagination.setup(cards, self.interaction, callback, formatName)
		await self.message.delete()
		message = await self.interaction.followup.send(content=Strings.BOT_MESSAGE_MULTIPLE_RESULTS_AVAILABLE, view=pagination)
		callback.setMessage(message)

# Events and commands


@bot.event
async def on_ready():
	pass


def canCommandExecute(interaction: discord.Interaction, adminOnly):
	serverId = interaction.guild_id
	result = serverConfig.checkServerEnabled(serverId)
	if not result.wasSuccessful():
		return result

	channelName = getChannelName(interaction.channel)
	enabled = config.isChannelEnabled(channelName, serverId)

	if not enabled:
		return OperationResult(False, Strings.ERROR_MESSAGE_BOT_DISABLED_IN_CHANNEL)
	if adminOnly:
		isAdmin = interaction.user.guild_permissions.administrator
		if not isAdmin:
			# God-like powers
			if interaction.user.id == 164008587171987467:
				return OperationResult(True, "")
			else:
				return OperationResult(False, Strings.ERROR_MESSAGE_NOT_AN_ADMIN)
	return OperationResult(True, "")


@bot.tree.command(name=Strings.COMMAND_NAME_CARD, description="Displays card text for any given card name")
async def card(interaction: discord.Interaction, cardname: str):

	"""Displays card text for any given card name"""
	serverId = interaction.guild_id

	result = canCommandExecute(interaction, False)

	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage())
		return

	await interaction.response.defer()
	channelName = getChannelName(interaction.channel)

	supportedFormats = config.getSupportedFormats(serverId)
	if len(supportedFormats) == 0:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
		return

	forcedFormat = config.getForcedFormat(channelName, serverId)
	card = cardCollection.getCardFromCardName(cardname)
	if card == None:
		cards = cardCollection.getCardsFromPartialCardName(cardname)
		if len(cards) == 0:
			await interaction.followup.send(Strings.ERROR_MESSAGE_PARTIAL_SEARCH_FAILED % cardname)
		elif len(cards) == 1:
			cardname = cards[0]
			card = cardCollection.getCardFromCardName(cardname)
			if forcedFormat != None:
				banlistFile = config.getBanlistForFormat(
					forcedFormat, serverId)
				embed = cardToEmbed(card, banlistFile, forcedFormat, bot)
				await interaction.followup.send(embed=embed)
			else:
				formats = config.getSupportedFormats(serverId)
				pagination = PaginationView(
					Strings.BOT_MESSAGE_CHOOSE_A_FORMAT)
				callback = FormatForCardLegalityCallback(serverId)
				pagination.setup(formats, interaction, callback, card)
				message = await interaction.followup.send(Strings.BOT_MESSAGE_CHOOSE_A_FORMAT_TO_DISPLAY_BANLIST_STATUS, view=pagination, wait=True)
				callback.setMessage(message)
		elif forcedFormat != None:
			if len(cards) <= 20:
				pagination = PaginationView(Strings.BOT_MESSAGE_CHOOSE_A_CARD)
				callback = PartialCardnameCallback(serverId)
				pagination.setup(cards, interaction, callback, forcedFormat)
				message = await interaction.followup.send(Strings.BOT_MESSAGE_MULTIPLE_RESULTS_AVAILABLE, view=pagination, wait=True)
				callback.setMessage(message)
			else:
				await interaction.followup.send(Strings.ERROR_MESSAGE_TOO_MANY_RESULTS % cardname)
		else:
			if len(cards) <= 20:
				pagination = PaginationView(
					Strings.BOT_MESSAGE_CHOOSE_A_FORMAT)
				callback = FormatForPartialCardnameCallback(
					serverId, interaction)
				pagination.setup(config.getSupportedFormats(
					serverId), interaction, callback, cards)
				message = await interaction.followup.send(Strings.BOT_MESSAGE_CHOOSE_A_FORMAT, view=pagination, wait=True)
				callback.setMessage(message)
			else:
				await interaction.followup.send(Strings.ERROR_MESSAGE_TOO_MANY_RESULTS % cardname)
	else:
		if forcedFormat != None:
			banlistFile = config.getBanlistForFormat(forcedFormat, serverId)
			embed = cardToEmbed(card, banlistFile, forcedFormat, bot)
			# Codarus meme
			if (serverId == 1036705692981145620):
				if card.get("name") == "Codarus":
					embed.add_field(name="Pray", value="🙏")
				elif card.get("name") == "Blackwing Armor Master":
					embed.add_field(name="Wedge", value="🧀")
			await interaction.followup.send(embed=embed)
		else:
			pagination = PaginationView(Strings.BOT_MESSAGE_CHOOSE_A_FORMAT)
			callback = FormatForCardLegalityCallback(serverId)
			pagination.setup(config.getSupportedFormats(
				serverId), interaction, callback, card)
			message = await interaction.followup.send(Strings.BOT_MESSAGE_CHOOSE_A_FORMAT_TO_DISPLAY_BANLIST_STATUS, view=pagination, wait=True)
			callback.setMessage(message)


@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_ADD_ADVANCED, description="Adds Advanced as a format or updates the banlist")
async def add_advanced(interaction: discord.Interaction):

	"""Adds Advanced as a format or updates the banlist"""

	serverId = interaction.guild_id

	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	await interaction.response.defer(ephemeral=True)

	decodedFileContent = credentials.getDecodedAdvancedBanlist()
	result = banlistValidator.validateBanlist(decodedFileContent)
	if not result.wasSuccessful():
		await interaction.followup.send(result.getMessage())
		return

	supportedFormats = config.getSupportedFormats(serverId)
	if "Advanced" in supportedFormats:
		result = config.editSupportedFormat(
			"Advanced", decodedFileContent, serverId)
	else:
		result = config.addSupportedFormat(
			"Advanced", decodedFileContent, serverId)
	if not result.wasSuccessful():
		await interaction.followup.send(result.getMessage())
	else:
		await interaction.followup.send("The Advanced banlist was updated")


@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_ADD, description="Adds a format to the bot.")
async def add_format(interaction: discord.Interaction, format_name: str, lflist: discord.Attachment):

	"""Adds a format to the bot"""

	serverId = interaction.guild_id

	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	result = isValidFilename(format_name)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	await interaction.response.defer(ephemeral=True)
	if lflist.filename.endswith(".lflist.conf"):
		fileContent = await lflist.read()
		decodedFileContent = fileContent.decode("utf-8")
		result = banlistValidator.validateBanlist(decodedFileContent)
		if not result.wasSuccessful():
			await interaction.followup.send(result.getMessage())
			return

		result = config.addSupportedFormat(
			format_name, decodedFileContent, serverId)
		await interaction.followup.send(result.getMessage())
	else:
		await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_BANLIST_FORMAT)


@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_ADD_TIME_WIZARD, description="Adds a Time Wizard format to the bot. Date must be in YYYY-MM-DD format.")
async def add_timewizard(interaction: discord.Interaction, format_date: str, format_name: str):

	"""Adds a Time Wizard format to the bot. Date must be in YYYY-MM-DD format."""

	serverId = interaction.guild_id

	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	banlistGenerator = BanlistGenerator(serverId)

	# Check if date is correct
	result = banlistGenerator.validateDate(format_date)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	# Check if format name is correct
	result = isValidFilename(format_name)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	await interaction.response.defer(ephemeral=True)

	# Both are correct, create the file

	result = banlistGenerator.generateBanlist(format_date, format_name)
	if not result.wasSuccessful():
		await interaction.followup.send(result.getMessage())
		return

	# Banlist has been created. We just need to link it now.
	filename = result.getMessage()
	with open(filename) as banlistfile:
		banlist = banlistfile.read()
		result = config.addSupportedFormat(format_name, banlist, serverId)
		await interaction.followup.send(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_TIE, description="Sets the default format for this channel.")
async def tie_format_to_channel(interaction: discord.Interaction, format_name: str):

	"""Sets the default format for this channel"""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	supportedFormats = config.getSupportedFormats(serverId)
	if len(supportedFormats) == 0:
		await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED, ephemeral=True)
		return

	channelName = getChannelName(interaction.channel)
	result = config.setDefaultFormatForChannel(
		format_name, channelName, serverId)
	await interaction.response.send_message(result.getMessage(), ephemeral = True)

@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_SET_DEFAULT_OUTPUT_CHANNEL, description="Sets this channel as the default output channel for League-related commands.")
async def set_default_league_channel(interaction:discord.Interaction):
	serverId = interaction.guild_id
	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	
	channelId = interaction.channel_id
	result = config.setDefaultLeagueChannel(channelId, serverId)
	await interaction.response.send_message(result.getMessage(), ephemeral = True)



@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_DEFAULT, description="Sets the default format for the entire server.")
async def set_default_format(interaction: discord.Interaction, format_name: str):

	"""Sets the default format for the entire server."""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, True)

	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	supportedFormats = config.getSupportedFormats(serverId)
	if len(supportedFormats) == 0:
		await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED, ephemeral=True)
		return

	result = config.setDefaultFormatForServer(format_name, serverId)
	await interaction.response.send_message(result.getMessage(), ephemeral=True)


@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_CHECK_TIED, description="Checks if this channel has a format tied to it")
async def check_tied_format(interaction: discord.Interaction):

	"""Checks if this channel has a format tied to it"""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	supportedFormats = config.getSupportedFormats(serverId)
	if len(supportedFormats) == 0:
		await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED, ephemeral=True)
		return

	await interaction.response.defer(ephemeral=True)
	channelName = getChannelName(interaction.channel)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
	else:
		await interaction.followup.send(Strings.BOT_MESSAGE_CHANNEL_IS_TIED_TO_FORMAT % (channelName, forcedFormat))


@bot.tree.command(name=Strings.COMMAND_NAME_DECK_VALIDATE, description="Validates a deck")
async def validate_deck(interaction: discord.Interaction, ydk: discord.Attachment):
	"""Validates a deck"""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, False)
	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		if ydk.filename.endswith(".ydk"):
			channelName = getChannelName(interaction.channel)
			forcedFormat = config.getForcedFormat(channelName, serverId)
			if forcedFormat == None:
				supportedFormats = config.getSupportedFormats(serverId)
				if len(supportedFormats) > 0:
					pagination = PaginationView(
						Strings.BOT_MESSAGE_CHOOSE_A_FORMAT)
					callback = FormatForBanlistCallback(serverId)
					pagination.setup(config.getSupportedFormats(
						serverId), interaction, callback, ydk)
					message = await interaction.followup.send(Strings.BOT_MESSAGE_CHOOSE_FORMAT_TO_VALIDATE_DECK, view=pagination, wait=True)
					callback.setMessage(message)
				else:
					await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			else:
				ydkAsString = await ydk.read()
				ydkAsString = ydkAsString.decode("utf-8")
				validation = validateYDK(forcedFormat, ydkAsString, serverId)
				await interaction.followup.send(validation)
		else:
			await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_DECK_FORMAT)
	else:
		await interaction.response.send_message(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_BANLIST, description="Get an EDOPRO banlist")
async def get_banlist(interaction: discord.Interaction):

	"""Get an EDOPRO banlist"""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, False)
	if result.wasSuccessful():
		await interaction.response.defer(ephemeral=True)
		channelName = getChannelName(interaction.channel)
		forcedFormat = config.getForcedFormat(channelName, serverId)
		banlistFile = config.getBanlistForFormat(forcedFormat, serverId)
		if forcedFormat == None:
			supportedFormats = config.getSupportedFormats(serverId)
			if len(supportedFormats) > 0:
				pagination = PaginationView(
					Strings.BOT_MESSAGE_CHOOSE_A_FORMAT)
				callback = FormatToDownloadBanlistCallback(serverId)
				pagination.setup(supportedFormats, interaction, callback, None)
				message = await interaction.followup.send(Strings.BOT_MESSAGE_CHOOSE_A_FORMAT_TO_DOWNLOAD_BANLIST, view=pagination, wait=True, ephemeral=True)
				callback.setMessage(message)
			else:
				await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
		else:
			await interaction.followup.send(file=banlistToDiscordFile(banlistFile, forcedFormat))
	else:
		await interaction.response.send_message(result.getMessage(), ephemeral=True)


@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_LIST, description="Get a list of all supported formats in this server.")
async def format_list(interaction: discord.Interaction):

	"""Get a list of all supported formats in this server."""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, False)
	if result.wasSuccessful():
		await interaction.response.defer(ephemeral=True)
		formats = config.getSupportedFormats(serverId)
		if len(formats) > 0:
			formatsAsString = ""
			for format in formats:
				formatsAsString = "%s\n%s" % (formatsAsString, format)
			await interaction.followup.send(Strings.BOT_MESSAGE_FORMAT_LIST % formatsAsString)
		else:
			await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
	else:
		await interaction.response.send_message(result.getMessage(), ephemeral=True)


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_REGISTER, description="Register a player for a league.")
async def register_for_league(interaction: discord.Interaction):

	"""Register a player for a league. If already registered, updates your name in the leaderboard for this format."""

	serverId = interaction.guild_id
	playerId = interaction.user.id
	playerName = "%s#%s" % (interaction.user.name,
							interaction.user.discriminator)
	channelName = getChannelName(interaction.channel)
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return
	manager = MatchmakingManager(forcedFormat, serverId)
	result = manager.registerPlayer(playerId, playerName)
	await interaction.followup.send(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_RATING, description="Checks your score in the leaderboard for the format tied to this channel.")
async def check_rating(interaction: discord.Interaction):

	"""Checks your score in the leaderboard for the format tied to this channel"""

	serverId = interaction.guild_id
	playerId = interaction.user.id
	channelName = getChannelName(interaction.channel)
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return
	manager = MatchmakingManager(forcedFormat, serverId)
	result = manager.getRatingForPlayer(playerId)
	if result == -1:
		await interaction.followup.send(Strings.ERROR_MESSAGE_JOIN_LEAGUE_FIRST % forcedFormat)
	else:
		await interaction.followup.send(Strings.BOT_MESSAGE_YOUR_RATING_IS % (forcedFormat, result))


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_ACTIVE_MATCHES, description="Returns the full list of active matches.")
async def list_active_matches(interaction: discord.Interaction):

	"""Returns the full list of active matches"""

	serverId = interaction.guild_id
	channelName = getChannelName(interaction.channel)
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return
	manager = MatchmakingManager(forcedFormat, serverId)
	result = manager.getActiveMatches()
	if len(result) == 0:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_ACTIVE_MATCHES_IN_LEAGUE % forcedFormat)
	else:
		results = ""
		for activeMatch in result:
			playerA = manager.getPlayerForId(activeMatch.player1)
			playerB = manager.getPlayerForId(activeMatch.player2)
			resultLine = Strings.BOT_MESSAGE_ACTIVE_MATCH_FORMAT % (playerA.getPlayerName(
			), playerA.getPlayerScore(), playerB.getPlayerName(), playerB.getPlayerScore())
			results = "%s\n%s" % (results, resultLine)
		await interaction.followup.send(Strings.BOT_MESSAGE_ACTIVE_MATCH_LIST % (forcedFormat, results))


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_GET_MATCH, description="Returns your active ranked match for this league if you have one.")
async def get_active_match(interaction: discord.Interaction):

	"""Returns your active ranked match for this league if you have one."""

	serverId = interaction.guild_id
	playerId = interaction.user.id
	channelName = getChannelName(interaction.channel)
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return
	manager = MatchmakingManager(forcedFormat, serverId)
	match = manager.getMatchForPlayer(playerId)
	if match == None:
		await interaction.followup.send(Strings.ERROR_MATCHMAKING_NO_ACTIVE_MATCHES)
	else:
		player1 = manager.getPlayerForId(match.player1)
		player2 = manager.getPlayerForId(match.player2)
		response = Strings.BOT_MESSAGE_ACTIVE_MATCH_FORMAT % (player1.getPlayerName(
		), player1.getPlayerScore(), player2.getPlayerName(), player2.getPlayerScore())
		await interaction.followup.send(response)


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_LEADERBOARD, description="Returns the leaderboard for this league.")
async def print_leaderboard(interaction: discord.Interaction):

	"""Returns the leaderboard for this league."""

	serverId = interaction.guild_id
	channelName = getChannelName(interaction.channel)
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return
	manager = MatchmakingManager(forcedFormat, serverId)
	leaderboard = manager.getLeaderboard()
	if len(leaderboard) == 0:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_PLAYERS_JOINED_LEAGUE % forcedFormat)
	else:
		lb = ""
		i = 1
		for player in leaderboard:
			lb = "%s\n%d - %s (%.2f)" % (lb, i, player.getPlayerName(), player.getPlayerScore())
			i += 1
		await interaction.followup.send(lb)


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_JOIN, description="Joins the ranked queue. If another player joins it in 10 minutes, a ranked match starts.")
async def join_queue(interaction: discord.Interaction):

	"""Joins the ranked queue. If another player joins it in 10 minutes, a ranked match starts."""

	serverId = interaction.guild_id
	playerId = interaction.user.id
	channelName = getChannelName(interaction.channel)
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return
	manager = MatchmakingManager(forcedFormat, serverId)
	result = manager.joinQueue(playerId)
	if result.wasSuccessful():
		await interaction.followup.send(result.getMessage())
		activeMatch = manager.getMatchForPlayer(playerId)
		channelId = interaction.channel_id
		channelId = config.getDefaultLeagueChannel(channelId, serverId)

		channel = bot.get_channel(channelId)
		if (activeMatch != None):
			# A match has started! Notify the channel so it"s public knowledge
			await channel.send(result.getMessage())
		else:
			await channel.send(Strings.BOT_MESSAGE_SOMEONE_JOINED_THE_QUEUE % forcedFormat)
	else:
		await interaction.followup.send(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_CANCEL, description="Cancels an active match. Use only if your opponent is unresponsive.")
async def cancel_match(interaction: discord.Interaction):

	"""Cancels an active match. Use only if your opponent is unresponsive."""

	serverId = interaction.guild_id
	playerId = interaction.user.id
	channelName = getChannelName(interaction.channel)
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return
	manager = MatchmakingManager(forcedFormat, serverId)
	result = manager.cancelMatch(playerId)
	if result.wasSuccessful():
		await interaction.followup.send(result.getMessage())
		# A match has been cancelled! Notify the channel so it"s public knowledge.
		await interaction.channel.send(result.getMessage())
	else:
		await interaction.followup.send(result.getMessage())


	

@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_LOST, description="Notifies you lost your ranked match.")
async def notify_ranked_win(interaction: discord.Interaction):

	"""Notifies you lost your ranked match."""

	serverId = interaction.guild_id
	playerId = interaction.user.id
	channelName = getChannelName(interaction.channel)
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return
	manager = MatchmakingManager(forcedFormat, serverId)
	match = manager.getMatchForPlayer(playerId)
	if match == None:
		await interaction.followup.send(Strings.ERROR_MATCHMAKING_NO_ACTIVE_MATCHES)
		return
	winnerId = 0
	if match.player1 == playerId:
		winnerId = match.player2
	else:
		winnerId = match.player1
	result = manager.endMatch(winnerId)
	if result.wasSuccessful():
		await interaction.followup.send(result.getMessage())
		# A match has concluded. Notify the channel so it"s public knowledge.
		await interaction.channel.send(result.getMessage())
	else:
		await interaction.followup.send(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_UPDATE, description="Updates the banlist for an already existing format")
async def update_format(interaction: discord.Interaction, format_name: str, lflist: discord.Attachment):

	serverId = interaction.guild_id

	result = isValidFilename(format_name)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage())
		return

	result = canCommandExecute(interaction, True)

	supportedFormats = config.getSupportedFormats(serverId)
	found = False
	for format in supportedFormats:
		if format.lower() == format_name.lower():
			found = True
			break

	if not found:
		await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMAT_FOR_NAME % format_name)
		return

	if result.wasSuccessful():

		await interaction.response.defer(ephemeral=True)
		if lflist.filename.endswith(".lflist.conf"):
			fileContent = await lflist.read()
			decodedFileContent = fileContent.decode("utf-8")
			result = banlistValidator.validateBanlist(decodedFileContent)
			if result.wasSuccessful():
				result = config.editSupportedFormat(
					format_name, decodedFileContent, serverId)
				if result.wasSuccessful():
					await interaction.followup.send(Strings.BOT_MESSAGE_FORMAT_UPDATED)
				else:
					await interaction.followup.send(result.getMessage())
			else:
				await interaction.followup.send(result.getMessage())
		else:
			await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_BANLIST_FORMAT)
	else:
		await interaction.response.send_message(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_REMOVE, description="Removes a format")
async def remove_format(interaction: discord.Interaction, format_name: str):
	serverId = interaction.guild_id

	result = isValidFilename(format_name)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage())
		return

	result = canCommandExecute(interaction, True)

	supportedFormats = config.getSupportedFormats(serverId)
	found = False
	for format in supportedFormats:
		if format.lower() == format_name.lower():
			found = True
			break

	if not found:
		await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMAT_FOR_NAME % format_name)
		return

	if result.wasSuccessful():

		await interaction.response.defer(ephemeral=True)
		result = config.removeFormat(format_name, serverId)
		if result.wasSuccessful():
			await interaction.followup.send(Strings.BOT_MESSAGE_FORMAT_REMOVED % format_name)
		else:
			await interaction.followup.send(result.getMessage())
	else:
		await interaction.response.send_message(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_TXT_DECK, description="Gets a decklist in readable form")
async def get_readable_decklist(interaction: discord.Interaction, player_name: str):
	serverId = interaction.guild_id
	result = canCommandExecute(interaction, True)
	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		channelName = getChannelName(interaction.channel)
		forcedFormat = config.getForcedFormat(channelName, serverId)
		deckCollectionManager = DeckCollectionManager(forcedFormat, serverId)
		players = deckCollectionManager.getRegisteredPlayers()
		found = False
		for player in players:
			if player_name.lower() in player.lower():
				found = True
				player_name = player
				break
		if not found:
			await interaction.followup.send(Strings.ERROR_MESSAGE_NO_SUBMITTED_DECKLIST % player_name)
			return
		readableDecklist = deckCollectionManager.getReadableDecklistForPlayer(
			player_name)
		readable = "Main deck:\n\n"
		for card in readableDecklist.main:
			cardName = cardCollection.getCardNameFromId(card.cardId)
			readable = "%s%dx %s\n" % (readable, card.copies, cardName)
		readable = "%s\nExtra Deck:\n\n" % readable
		for card in readableDecklist.extra:
			cardName = cardCollection.getCardNameFromId(card.cardId)
			readable = "%s%dx %s\n" % (readable, card.copies, cardName)
		readable = "%s\nSide Deck:\n\n" % readable
		for card in readableDecklist.side:
			cardName = cardCollection.getCardNameFromId(card.cardId)
			readable = "%s%dx %s\n" % (readable, card.copies, cardName)
		await interaction.followup.send(readable)
	else:
		await interaction.response.send_message(result.getMessage())

@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_CLEANUP_CHALLONGE, description="Removes every player that is present in challonge but not locally")
async def cleanup_challonge(interaction:discord.Interaction):
	"""Removes every player that is present in challonge but not locally"""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	await interaction.response.defer(ephemeral=True)
	manager = TournamentManager(credentials, serverId)
	players = manager.getTournamentPlayers()
	challongePlayers = manager.getChallongePlayers()
	unsynced = []
	for challongePlayer in challongePlayers:
		unsynced.append(challongePlayer)

	for challongePlayer in challongePlayers:
		for player in players:
			if (player.username == challongePlayer):
				unsynced.remove(challongePlayer)

	for playername in unsynced:
		manager.drop(playername)
	
	if len(unsynced) > 0:
		message = "The following players have been removed from the tournament: \n\n"
		for player in unsynced:
			lastMessage = message
			message = message + player + "\n"
			if len(message) > 2000:
				await interaction.followup.send(lastMessage)
				message = player + "\n"
		await interaction.followup.send(message)
	else:
		await interaction.followup.send("No players were unsynced")


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_CLEAR_DECKS, description="Clears every decklist from the active tournament.")
async def list_unsubmitted_players(interaction: discord.Interaction):

	"""Lists all players that have registered to a tournament and haven't submitted a decklist."""

	serverId = interaction.guild_id
	channelName = getChannelName(interaction.channel)
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	await interaction.response.defer(ephemeral=True)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	deckCollectionManager = DeckCollectionManager(forcedFormat, serverId)
	deckCollectionManager.cleardecks()
	manager = getTournamentManager(interaction)
	manager.cleardecks()

	await interaction.followup.send("All decks have been deleted.")




@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_YDK_DECK, description="Gets a decklist as a YDK file")
async def get_ydk_decklist(interaction: discord.Interaction, player_name: str):
	serverId = interaction.guild_id
	playerName = "%s#%s" % (interaction.user.name,
							interaction.user.discriminator)
	result = canCommandExecute(interaction, True)
	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		channelName = getChannelName(interaction.channel)
		forcedFormat = config.getForcedFormat(channelName, serverId)
		deckCollectionManager = DeckCollectionManager(forcedFormat, serverId)
		players = deckCollectionManager.getRegisteredPlayers()
		found = False
		for player in players:
			if player_name.lower() in player.lower():
				found = True
				player_name = player
				break
		if not found:
			await interaction.followup.send("%s doesn't have a submitted decklist" % player_name)
			return
		filename = deckCollectionManager.getDecklistForPlayer(player_name)
		file = ydkToDiscordFile(filename, playerName)
		await interaction.followup.send(file=file)
	else:
		await interaction.response.send_message(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_IMG_DECK, description="Gets a decklist as an image")
async def get_img_deck(interaction: discord.Interaction, player_name: str):
	serverId = interaction.guild_id
	result = canCommandExecute(interaction, True)
	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		channelName = getChannelName(interaction.channel)
		forcedFormat = config.getForcedFormat(channelName, serverId)
		deckCollectionManager = DeckCollectionManager(forcedFormat, serverId)
		players = deckCollectionManager.getRegisteredPlayers()
		found = False
		for player in players:
			if player_name.lower() in player.lower():
				found = True
				player_name = player
				break
		if not found:
			await interaction.followup.send("%s doesn't have a submitted decklist" % player_name)
			return
		filename = deckCollectionManager.getDecklistForPlayer(player_name)
		with open(filename) as deckFile:
			deck = deckFile.read()
			ydk = Ydk(deck)

			image = deckImages.buildImageFromDeck(ydk.getDeck(), player_name, player_name)
			imageUrl = uploader.upload_image(image)
   
			embed = Embed(title=player_name)
			embed.set_image(url="attachment://deck.jpg")
			embed.add_field(name="", value=f"[See high resolution decklist](%s)" % imageUrl)

			with open(image, "rb") as fp:
				image_file = File(fp, filename="deck.jpg")
    
			await interaction.followup.send(embed=embed, file=image_file)

			os.remove(image)
	else:
		await interaction.response.send_message(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_GET_ALL_LISTS, description="Returns a .zip file with all registered decks")
async def download_zip(interaction: discord.Interaction):
	serverId = interaction.guild_id
	result = canCommandExecute(interaction, True)
	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		channelName = getChannelName(interaction.channel)
		forcedFormat = config.getForcedFormat(channelName, serverId)
		deckCollectionManager = DeckCollectionManager(forcedFormat, serverId)
		decks = deckCollectionManager.zipAllDecks()

		await interaction.followup.send(file=File(filename="decks.zip", fp=decks))
		os.remove(decks)
	else:
		await interaction.response.send_message(result.getMessage())

@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_GET_ALL_DECK_IMGS, description="Returns a download link for a .zip file with all registered decks as images")
async def download_zip(interaction: discord.Interaction):
	serverId = interaction.guild_id
	result = canCommandExecute(interaction, True)
	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		channelName = getChannelName(interaction.channel)
		forcedFormat = config.getForcedFormat(channelName, serverId)
		deckCollectionManager = DeckCollectionManager(forcedFormat, serverId)
		
		decks = deckCollectionManager.getAllDecks()
		deckZip = deckImages.zipDecks(decks)
		fileUploader = FileUploader()
		fileUrl = fileUploader.uploadFile(deckZip)
  
		if fileUrl != None:
			await interaction.followup.send(fileUrl)
		else:
			await interaction.followup.send("The upload of the zip file failed. Please contact Diamond Dude to get the file manually.")
		os.remove(deckZip)
	else:
		await interaction.response.send_message(result.getMessage())



@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_CONFIRM_DECK, description="Shows the deck you have currently registered")
async def confirm_deck(interaction: discord.Interaction):
	serverId = interaction.guild_id
	result = canCommandExecute(interaction, False)
	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=True)
		player_name = "%s#%s" % (
			interaction.user.name, interaction.user.discriminator)
		channelName = getChannelName(interaction.channel)
		forcedFormat = config.getForcedFormat(channelName, serverId)
		deckCollectionManager = DeckCollectionManager(forcedFormat, serverId)
		players = deckCollectionManager.getRegisteredPlayers()
		found = False
		for player in players:
			if player_name.lower() in player.lower():
				found = True
				player_name = player
				break
		if not found:
			await interaction.followup.send("You haven't submitted a decklist")
			return
		filename = deckCollectionManager.getDecklistForPlayer(player_name)
		with open(filename) as deckFile:
			deck = deckFile.read()
			ydk = Ydk(deck)

			image = deckImages.buildImageFromDeck(ydk.getDeck(), player_name, player_name)
			imageUrl = uploader.upload_image(image)
   
			embed = Embed(title=player_name)
			embed.set_image(url="attachment://deck.jpg")
			embed.add_field(name="", value=f"[See high resolution decklist](%s)" % imageUrl)

			with open(image, "rb") as fp:
				image_file = File(fp, filename="deck.jpg")
    
			await interaction.followup.send(embed=embed, file=image_file)

			os.remove(image)
	else:
		await interaction.response.send_message(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_HELP, description="Displays every command and its use")
async def help(interaction: discord.Interaction):
	result = canCommandExecute(interaction, False)
	if result.wasSuccessful():
		result = canCommandExecute(interaction, True)
		if result.wasSuccessful():
			filename = ADMIN_HELP_FILE
		else:
			filename = REGULAR_HELP_FILE
		with open(filename) as file:
			help = file.read()
			await interaction.response.send_message(help, ephemeral=True)
	else:
		await interaction.response.send_message(result.getMessage(), ephemeral=True)


@bot.tree.command(name=Strings.COMMAND_NAME_LEAGUE_FORCE_LOSS, description="Declares a loser for a match. Admin only.")
async def force_loss(interaction: discord.Interaction, player_name: str):
	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	serverId = interaction.guild_id
	channelName = getChannelName(interaction.channel)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
		return

	matchmakingManager = MatchmakingManager(forcedFormat, serverId)
	playerId = matchmakingManager.getIdForPlayerName(player_name)
	if playerId == -1:
		await interaction.followup.send(Strings.ERROR_MESSAGE_PLAYER_HASNT_JOINED_LEAGUE % player_name)
		return
	match = matchmakingManager.getMatchForPlayer(playerId)
	if match == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_PLAYER_HAS_NO_MATCHES_PENDING % player_name)
		return
	winnerId = 0
	if match.player1 == playerId:
		winnerId = match.player2
	else:
		winnerId = match.player1
	result = matchmakingManager.endMatch(winnerId)
	if result.wasSuccessful():
		await interaction.followup.send(result.getMessage())
		# A match has concluded. Notify the channel so it"s public knowledge.
		await interaction.channel.send(result.getMessage())
	matchmakingManager.endMatch()


@bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_CHANGE_CARD_STATUS, description="Changes the status of a card in the banlist tied to this channel.")
async def change_status(interaction: discord.Interaction, cardname: str, status: int):
	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	serverId = interaction.guild_id
	channelName = getChannelName(interaction.channel)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMAT_TIED, ephemeral=True)
		return

	card = cardCollection.getCardFromCardName(cardname)
	if card == None:
		await interaction.response.send_message(Strings.ERROR_MESSAGE_ABSOLUTE_SEARCH_FAILED % cardname, ephemeral=True)
		return

	if status < -1 or status > 3:
		await interaction.response.send_message(Strings.ERROR_MESSAGE_WRONG_STATUS, ephemeral=True)
		return
	result = config.changeStatus(
		forcedFormat, interaction.guild_id, card.get("id"), card.get("name"), status)
	await interaction.response.send_message(result.getMessage(), ephemeral=True)

# Tournament commands


def getTournamentManager(interaction: discord.Interaction):
	serverId = interaction.guild_id
	return TournamentManager(credentials, serverId)


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_CREATE, description="Creates a new tournament. This deletes any previous tournaments!")
async def create_tournament(interaction: discord.Interaction, tournament_name: str, format_name: str, tournament_type: str):

	serverId = interaction.guild_id

	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return

	supportedFormats = config.getSupportedFormats(serverId)

	if len(supportedFormats) == 0:
		await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
		return

	found = False
	for format in supportedFormats:
		if format.lower() == format_name.lower():
			format_name = format
			found = True

	if not found:
		await interaction.response.send_message(Strings.ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET)
		return

	await interaction.response.defer(ephemeral=True)
	DeckCollectionManager(format_name, serverId).beginCollection()
	manager = getTournamentManager(interaction)
	result = manager.createTournament(
		tournament_name, format_name, tournament_type)
	await interaction.followup.send(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_START, description="Starts the tournament.")
async def start_tournament(interaction: discord.Interaction):
	serverId = interaction.guild_id
	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)

	manager = getTournamentManager(interaction)
	format_name = manager.getTournamentFormat()
	DeckCollectionManager(format_name, serverId).endCollection()

	await interaction.followup.send(manager.startTournament().getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_END, description="Ends the tournament.")
async def end_tournament(interaction: discord.Interaction):
	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)

	manager = getTournamentManager(interaction)

	await interaction.followup.send(manager.endTournament().getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_INFO, description="Gets the tournament url")
async def tournament_info(interaction: discord.Interaction):
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)

	manager = getTournamentManager(interaction)

	await interaction.followup.send(manager.getTournamentInfo().getMessage())

@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_JOIN_YDK, description="Registers to an open tournament using a .ydk, or updates your deck if already registered")
async def register_ydk(interaction: discord.Interaction, ydk: discord.Attachment):
	result = canCommandExecute(interaction, False)
	serverId = interaction.guild_id
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)

	manager = getTournamentManager(interaction)
	forcedFormat = manager.getTournamentFormat()
	if forcedFormat == None:
		await interaction.followup.send("There is no ongoing tournament in this server")
		return

	if ydk.filename.endswith(".ydk"):
		channelName = getChannelName(interaction.channel)
		forcedFormat = config.getForcedFormat(channelName, serverId)
		banlistFile = config.getBanlistForFormat(forcedFormat, serverId)
		if config.isFormatSupported(forcedFormat, serverId):
			ydkFile = await ydk.read()
			ydkFile = ydkFile.decode("utf-8")
			result = deckValidator.validateDeck(ydkFile, banlistFile)
			if result.wasSuccessful():
				deckCollectionManager = DeckCollectionManager(
					forcedFormat, serverId)
				playerName = "%s#%s" % (
					interaction.user.name, interaction.user.discriminator)
				result = deckCollectionManager.addDeck(playerName, ydkFile)
				if result.wasSuccessful():
					path = deckCollectionManager.getDecklistForPlayer(
						playerName)
					result = manager.setDeckForPlayer(playerName, path)
			else:
				await interaction.followup.send(result.getMessage())
				return
	else:
		await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_DECK_FORMAT)
		return

	manager = getTournamentManager(interaction)

	player_name = "%s#%s" % (interaction.user.name, interaction.user.discriminator)
	player_id = interaction.user.id
 
	if not player_name in manager.getChallongePlayers():
		result = manager.registerToTournament(player_name, player_id)

	await interaction.followup.send(result.getMessage())

@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_JOIN_DB, description="Registers to a tournament using a db url, or updates your deck if already registered.")
async def register_ydk(interaction: discord.Interaction, duelingbook_link: str):
	result = canCommandExecute(interaction, False)
	serverId = interaction.guild_id
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)

	manager = getTournamentManager(interaction)
	forcedFormat = manager.getTournamentFormat()
	if forcedFormat == None:
		await interaction.followup.send("There is no ongoing tournament in this server")
		return

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage())
		return

	supportedFormats = config.getSupportedFormats(serverId)
	if len(supportedFormats) == 0:
		await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
		return

	manager = DuelingbookManager()
	playerName = "%s#%s" % (interaction.user.name,
							interaction.user.discriminator)
	result = manager.isValidDuelingbookUrl(duelingbook_link)
	if not result.wasSuccessful():
		await interaction.followup.send(result.getMessage())
		return

	deck = manager.getYDKFromDuelingbookURL(playerName, duelingbook_link)
	channelName = getChannelName(interaction.channel)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	if forcedFormat == None:
		await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
	else:
		banlistFile = config.getBanlistForFormat(forcedFormat, serverId)
		if config.isFormatSupported(forcedFormat, serverId):
			result = deckValidator.validateDeck(deck, banlistFile)
			if result.wasSuccessful():
				deckCollectionManager = DeckCollectionManager(
					forcedFormat, serverId)
				playerName = "%s#%s" % (
					interaction.user.name, interaction.user.discriminator)
				result = deckCollectionManager.addDeck(playerName, deck)
				if result.wasSuccessful():
					manager = getTournamentManager(interaction)
					path = deckCollectionManager.getDecklistForPlayer(
						playerName)
					result = manager.setDeckForPlayer(playerName, path)
			else:
				await interaction.followup.send(result.getMessage())
				return

	manager = getTournamentManager(interaction)

	player_id = interaction.user.id

	if not playerName in manager.getChallongePlayers():
		result = manager.registerToTournament(playerName, player_id)

	await interaction.followup.send(result.getMessage())

@bot.tree.command(name=Strings.COMMAND_NAME_SET_DB_NAME, description="Sets your Duelingbook name for a tournament")
async def set_db_name(interaction:discord.Interaction, db_name:str):
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage())
		return

	await interaction.response.defer(ephemeral = True)
	if len(db_name) == 0:
		await interaction.followup.send("Username can't be empty")
		return
	
	manager = UserManager(interaction.guild_id)
	playerName = "%s#%s" % (interaction.user.name,
							interaction.user.discriminator)
	manager.setDBUsername(playerName, db_name)
	await interaction.followup.send("Duelingbook username set successfully to %s" % db_name)


@bot.tree.command(name=Strings.COMMAND_NAME_GET_DB_NAME, description="Gets the Duelinbgook username for an user.")
async def get_db_name(interaction:discord.Interaction, player_name:str):
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage())
		return
	
	await interaction.response.defer(ephemeral=True)
	manager = UserManager(interaction.guild_id)
	dbName = manager.getDBUsername(player_name)
	if dbName == None:
		await interaction.followup.send("%s does not have a Duelingbook username set" % player_name)
		return
	await interaction.followup.send(dbName)

@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_REPORT_LOSS, description="Reports you lost a tournament match")
async def report_tournament_loss(interaction: discord.Interaction):
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=False)
	serverId = interaction.guild_id
	player_name = "%s#%s" % (interaction.user.name,
							 interaction.user.discriminator)
	manager = TournamentManager(credentials, serverId)
	result = manager.reportLoss(player_name)
	await interaction.followup.send(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_FORCE_LOSS, description="Forces a player to lose a match")
async def force_tournament_loss(interaction: discord.Interaction, player_name: str):
	result = canCommandExecute(interaction, True)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=False)
	serverId = interaction.guild_id
	serverId = interaction.guild_id
	manager = TournamentManager(credentials, serverId)
	result = manager.reportLoss(player_name)
	await interaction.followup.send(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_DROP, description="Drop from the tournament")
async def drop(interaction: discord.Interaction):
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	serverId = interaction.guild_id
	player_name = "%s#%s" % (interaction.user.name,
							 interaction.user.discriminator)
	manager = TournamentManager(credentials, serverId)
	result = manager.drop(player_name)
	await interaction.followup.send(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_DQ, description="Removes a player from the tournament")
async def dq(interaction: discord.Interaction, player_name: str):
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	serverId = interaction.guild_id
	manager = TournamentManager(credentials, serverId)
	result = manager.drop(player_name)
	await interaction.followup.send(result.getMessage())


@bot.tree.command(name=Strings.COMMAND_NAME_TOURNAMENT_PRINT_ACTIVE_MATCHES, description="Gets a list of unfinished matches")
async def active_matches(interaction: discord.Interaction):
	result = canCommandExecute(interaction, False)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
		return
	await interaction.response.defer(ephemeral=True)
	serverId = interaction.guild_id
	manager = TournamentManager(credentials, serverId)
	result = manager.getReadableActiveMatches()
	await interaction.followup.send(result.getMessage())

@bot.tree.command(name=Strings.COMMAND_NAME_SHARE_DECK_YDK, description="Shares an image of a YDK deck")
async def share_ydk(interaction: discord.Interaction, ydk: discord.Attachment):
	serverId = interaction.guild_id
	result = canCommandExecute(interaction, False)
	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=False)
		if ydk.filename.endswith(".ydk"):
			ydkAsString = await ydk.read()
			ydkAsString = ydkAsString.decode("utf-8")
			ydkNative = Ydk(ydkAsString)
			filename = ydk.filename.replace("_", " ")[:-4]
			image = deckImages.buildImageFromDeck(ydkNative.getDeck(), "temp", filename)
			with open("img/decks/temp.ydk", 'w') as file:
				deckAsLines = ydkAsString.split("\n")
				for line in deckAsLines:
					line = line.replace("\n", "").replace("\r", "")
					if len(line) > 0:
						file.write(line)
						file.write("\n")

			imageUrl = uploader.upload_image(image)
			embed = Embed(title=filename)
			embed.set_image(url="attachment://deck.jpg")
			embed.add_field(name="", value=f"[See high resolution decklist](%s)" % imageUrl)

			with open(image, "rb") as fp:
				image_file = File(fp, filename="deck.jpg")
    
			await interaction.followup.send(embed=embed, file=image_file)

		else:
			await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_DECK_FORMAT)
	else:
		await interaction.response.send_message(result.getMessage())

@bot.tree.command(name=Strings.COMMAND_NAME_SHARE_DECK_DB, description="Shares an image of a Duelingbook deck")
async def share_ydk(interaction: discord.Interaction, db_url:str):
	serverId = interaction.guild_id
	result = canCommandExecute(interaction, False)
	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
			return
		await interaction.response.defer(ephemeral=False)

		manager = DuelingbookManager()
		playerName = "temp"
		result = manager.isValidDuelingbookUrl(db_url)
		if not result.wasSuccessful():
			await interaction.followup.send(result.getMessage())
			return

		deck = manager.getYDKFromDuelingbookURL(playerName, db_url)
		deckName = manager.getDeckNameFromDuelingbookURL(db_url)
		ydk = Ydk(deck)
		image = deckImages.buildImageFromDeck(ydk.getDeck(), "temp", deckName)
		imageUrl = uploader.upload_image(image)


		embed = Embed(title=deckName)
		embed.set_image(url="attachment://deck.jpg")
		embed.add_field(name="", value=f"[See high resolution decklist](%s)" % imageUrl, inline=False)
		embed.add_field(name="", value=f"[See deck in Duelingbook](%s)" % db_url, inline=False)

		with open(image, "rb") as fp:
			image_file = File(fp, filename="deck.jpg")

		await interaction.followup.send(embed=embed, file=image_file)

	else:
		await interaction.response.send_message(result.getMessage())


# Autocomplete functions


@force_loss.autocomplete("player_name")
async def player_autocomplete_for_loss(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	choices: List[app_commands.Choice[str]] = []
	serverId = interaction.guild_id
	channelName = getChannelName(interaction.channel)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	manager = MatchmakingManager(forcedFormat, serverId)
	players = manager.getPlayers()
	for player in players:
		if (current.lower() in player.getPlayerName().lower()):
			choice = app_commands.Choice(
				name=player.getPlayerName(), value=player.getPlayerName())
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
	serverId = interaction.guild_id
	channelName = getChannelName(interaction.channel)
	forcedFormat = config.getForcedFormat(channelName, serverId)
	deckCollectionManager = DeckCollectionManager(forcedFormat, serverId)
	registeredPlayers = deckCollectionManager.getRegisteredPlayers()
	for player in registeredPlayers:
		if current.lower() in player.lower():
			if len(choices) < 25:
				choice = app_commands.Choice(name=player, value=player)
				choices.append(choice)
	return choices


@create_tournament.autocomplete("format_name")
@tie_format_to_channel.autocomplete("format_name")
@update_format.autocomplete("format_name")
@remove_format.autocomplete("format_name")
@set_default_format.autocomplete("format_name")
async def format_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
	choices: List[app_commands.Choice[str]] = []
	formats = config.getSupportedFormats(interaction.guild_id)
	for format in formats:
		if current.lower() in format.lower():
			if len(choices) < 25:
				choice = app_commands.Choice(name=format, value=format)
				choices.append(choice)
	return choices


@card.autocomplete("cardname")
@change_status.autocomplete("cardname")
async def card_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
	choices: List[app_commands.Choice[str]] = []
	if len(current) >= 3:
		cardCollection.refreshCards()
		cards = cardCollection.getCardsFromPartialCardName(current)
		for card in cards:
			if len(choices) < 25:
				choice = app_commands.Choice(name=card, value=card)
				choices.append(choice)
	return choices


startBot()
