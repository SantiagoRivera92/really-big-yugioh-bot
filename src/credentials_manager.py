import json

DISCORD_API_KEY = 'discord_key'

class CredentialsManager:
	def __init__(self, credentialsFile):
		with open(credentialsFile) as cred:
			self.credentials = json.load(cred)

	def getDiscordAPIKey(self):
		return self.credentials.get(DISCORD_API_KEY)