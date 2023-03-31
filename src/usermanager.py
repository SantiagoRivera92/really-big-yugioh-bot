import os
import json
from typing import List

USERNAME_KEY = "discord_name"
DUELINGBOOK_NAME_KEY = "duelingbook_name"

def userFromJson(user:dict):
	username = user[USERNAME_KEY]
	dbname = user[DUELINGBOOK_NAME_KEY]
	return User(username, dbname)



class User:
	def __init__(self, username:str, dbname:str):
		self.username = username
		self.dbname = dbname

	def toJson(self):
		user = {}
		user[USERNAME_KEY] = self.username
		user[DUELINGBOOK_NAME_KEY] = self.dbname
		return user


class Users:

	def __init__(self, serverId:int):
		self.folderName = "json/users/%d" % serverId
		self.fileName = "json/users/%d/users.json" % serverId

		self.users : List[User] = []

		if not os.path.exists(self.folderName):
			os.makedirs(self.folderName)
		if not os.path.exists(self.fileName):
			self.save()
		
		with open(self.fileName) as usersFile:
			rawUsers = json.load(usersFile)
			for user in rawUsers:
				self.users.append(userFromJson(user))

	def save(self):
		with open(self.fileName, 'w') as usersFile:
			json.dump(self.toJson(), usersFile, indent=4)

	def toJson(self):
		playersAsJson = []
		for player in self.users:
			playersAsJson.append(player.toJson())
		return playersAsJson

	def getUserFromUsername(self, username:str):
		for user in self.users:
			if user.username == username:
				return user

		return None

	def setDBUsername(self, username:str, dbName:str):
		user = self.getUserFromUsername(username)
		if user != None:
			user.dbname = dbName
		else:
			user = User(username, dbName)
			self.users.append(user)
		self.save()

	def getDBUsername(self, username:str):
		user = self.getUserFromUsername(username)
		if user == None:
			return None
		return user.dbname

	def getPartialUsernameMatches(self, current:str):
		partialMatches : List[str] = []
		for user in self.users:
			if current.lower() in user.username.lower():
				partialMatches.append(user.username)
		return partialMatches
		

class UserManager:

	def __init__(self, serverId:int):
		self.users = Users(serverId)
	
	def getDBUsername(self, username:str):
		return self.users.getDBUsername(username)

	def setDBUsername(self, username:str, dbName:str):
		self.users.setDBUsername(username, dbName)

	def getPartialUsernameMatches(self, current:str):
		return self.users.getPartialUsernameMatches(current)
