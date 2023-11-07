
import os
import json
from typing import List, Union
import challonge
from challonge.api import ChallongeException
from src.credentials_manager import CredentialsManager
from src.utils.utils import OperationResult
import src.strings as Strings

FOLDER_NAME = "json/tournaments/%d"
FILE_NAME = "json/tournaments/%d/tournament.json"

URL_KEY = 'full_challonge_url'
ID_KEY = 'id'
CHALLONGE_PLAYER_ID_KEY = 'challonge_id'
NAME_KEY = 'name'
DB_NAME_KEY = "db_name"
PLAYERS_KEY = 'players'
OPEN_KEY = 'open'
STATE_KEY = 'state'
FORMAT_KEY = 'format'

MATCHES_KEY = 'matches'
MATCH_KEY = 'match'
PLAYER_1_ID_KEY = 'player1_id'
PLAYER_2_ID_KEY = 'player2_id'
WINNER_ID_KEY = 'winner_id'
SCORES_CSV_KEY = 'scores_csv'
PARTICIPANT_KEY = 'participant'
PARTICIPANTS_KEY = 'participants'

VALID_TOURNAMENT_TYPES = ["swiss", "double elimination", "single elimination", "round robin"]

def sanitized_tournament_name(tournament_name:str):
	legal_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_.-"
	sanitized_name = ""
	for character in tournament_name:
		if character in legal_characters:
			sanitized_name = f"{sanitized_tournament_name}{character}"
		else:
			sanitized_name = f"{sanitized_tournament_name}_"
	return sanitized_name

class Player:
	def __init__(self, username:str, discord_id: int):
		self.username = username
		self.discord_id = discord_id
		self.challonge_id = 0
		self.db_name = ""
	
	def set_challonge_player_id(self, challonge_id: int):
		self.challonge_id = challonge_id

	def set_db_name(self, db_name:str):
		self.db_name = db_name

	def to_json(self):
		dictionary = {}
		dictionary[NAME_KEY] = self.username
		dictionary[ID_KEY] = self.discord_id
		dictionary[CHALLONGE_PLAYER_ID_KEY] = self.challonge_id
		dictionary[DB_NAME_KEY] = self.db_name
		return dictionary
	
	def get_challonge_player_id(self):
		return self.challonge_id
	
	def get_username(self):
		return self.username
	
	def get_discord_id(self):
		return self.discord_id

class OpenMatch:

	def __init__(self, player_1:Player, player_2:Player):
		self.player_1 = player_1
		self.player_2 = player_2

class Tournament:

	def __init__(self, server_id:int):
		self.server_id = server_id
		self.url = None
		self.id = None
		self.name = None
		self.format = None
		self.tournament_is_open = None
		self.players : List[Player] = []
		self.tournament_is_open = False

	def set_url(self, url:str):
		self.url = url
		return self

	def get_url(self):
		return self.url

	def set_id(self, _id:int):
		self.id = _id
		return self
	
	def get_id(self):
		return self.id

	def set_name(self, name:str):
		self.name=name
		return self

	def set_format(self, _format:str):
		self.format=_format
		return self

	def get_format(self):
		return self.format

	def get_name(self):
		return self.name

	def is_open(self):
		return self.tournament_is_open

	def open(self):
		self.tournament_is_open = True
		return self
	
	def close(self):
		self.tournament_is_open = False
		return self

	def set_players(self, player_list : List[Player]):
		self.players = player_list
		return self
	
	def add_player(self, playername:str, discord_id:int):
		if self.tournament_is_open:
			found = False
			for player in self.players:
				if player.discord_id == discord_id:
					found = True
			if not found:
				player = Player(playername, discord_id)
				self.players.append(player)
				self.save()
				return OperationResult(True, Strings.BOT_MESSAGE_JOINED_TOURNAMENT)
		else:
			return OperationResult(False, Strings.ERROR_MESSAGE_SIGNUPS_CLOSED)
		return OperationResult(False, Strings.ERROR_MESSAGE_ALREADY_JOINED_TOURNAMENT)

	def get_player_for_name(self, playername:str) -> Union[Player|None]:
		for player in self.players:
			if player.get_username() == playername:
				return player
		return None
	
	def get_player_from_challonge_id(self, challonge_id:int) -> Union[Player|None]:
		for player in self.players:
			if player.get_challonge_player_id() == challonge_id:
				return player
		return None

	def remove_player(self, playername:str):
		player = self.get_player_for_name(playername)
		if player is not None:
			self.players.remove(player)
			self.save()
			if self.is_open():
				return OperationResult(True, Strings.BOT_MESSAGE_DROPPED % playername)
			return OperationResult(False, Strings.BOT_MESSAGE_UNREGISTERED % playername)
		return OperationResult(False, Strings.ERROR_MESSAGE_CANT_DROP % playername)

	def save(self):
		folder = FOLDER_NAME % self.server_id
		file = FILE_NAME % self.server_id
		if not os.path.exists(folder):
			os.makedirs(folder)
		with open(file, 'w', encoding="utf-8") as tournament_file:
			json.dump(self.to_json(), tournament_file, indent=4)
		return self
		
	def to_json(self):
		dictionary = {}
		dictionary[OPEN_KEY] = self.tournament_is_open
		dictionary[NAME_KEY] = self.name
		dictionary[ID_KEY] = self.id
		dictionary[URL_KEY] = self.url
		dictionary[FORMAT_KEY] = self.format
		players_as_dicts = []
		for player in self.players:
			players_as_dicts.append(player.to_json())
		dictionary[PLAYERS_KEY] = players_as_dicts
		return dictionary

