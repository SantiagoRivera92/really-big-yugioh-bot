import sys
sys.dont_write_bytecode = True

from src.credentials_manager import CredentialsManager
from src.bot.really_big_yugioh_bot import ReallyBigYugiohBot
from src.command_manager import CommandManager
from src.card.card_collection import CardCollection

bot = ReallyBigYugiohBot()

sync_commands=False

@bot.event
async def on_ready():
	CommandManager(bot, CardCollection())
	if sync_commands:
		commands = await bot.tree.sync()
		for command in commands:
			print(command.name)
	print('Bot is ready')


bot.run(CredentialsManager().get_discord_key())