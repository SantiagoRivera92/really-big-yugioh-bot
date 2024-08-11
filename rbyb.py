import sys
sys.dont_write_bytecode = True

from src.credentials_manager import CredentialsManager
from src.bot.really_big_yugioh_bot import ReallyBigYugiohBot

bot = ReallyBigYugiohBot()

@bot.event
async def on_ready():
	for guild in bot.guilds:
		print(f"Syncing tree for {guild.name} ({guild.id})")
		commands = await bot.tree.sync(guild=guild)
		if len(commands) == 0:
			print("No new commands")
		for command in commands:
			print(f"Updated command {command.name} in {guild.name}")
	print('Bot is ready')

bot.run(CredentialsManager().get_discord_key())