def tournament_from_response(tournament:dict, server_id:int):
	challonge_tournament = Tournament(server_id)
	players : List[Player] = []
	for player_dict in tournament[PLAYERS_KEY]:
		player = Player(player_dict[NAME_KEY], player_dict[ID_KEY])
		player.set_challonge_player_id(player_dict[CHALLONGE_PLAYER_ID_KEY])
		players.append(player)

	challonge_tournament.set_url(tournament[URL_KEY]).set_id(tournament[ID_KEY]).set_name(tournament[NAME_KEY]).set_format(tournament[FORMAT_KEY]).set_players(players)
	if tournament.get(OPEN_KEY):
		return challonge_tournament.open().save()
	return challonge_tournament.close().save()

def get_tournament_for_server(server_id:int) -> Union[Tournament | None]:
	tournament_file = FILE_NAME % server_id
	if os.path.exists(tournament_file):
		with open(tournament_file, encoding="utf-8") as file:
			dictionary = json.load(file)
			tournament = tournament_from_response(dictionary, server_id)
			return tournament
	return None

class TournamentManager:


	def __init__(self, credentials:CredentialsManager, server_id: int):
		dir(challonge)
		challonge.set_credentials(credentials.get_challonge_username(), credentials.get_challonge_key())
		self.server_id = server_id

	def create_tournament(self, tournament_name:str, format_name:str, tournament_type:str):
		try:
			params = {
				"pts_for_match_win":3.0,
				"pts_for_match_tie":1.0,
				"pts_for_bye":3.0
			}
			if not tournament_type in VALID_TOURNAMENT_TYPES:
				return OperationResult(False, Strings.ERROR_INVALID_TOURNAMENT_TYPE)
			tournament_dict = challonge.tournaments.create(tournament_name, sanitized_tournament_name(tournament_name), tournament_type, **params)
			tournament = Tournament(self.server_id)
			tournament.set_url(tournament_dict[URL_KEY]).set_id(tournament_dict[ID_KEY]).set_name(tournament_name).set_format(format_name).open().save()
			return OperationResult(True, Strings.BOT_MESSAGE_TOURNAMENT_CREATED % (tournament_name, tournament.get_url()))
		except ChallongeException as exception:
			return OperationResult(False, str(exception))

	def get_tournament_from_challonge(self):
		tournament = get_tournament_for_server(self.server_id)
		params = {
				"include_participants":1,
				"include_matches":1
			}
		response = challonge.tournaments.show(tournament.id, **params)
		participants = response[PARTICIPANTS_KEY]
		players = tournament.players
		for participant in participants:
			participant = participant[PARTICIPANT_KEY]
			player_name = participant[NAME_KEY]
			player_challonge_id = participant[ID_KEY]
			for player in players:
				if player_name == player.username:
					player.set_challonge_player_id(player_challonge_id)
		tournament.save()
		return response

	def get_tournament_format(self):
		tournament = get_tournament_for_server(self.server_id)
		return tournament.get_format()
		
	def get_matches(self):
		tournament = get_tournament_for_server(self.server_id)
		if tournament is None:
			return None
		response = self.get_tournament_from_challonge()
		matches = response[MATCHES_KEY]
		players = tournament.players

		open_matches : List[OpenMatch] = []
		for match in matches:
			match = match[MATCH_KEY]
			if match[STATE_KEY] == OPEN_KEY:
				player_1_id = match[PLAYER_1_ID_KEY]
				player_2_id = match[PLAYER_2_ID_KEY]
				player_1 : Player = None
				player_2 : Player = None
				for player in players:
					if (player_1 is None or player_2 is None):
						if player.challonge_id == player_1_id:
							player_1 = player
						if player.challonge_id == player_2_id:
							player_2 = player
				if (player_1 is not None and player_2 is not None):
					open_matches.append(OpenMatch(player_1, player_2))
		tournament.save()
		return open_matches

	def report_loss(self, player_name:str):
		self.update_challonge_id_for_all_players()
		tournament = get_tournament_for_server(self.server_id)
		player = tournament.get_player_for_name(player_name)
		player_id = player.get_challonge_player_id()
		matches = self.get_active_matches()
		for match in matches:
			if match[PLAYER_1_ID_KEY] == player_id or match[PLAYER_2_ID_KEY] == player_id:
				# This is the match
				if match[PLAYER_1_ID_KEY] == player_id:
					winner = match[PLAYER_2_ID_KEY]
				else:
					winner = match[PLAYER_1_ID_KEY]

				winner_as_player = tournament.get_player_from_challonge_id(winner)
				loser_as_player = tournament.get_player_for_name(player_name)
				
				match[WINNER_ID_KEY] = winner
				match[SCORES_CSV_KEY] = "1-0"

				challonge.matches.update(tournament.id, match[ID_KEY], **match)
				new_matches = self.get_active_matches()
    
				return OperationResult(True, self.get_active_matches_as_string(matches, new_matches, tournament, loser_as_player, winner_as_player))		

		return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_MATCH % player_name)

	def get_active_matches_as_string(self, matches, new_matches, tournament: Tournament, loser: Player, winner: Player):
		loss_text = Strings.BOT_MESSAGE_LOSS_REGISTERED % (loser.get_discord_id(), winner.get_discord_id())
		active_matches = []

		for new_match in new_matches:
			found = False
			for old_match in matches:
				if old_match["id"] == new_match["id"]:
					found = True
					break
			if not found:
				active_matches.append(new_match)
    
		active_matches_as_text = ""
		if len(active_matches) > 0:
			active_matches_as_text = "There are new active matches!\n\n"
			for match in active_matches:
				player1 = match[PLAYER_1_ID_KEY]
				player2 = match[PLAYER_2_ID_KEY]
				p1 = tournament.get_player_from_challonge_id(player1)
				p2 = tournament.get_player_from_challonge_id(player2)
				p1id = p1.discord_id
				p2id = p2.discord_id
				active_matches_as_text = active_matches_as_text + Strings.BOT_MESSAGE_NEW_MATCH % (p1id, p2id) + "\n"
			return loss_text + "\n\n" + active_matches_as_text
		return loss_text
		

	def update_challonge_id_for_all_players(self):
		tournament = get_tournament_for_server(self.server_id)
		players = challonge.participants.index(tournament.id)
		for player in tournament.players:
			for challonge_player in players:
				if player.username == challonge_player['name']:
					player.challonge_id = challonge_player['id']
		tournament.save()

	def register_to_tournament(self, player_name: str, player_id: int, path: str) -> OperationResult:
		tournament = get_tournament_for_server(self.server_id)
		if tournament is None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		if tournament.is_open():
			if tournament.get_player_for_name(player_name) is None:
				print(f"Adding {player_name} to the tournament")
				result = tournament.add_player(player_name, player_id)
				challonge.participants.create(tournament.id, player_name)
				return result
			return OperationResult(False, Strings.ERROR_MESSAGE_PLAYER_ALREADY_JOINED)
		return OperationResult(False, Strings.ERROR_MESSAGE_TOURNAMENT_ALREADY_STARTED)

	def drop(self, player_name:str):
		tournament = get_tournament_for_server(self.server_id)
		if tournament is None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		print(f"Removing {player_name} from the tournament")
		participants = challonge.participants.index(tournament.id)
		active_matches = self.get_active_matches()
		player = tournament.get_player_for_name(player_name)
		found = False
		if player is not None:
			for match in active_matches:
				if match[PLAYER_1_ID_KEY] == player.challonge_id:
					found = True
					continue
				if match[PLAYER_2_ID_KEY] == player.challonge_id:
					found = True
					continue
			if found:
				self.report_loss(player_name)
				new_active_matches = self.get_active_matches()
				text = self.get_active_matches_as_string(active_matches, new_active_matches, tournament, player, self.get_winner_from_loser(player))
			
		for participant in participants:
			if participant['name'] == player_name:
				player_id = participant['id']
				challonge.participants.destroy(tournament.id,player_id)

		result = tournament.remove_player(player_name)

		if found:
			result.message = result.message + text
			
		return result

	def get_tournament_info(self):
		tournament = get_tournament_for_server(self.server_id)
		if tournament is None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		return OperationResult(True, tournament.get_url())

	def start_tournament(self):
		tournament = get_tournament_for_server(self.server_id)
		if tournament is None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		if tournament.is_open():
			tournament.close().save()
			challonge.participants.randomize(str(tournament.get_id()))
			challonge.tournaments.start(str(tournament.get_id()))
			return OperationResult(True, Strings.BOT_MESSAGE_TOURNAMENT_STARTED % tournament.get_url())
		
		return OperationResult(False, Strings.ERROR_MESSAGE_TOURNAMENT_ALREADY_STARTED)

	def end_tournament(self):
		tournament = get_tournament_for_server(self.server_id)
		if tournament is None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		if tournament.is_open():
			return OperationResult(False, Strings.ERROR_MESSAGE_TOURNAMENT_HAS_NOT_STARTED)
		challonge.tournaments.finalize(str(tournament.get_id()))
		return OperationResult(True, Strings.BOT_MESSAGE_TOURNAMENT_ENDED % tournament.get_url())

	def get_active_matches(self) -> List:
		tournament = self.get_tournament_for_server()
		params = {
				"state":"open"
			}
		matches = challonge.matches.index(tournament.get_id(), **params)
		return matches

	def get_winner_from_loser(self, player_name:str) -> Union[Player | None]:
		tournament = get_tournament_for_server(self.server_id)
		player = tournament.get_player_for_name(player_name)
		if player is not None:
			player_id = player.get_challonge_player_id()
			matches = self.get_active_matches()
			for match in matches:
				if match[PLAYER_1_ID_KEY] == player_id:
					return tournament.get_player_from_challonge_id(match[PLAYER_2_ID_KEY])
				if match[PLAYER_2_ID_KEY] == player_id:
					return tournament.get_player_from_challonge_id(match[PLAYER_1_ID_KEY])
		print(matches)
		print(f"Couldn't find a match for {player_name}")
		return None
				

	def get_readable_active_matches(self):
		tournament = self.get_tournament_for_server()
		if tournament is None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		if not tournament.is_open():
			return OperationResult(False, Strings.ERROR_MESSAGE_TOURNAMENT_HAS_NOT_STARTED)
		matches = self.get_active_matches()
		if len(matches) == 0:
			return OperationResult(False, Strings.BOT_MESSAGE_TOURNAMENT_ENDED % tournament.get_url())
		active_matches = "Active Matches:\n"
		for match in matches:
			player1 = match[PLAYER_1_ID_KEY]
			player2 = match[PLAYER_2_ID_KEY]
			p1 = tournament.get_player_from_challonge_id(player1)
			p2 = tournament.get_player_from_challonge_id(player2)
			active_matches = f"{active_matches}\n<@{p1.discord_id}> vs <@{p2.discord_id}>"
		return OperationResult(True, active_matches)

	def set_db_name(self, playername:str, db_name:str):
		tournament = self.get_tournament_for_server()
		player = tournament.get_player_for_name(playername)
		if player is None:
			return OperationResult(False, "You aren't registered for the tournament")
		player.set_db_name(db_name)
		tournament.save()
		return OperationResult(True, f"Your Duelingbook name was updated to {db_name}")

	def get_db_name(self, playername:str):
		tournament = self.get_tournament_for_server()
		player = tournament.get_player_for_name(playername)
		if player is None:
			return OperationResult(False, f"{playername} isn't registered for the tournament")
		if player.db_name == "":
			return OperationResult(False, f"{playername} hasn't set their Duelingbook username")
		return OperationResult(True, player.db_name)

	def get_tournament_for_server(self):
		return get_tournament_for_server(self.server_id)

	def get_tournament_players(self):
		tournament = self.get_tournament_for_server()
		return tournament.players

	def get_challonge_players(self):
		tournament = self.get_tournament_for_server()
		participants = challonge.participants.index(tournament.id)
		player_list: List[str] = []
		for participant in participants:
			player_list.append(participant['name'])
		return player_list