
from typing import List
import asyncio

import discord
from discord import app_commands
from src.command_manager import CommandManager
from src.card.card_collection import CardCollection
from src.league.matchmaking import MatchmakingManager
from src.config.config import Config
from src.config.server_config import ServerConfig

decay: bool = False

class ReallyBigYugiohBot(discord.Client):
	
	def __init__(self):
		intents = discord.Intents.default()
		intents.message_content = True
		super().__init__(intents=intents)
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		self.loop.create_task(decay_scores())
		card_collection = CardCollection()
		CommandManager(self, card_collection)
		new_commands = await self.tree.sync()

async def decay_scores():
	global decay
	if decay:
		servers: List[int] = ServerConfig().get_enabled_servers()
		for server_id in servers:
			# Get list of formats for that server
			formats = Config().get_supported_formats(server_id)
			for _format in formats:
				MatchmakingManager(_format, server_id).decay()
	else:
		decay = True
	await asyncio.sleep(86400)