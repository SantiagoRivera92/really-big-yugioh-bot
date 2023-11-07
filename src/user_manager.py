import os
import json
from typing import List

USERNAME_KEY = "discord_name"
DUELINGBOOK_NAME_KEY = "duelingbook_name"

def user_from_json(user:dict):
	user_name = user[USERNAME_KEY]
	db_name = user[DUELINGBOOK_NAME_KEY]
	return User(user_name, db_name)

class User:
	def __init__(self, user_name:str, db_name:str):
		self.user_name = user_name
		self.db_name = db_name

	def to_json(self):
		user = {}
		user[USERNAME_KEY] = self.user_name
		user[DUELINGBOOK_NAME_KEY] = self.db_name
		return user


class Users:

	def __init__(self, server_id:int):
		self.folder_name = f"json/users/{server_id}"
		self.file_name = f"json/users/{server_id}/users.json"

		self.users : List[User] = []

		if not os.path.exists(self.folder_name):
			os.makedirs(self.folder_name)
		if not os.path.exists(self.file_name):
			self.save()
		
		with open(self.file_name, encoding="utf-8") as users_file:
			raw_users = json.load(users_file)
			for user in raw_users:
				self.users.append(user_from_json(user))

	def save(self):
		with open(self.file_name, 'w', encoding="utf-8") as users_file:
			json.dump(self.to_json(), users_file, indent=4)

	def to_json(self):
		players_as_json = []
		for player in self.users:
			players_as_json.append(player.to_json())
		return players_as_json

	def get_user_from_username(self, user_name:str):
		for user in self.users:
			if user.user_name == user_name:
				return user

		return None

	def set_db_username(self, user_name:str, db_name:str):
		user = self.get_user_from_username(user_name)
		if user is not None:
			user.db_name = db_name
		else:
			user = User(user_name, db_name)
			self.users.append(user)
		self.save()

	def get_db_username(self, user_name:str):
		user = self.get_user_from_username(user_name)
		if user is None:
			return None
		return user.db_name

	def get_partial_username_matches(self, current:str):
		partial_matches : List[str] = []
		for user in self.users:
			if current.lower() in user.user_name.lower():
				partial_matches.append(user.user_name)
		return partial_matches
		

class UserManager:

	def __init__(self, server_id:int):
		self.users = Users(server_id)
	
	def get_db_username(self, user_name:str):
		return self.users.get_db_username(user_name)

	def set_db_username(self, user_name:str, db_name:str):
		self.users.set_db_username(user_name, db_name)

	def get_partial_username_matches(self, current:str):
		return self.users.get_partial_username_matches(current)
