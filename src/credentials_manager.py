import json

DISCORD_API_KEY = 'discord_key'
CHALLONGE_API_KEY = 'challonge_key'
CHALLONGE_USERNAME_KEY = 'challonge_username'
CLOUDINARY_CLOUD_NAME = 'cloudinary_cloud_name'
CLOUDINARY_API_KEY = 'cloudinary_api_key'
CLOUDINARY_API_SECRET = 'cloudinary_api_secret'

class CredentialsManager:
	def __init__(self):
		with open("json/credentials.json", encoding="utf-8") as cred:
			self.credentials = json.load(cred)

	def get_discord_key(self):
		return self.credentials.get(DISCORD_API_KEY)

	def get_challonge_username(self):
		return self.credentials.get(CHALLONGE_USERNAME_KEY)

	def get_challonge_key(self):
		return self.credentials.get(CHALLONGE_API_KEY)

	def get_cloudinary_cloud_name(self):
		return self.credentials.get(CLOUDINARY_CLOUD_NAME)

	def get_cloudinary_key(self):
		return self.credentials.get(CLOUDINARY_API_KEY)

	def get_cloudinary_secret(self):
		return self.credentials.get(CLOUDINARY_API_SECRET)