import json

NAME_KEY = 'name'
DB_NAME_KEY = "db_name"
ID_KEY = 'id'

class Player:
	def __init__(self, username:str, discord_id: int):
		self.username = username
		self.discord_id = discord_id
		self.challonge_id = 0
		self.db_name = ""

	def set_db_name(self, db_name:str):
		self.db_name = db_name

	def to_json(self):
		dictionary = {}
		dictionary[NAME_KEY] = self.username
		dictionary[ID_KEY] = self.discord_id
		dictionary[DB_NAME_KEY] = self.db_name
		return dictionary
	
	def get_challonge_player_id(self):
		return self.challonge_id
	
	def get_username(self):
		return self.username
	
	def get_discord_id(self):
		return self.discord_id


def player_from_json(player_as_json:str) -> Player:
    dictionary = json.load(player_as_json)
    name = dictionary[NAME_KEY]
    player_id = dictionary[ID_KEY]
    db_name = dictionary[DB_NAME_KEY]
    player = Player(name, player_id)
    player.set_db_name(db_name)
    return player