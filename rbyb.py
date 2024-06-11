import sys
sys.dont_write_bytecode = True

from src.credentials_manager import CredentialsManager
from src.bot.really_big_yugioh_bot import ReallyBigYugiohBot

bot = ReallyBigYugiohBot()

@bot.event
async def on_ready():
	print('Bot is ready')

bot.run(CredentialsManager().get_discord_key())