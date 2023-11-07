# Pycache stuff

import sys

sys.dont_write_bytecode = True

# Imports

import asyncio

from typing import List

from src.league.matchmaking import MatchmakingManager
from src.command_manager import CommandManager
from src.utils.utils import ReallyBigYugiohBot
from src.credentials_manager import CredentialsManager
from src.config.config import Config
from src.config.server_config import ServerConfig
from src.card.card_collection import CardCollection

decay: bool = False

bot = ReallyBigYugiohBot()

card_collection = CardCollection()

commandManager = CommandManager(bot, card_collection)


def start_bot():
	bot.run(CredentialsManager().get_discord_key())

@bot.event
async def on_ready():
	print('Bot is ready')
	bot.loop.create_task(decay_scores())


async def decay_scores():
	global decay
	if decay:
		servers: List[int] = ServerConfig().get_enabled_servers()
		for server_id in servers:
			# Get list of formats for that server
			formats = Config(card_collection).get_supported_formats(server_id)
			for _format in formats:
				MatchmakingManager(_format, server_id).decay()
	else:
		decay = True
	await asyncio.sleep(86400)

start_bot()