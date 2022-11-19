import json
import urllib.request

DISCORD_API_KEY = 'discord_key'
ADVANCED_BANLIST_KEY = 'advanced_banlist'
CHALLONGE_API_KEY = 'challonge_key'
CHALLONGE_USERNAME_KEY = 'challonge_username'

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
			  'AppleWebKit/537.11 (KHTML, like Gecko) '
							'Chrome/23.0.1271.64 Safari/537.11',
							'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
							'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
							'Accept-Encoding': 'none',
							'Accept-Language': 'en-US,en;q=0.8',
							'Connection': 'keep-alive'}

class CredentialsManager:
	def __init__(self, credentialsFile):
		with open(credentialsFile) as cred:
			self.credentials = json.load(cred)

	def getDiscordAPIKey(self):
		return self.credentials.get(DISCORD_API_KEY)
	
	def getAdvancedBanlistUrl(self):
		return self.credentials.get(ADVANCED_BANLIST_KEY)

	def getDecodedAdvancedBanlist(self):
		url = self.getAdvancedBanlistUrl()
		request = urllib.request.Request(url, None, header)
		with urllib.request.urlopen(request) as url:
			return url.read().decode()

	def getChallongeUsername(self):
		return self.credentials.get(CHALLONGE_USERNAME_KEY)

	def getChallongeApiKey(self):
		return self.credentials.get(CHALLONGE_API_KEY)