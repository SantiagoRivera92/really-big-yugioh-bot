import discord
from discord import Embed, DMChannel
from discord import app_commands
from discord import File
from src.deck_validation import DeckValidator
from src.banlist_validation import BanlistValidator
from src.card_embeds import cardToEmbed
from src.utils import MyClient, OperationResult, getChannelName, isValidFilename
from src.views import PaginationView
from src.config import Config
from src.server_config import ServerConfig
from src.credentials_manager import CredentialsManager
from src.card_collection import CardCollection

#Configuration

credentialsFile = 'json/credentials.json'
enabledServers = 'json/enabledServers.json'

cardCollection = CardCollection()
credentials = CredentialsManager(credentialsFile)
config = Config(cardCollection)
deckValidator = DeckValidator(cardCollection)
banlistValidator = BanlistValidator()
serverConfig = ServerConfig(enabledServers)


intents = discord.Intents.default()
intents.message_content = True
bot = MyClient(intents=intents)

def startBot():
	bot.run(credentials.getDiscordAPIKey())

def banlistToDiscordFile(banlistFile, formatName):
	description = "Banlist for %s in .lflist.conf format (as used by EDOPRO)"%formatName
	fileName = "%s.lflist.conf"%formatName
	return File(description = description, filename=fileName, fp=banlistFile)

async def validateYDK(formatName, attachment, serverId):

	banlistFile = config.getBanlistForFormat(formatName, serverId)

	if config.isFormatSupported(formatName):
		ydkFile = await attachment.read()
		result = deckValidator.validateDeck(ydkFile, banlistFile)
		if result.wasSuccessful():
			return "Your deck is valid in %s" % formatName
		else:
			return "Your deck is not valid in %s.\n%s"%(formatName, result.getMessage())
	else:
		return "%s is not supported as a format as of right now." % formatName

# Callbacks

class FormatForBanlistCallback:

	def __init__(self, serverId):
		self.serverId = serverId

	def setMessage(self, message:discord.WebhookMessage):
		self.message = message

	async def executeCallback(self,formatName, attachment):
		validation = await validateYDK(formatName, attachment, self.serverId)
		await self.message.edit(content=validation, view=None)

class FormatForCardLegalityCallback:

	def __init__(self, serverId):
		self.serverId = serverId

	def setMessage(self, message:discord.WebhookMessage):
		self.message = message

	async def executeCallback(self, formatName, card):
		banlistFile = config.getBanlistForFormat(formatName, self.serverId)
		embed = cardToEmbed(card, banlistFile, formatName, bot)

		await self.message.edit(embed=embed, view=None)

class FormatToDownloadBanlistCallback:

	def __init__(self, serverId):
		self.serverId = serverId

	def setMessage(self, message:discord.WebhookMessage):
		self.message = message

	async def executeCallback(self,formatName, attachment):
		banlistFiles = config.getBanlistForFormat(formatName, self.serverId)
		await self.message.edit(content=None, embed=None, view=None, attachments=[banlistToDiscordFile(banlistFiles, formatName)])

class PartialCardnameCallback:

	def __init__(self, serverId):
		self.serverId = serverId

	def setMessage(self, message:discord.WebhookMessage):
		self.message = message

	async def executeCallback(self, cardName, formatName):
		card = cardCollection.getCardFromCardName(cardName)
		banlistfile = config.getBanlistForFormat(formatName, self.serverId)
		embed = cardToEmbed(card, banlistfile, formatName, bot)
		await self.message.edit(content="",embed=embed, view=None)

class FormatForPartialCardnameCallback:

	def __init__(self, serverId, interaction:discord.Interaction):
		self.serverId = serverId
		self.interaction = interaction
	
	def setMessage(self, message:discord.WebhookMessage):
		self.message = message

	async def executeCallback(self, formatName, cards):
		callback = PartialCardnameCallback(self.serverId)
		pagination = PaginationView('Select a card')
		pagination.setup(cards, self.interaction, callback, formatName)
		await self.message.delete()
		message = await self.interaction.followup.send(content="Multiple results available. Please pick one.", view=pagination)
		callback.setMessage(message)



# Events and commands

@bot.event
async def on_ready():
	pass


def canCommandExecute(interaction:discord.Interaction, adminOnly):
	serverId = interaction.guild_id
	result = serverConfig.checkServerEnabled(serverId)
	if not result.wasSuccessful():
		return result
	channelName = getChannelName(interaction.channel)
	enabled = config.isChannelEnabled(channelName, serverId)
	if not enabled:
		return OperationResult(False, "The bot is disabled in this channel!")
	if adminOnly:
		isAdmin = interaction.user.guild_permissions.administrator
		if not isAdmin:
			# God-like powers
			if interaction.user.id == 164008587171987467:
				return OperationResult(True, "")
			else:
				return OperationResult(False, "This command requires admin privileges")
	return OperationResult(True, "")

