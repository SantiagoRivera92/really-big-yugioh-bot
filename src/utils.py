import math
import discord
from discord import app_commands

class OperationResult:
	
	def __init__(self, success, message):
		self.success = success
		self.message = message

	def was_successful(self):
		return self.success

	def get_message(self):
		return self.message

class ReallyBigYugiohBot(discord.Client):
	
	def __init__(self):
		intents = discord.Intents.default()
		intents.message_content = True
		super().__init__(intents=intents)
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		await self.tree.sync()

def get_status_in_banlist(card_id, banlist):
	banlist_as_lines = banlist.split("\n")
	id_as_string = str(card_id)
	for line in banlist_as_lines:
		id_in_line = line.split(' ')[0]
		if id_as_string == id_in_line:
			id_count = int(math.log10(card_id))+1
			line = line[id_count+1:id_count+2]
			if line == "-":
				line = "-1"
			return int(line)
	return -1