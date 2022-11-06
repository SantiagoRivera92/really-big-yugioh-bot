import math
import discord
from discord import app_commands

dmChannelKey = "dm"
groupChannelKey = "group"
threadChannelKey = "thread"

class OperationResult:
	def __init__(self, success, message):
		self.success = success
		self.message = message

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

def getChannelName(channel):
	if isinstance(channel, discord.channel.DMChannel):
		return dmChannelKey
	elif isinstance(channel, discord.channel.GroupChannel):
		return groupChannelKey
	elif isinstance(channel, discord.channel.Thread):
		return threadChannelKey
	else:
		return channel.name

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()