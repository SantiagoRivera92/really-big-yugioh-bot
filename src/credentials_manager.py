import json

discordApiKey = 'discord_key'
challongeApiKey = 'challonge_key'
challongeUsername = 'challonge_username'

class CredentialsManager:
	def __init__(self, credentialsFile):
		with open(credentialsFile) as cred:
			self.credentials = json.load(cred)

	def getDiscordAPIKey(self):
		return self.credentials.get(discordApiKey)
	
	def getChallongeAPIKey(self):
		return self.credentials.get(challongeApiKey)

	def getChallongeUsername(self):
		return self.credentials.get(challongeUsername)