@bot.tree.command(name="card", description='Displays card text for any given card name')
async def card(interaction: discord.Interaction, cardname: str):

	"""Displays card text for any given card name"""
	serverId = interaction.guild_id

	result = canCommandExecute(interaction, False)

	if result.wasSuccessful():
		# Channel is enabled. We tell the interaction to wait for us until we find the card text
		await interaction.response.defer()
		channelName = getChannelName(interaction.channel)
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			interaction.response.send_message("No formats have been enabled in this server. To add a format, use /add_format")
			pass
		forcedFormat = config.getForcedFormat(channelName, serverId)
		card = cardCollection.getCardFromCardName(cardname)
		if card == None:
			cards = cardCollection.getCardsFromPartialCardName(cardname)
			if len(cards) == 0:
				await interaction.followup.send("There are no cards with %s in their name"%cardname)
			elif len(cards) == 1:
				cardname = cards[0]
				card = cardCollection.getCardFromCardName(cardname)
				if forcedFormat != None:
					banlistFile = config.getBanlistForFormat(forcedFormat, serverId)
					embed = cardToEmbed(card, banlistFile, forcedFormat, bot)
					await interaction.followup.send(embed=embed)
				else:
					formats = config.getSupportedFormats(serverId)
					pagination = PaginationView("Select a format")
					callback = FormatForCardLegalityCallback(serverId)
					pagination.setup(config.getSupportedFormats(serverId), interaction, callback, card)
					message = await interaction.followup.send("Please choose a format to display banlist status", view=pagination, wait=True)
					callback.setMessage(message)
			elif forcedFormat != None:
				if len(cards) <= 20:
					pagination = PaginationView('Select a card')
					callback = PartialCardnameCallback(serverId)
					pagination.setup(cards, interaction, callback, forcedFormat)
					message = await interaction.followup.send("Multiple results available. Please pick one.", view=pagination, wait=True)
					callback.setMessage(message)
				else:
					await interaction.followup.send("More than 20 cards contain %s. Please be more specific."%cardname)
			else:
				if len(cards) <= 20:
					pagination = PaginationView('Select a format')
					callback = FormatForPartialCardnameCallback(serverId, interaction)
					pagination.setup(config.getSupportedFormats(serverId), interaction, callback, cards)
					message = await interaction.followup.send("Select a format", view=pagination, wait=True)
					callback.setMessage(message)
				else:
					await interaction.followup.send("More than 20 cards contain %s. Please be more specific."%cardname)

		else:
			if forcedFormat != None:
				banlistFile = config.getBanlistForFormat(forcedFormat, serverId)
				embed = cardToEmbed(card, banlistFile, forcedFormat, bot)
				await interaction.followup.send(embed=embed)
			else:
				pagination = PaginationView("Select a format")
				callback = FormatForCardLegalityCallback(serverId)
				pagination.setup(config.getSupportedFormats(serverId), interaction, callback, card)
				message = await interaction.followup.send("Please choose a format to display banlist status", view=pagination, wait=True)
				callback.setMessage(message)
	else:
		await interaction.response.send_message(result.getMessage())

@bot.tree.command(name='add_format', description='Adds a format to the bot.')
async def add_format(interaction: discord.Interaction, format_name: str, lflist: discord.Attachment):

	"""Adds a format to the bot"""

	serverId = interaction.guild_id

	result = isValidFilename(format_name)
	if not result.wasSuccessful():
		await interaction.response.send_message(result.getMessage())
		pass

	result = canCommandExecute(interaction, True)

	if result.wasSuccessful():

		await interaction.response.defer(ephemeral=True)
		if lflist.filename.endswith(".lflist.conf"):
			fileContent = await lflist.read()
			decodedFileContent = fileContent.decode("utf-8")
			result = banlistValidator.validateBanlist(decodedFileContent)
			if result.wasSuccessful():
				result = config.addSupportedFormat(format_name, decodedFileContent, serverId)
				if result.wasSuccessful():
					await interaction.followup.send("Your format was added to the bot!")
				else:
					await interaction.followup.send(result.getMessage())
			else:
				await interaction.followup.send(result.getMessage())	
		else:
			await interaction.followup.send("The only supported banlist format is a .lflist.conf file")
	else:
		await interaction.response.send_message(result.getMessage())

