import json
import urllib.request

DISCORD_API_KEY = 'discord_key'
ADVANCED_BANLIST_KEY = 'advanced_banlist'
CHALLONGE_API_KEY = 'challonge_key'
CHALLONGE_USERNAME_KEY = 'challonge_username'
GOOGLE_DRIVE_FOLDER = 'google_drive_folder'
CLOUDINARY_CLOUD_NAME = 'cloudinary_cloud_name'
CLOUDINARY_API_KEY = 'cloudinary_api_key'
CLOUDINARY_API_SECRET = 'cloudinary_api_secret'


header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
			  'AppleWebKit/537.11 (KHTML, like Gecko) '
							'Chrome/23.0.1271.64 Safari/537.11',
							'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
							'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
							'Accept-Encoding': 'none',
							'Accept-Language': 'en-US,en;q=0.8',
							'Connection': 'keep-alive'}

class CredentialsManager:
	def __init__(self):
		with open("json/credentials.json") as cred:
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

	def getGoogleDriveFolder(self):
		return self.credentials.get(GOOGLE_DRIVE_FOLDER)

	def getCloudinaryCloudName(self):
		return self.credentials.get(CLOUDINARY_CLOUD_NAME)

	def getCloudinaryApiKey(self):
		return self.credentials.get(CLOUDINARY_API_KEY)

	def getCloudinaryApiSecret(self):
		return self.credentials.get(CLOUDINARY_API_SECRET)