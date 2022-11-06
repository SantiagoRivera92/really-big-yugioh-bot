import json

discordApiKey = 'discord_key'

class CredentialsManager:
	def __init__(self, credentialsFile):
		with open(credentialsFile) as cred:
			self.credentials = json.load(cred)

	def getDiscordAPIKey(self):
		return self.credentials.get(discordApiKey)