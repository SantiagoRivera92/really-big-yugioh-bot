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