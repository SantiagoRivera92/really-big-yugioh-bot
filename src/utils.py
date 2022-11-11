import math
import discord
import src.strings as Strings
from discord import app_commands

DM_CHANNEL_KEY = "dm"
GROUP_CHANNEL_KEY = "group"
THREAD_CHANNEL_KEY = "thread"
OTHER_KEY = "other"

class OperationResult:
	def __init__(self, success, message):
		self.success = success
		self.message = message
		self.hasExtras = False
		self.extraParam = None

	def addExtras(self, extraParam):
		self.extraParam = extraParam
		self.hasExtras = True

	def hasExtraParams(self):
		return self.hasExtras

	def getExtras(self):
		if self.hasExtras:
			return self.extraParam
		return None

	def wasSuccessful(self):
		return self.success

	def getMessage(self):
		return self.message

def getStatusInBanlist(cardId, banlist):
	banlistAsLines = banlist.split("\n")
	idAsString = str(cardId)
	for line in banlistAsLines:
		if idAsString in line:
			idCount = int(math.log10(cardId))+1
			line = line[idCount+1:idCount+2]
			if line == "-":
				line = "-1"
			return int(line)
	return -1


def getChannelName(channel:discord.channel):
	if isinstance(channel, discord.channel.DMChannel):
		return DM_CHANNEL_KEY
	elif isinstance(channel, discord.channel.GroupChannel):
		return GROUP_CHANNEL_KEY
	elif isinstance(channel, discord.channel.Thread):
		return THREAD_CHANNEL_KEY
	elif isinstance(channel, discord.channel.PartialMessageable):
		return OTHER_KEY
	else:
		return channel.name

def isValidFilename(filename:str):
	if len(filename) == 0:
		return OperationResult(False, Strings.ERROR_FORMAT_NAME_EMPTY)
	invalidCharacters = "#%&\{\}\\<>*?/$!\'\":@+`|="
	for char in invalidCharacters:
		if char in filename:
			return OperationResult(False, Strings.ERROR_FORMAT_NAME_INVALID_CHARACTER % char)
	return OperationResult(True, "")

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()