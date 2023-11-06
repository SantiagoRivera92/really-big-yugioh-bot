import math
import discord
from discord import app_commands

DM_CHANNEL_KEY = "dm"
GROUP_CHANNEL_KEY = "group"
THREAD_CHANNEL_KEY = "thread"
OTHER_KEY = "other"

class OperationResult:
	
	def __init__(self, success, message):
		self.success = success
		self.message = message

	def was_successful(self):
		return self.success

	def get_message(self):
		return self.message

class ReallyBigYugiohBot(discord.Client):
	
	def __init__(self, *, intents: discord.Intents):
		super().__init__(intents=intents)
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		await self.tree.sync()

def get_status_in_banlist(cardId, banlist):
	banlist_as_lines = banlist.split("\n")
	id_as_string = str(cardId)
	for line in banlist_as_lines:
		id_in_line = line.split(' ')[0]
		if id_as_string == id_in_line:
			id_count = int(math.log10(cardId))+1
			line = line[id_count+1:id_count+2]
			if line == "-":
				line = "-1"
			return int(line)
	return -1

def get_channel_name(channel:discord.channel):
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