@bot.tree.command(name='tie_format_to_channel', description="Sets the default format for this channel.")
async def tie_format_to_channel(interaction: discord.Interaction, format_name:str):

	"""Sets the default format for this channel"""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, True)

	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			interaction.response.send_message("No formats have been enabled in this server. To add a format, use /add_format")
			pass
		await interaction.response.defer(ephemeral=True)
		channelName = getChannelName(interaction.channel)
		result = config.setDefaultFormatForChannel(format_name, channelName, serverId)
		if result.wasSuccessful():
			await interaction.followup.send("%s is now the default format for channel %s"%(format_name, channelName))
		else:
			await interaction.followup.send(result.getMessage())
	else:
		await interaction.response.send_message(result.getMessage())

@bot.tree.command(name='check_tied_format', description="Checks if this channel has a format tied to it")
async def check_tied_format(interaction:discord.Interaction):

	"""Checks if this channel has a format tied to it"""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, False)

	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			interaction.response.send_message("No formats have been enabled in this server. To add a format, use /add_format")
			pass
		await interaction.response.defer(ephemeral=True)
		channelName = getChannelName(interaction.channel)
		forcedFormat = config.getForcedFormat(channelName, serverId)
		if forcedFormat == None:
			await interaction.followup.send("Channel %s has no format tied to it"%channelName)
		else:
			await interaction.followup.send("Channel %s is tied to a format: %s"%(channelName, forcedFormat))
	else:
		await interaction.response.send_message(result.getMessage())

@bot.tree.command(name='validate_deck', description="Validates a deck")
async def validate_deck(interaction:discord.Interaction, ydk: discord.Attachment):
	"""Validates a deck"""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, True)
	if result.wasSuccessful():
		supportedFormats = config.getSupportedFormats(serverId)
		if len(supportedFormats) == 0:
			interaction.response.send_message("No formats have been enabled in this server. To add a format, use /add_format")
			pass
		await interaction.response.defer(ephemeral=True)
		if ydk.filename.endswith(".ydk"):
			channelName = getChannelName(interaction.channel)
			forcedFormat = config.getForcedFormat(channelName, serverId)
			if forcedFormat == None:
				pagination = PaginationView("Select a format")
				callback = FormatForBanlistCallback(serverId)
				pagination.setup(config.getSupportedFormats(serverId), interaction, callback, ydk)
				message = await interaction.followup.send("Please choose a format to validate your deck", view=pagination, wait=True)
				callback.setMessage(message)
			else:
				validation = await validateYDK(forcedFormat, ydk)
				await interaction.followup.send(validation)
		else:
			await interaction.followup.send("Only .ydk files can be validated")
	else:
		await interaction.response.send_message(result.getMessage())

@bot.tree.command(name="get_banlist", description="Get an EDOPRO banlist")
async def get_banlist(interaction:discord.Interaction):

	"""Get an EDOPRO banlist"""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, False)
	if result.wasSuccessful():
		await interaction.response.defer(ephemeral=True)
		channelName = getChannelName(interaction.channel)
		forcedFormat = config.getForcedFormat(channelName, serverId)
		banlistFile = config.getBanlistForFormat(forcedFormat, serverId)

		if forcedFormat == None:
			pagination = PaginationView("Select a format")
			callback = FormatToDownloadBanlistCallback(serverId)
			pagination.setup(config.getSupportedFormats(serverId), interaction, callback, None)
			message = await interaction.followup.send("Please choose a format to download its banlist", view=pagination, wait=True, ephemeral=True)
			callback.setMessage(message)
		else:
			await interaction.followup.send(file=banlistToDiscordFile(banlistFile, forcedFormat))
	else:
		await interaction.response.send_message(result.getMessage(), ephemeral=True)

@bot.tree.command(name="format_list", description="Get a list of all supported formats in this server.")
async def format_list(interaction:discord.Interaction):

	"""Get a list of all supported formats in this server."""

	serverId = interaction.guild_id
	result = canCommandExecute(interaction, False)
	if result.wasSuccessful():
		await interaction.response.defer(ephemeral=True)
		formats = config.getSupportedFormats(serverId)
		if len(formats) > 0:
			formatsAsString = ""
			for format in formats:
				formatsAsString = "%s\n%s"%(formatsAsString, format)
			await interaction.followup.send("These are all the supported formats in this server:\n%s"%formatsAsString)
		else:
			await interaction.followup.send("No formats have been enabled in this server. To add a format, use /add_format")
	else:
		await interaction.response.send_message(result.getMessage(), ephemeral=True)
	

startBot()