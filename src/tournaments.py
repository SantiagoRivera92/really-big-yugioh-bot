import challonge
from challonge.api import ChallongeException
from src.credentials_manager import CredentialsManager
from src.utils import OperationResult
import os
import json
from typing import List, Union
import src.strings as Strings

foldername = "json/tournaments/%d"
filename = "json/tournaments/%d/tournament.json"

URL_KEY = 'full_challonge_url'
ID_KEY = 'id'
CHALLONGE_PLAYER_ID_KEY = 'challonge_id'
NAME_KEY = 'name'
DB_NAME_KEY = "dbName"
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

def sanitizedTournamentName(tournamentName:str):
	legalCharacters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_"
	sanitizedTournamentName = ""
	for character in tournamentName:
		if character in legalCharacters:
			sanitizedTournamentName = "%s%s" % (sanitizedTournamentName, character)
		else:
			sanitizedTournamentName = "%s_" % (sanitizedTournamentName)
	return sanitizedTournamentName

class Player:
	def __init__(self, username:str, discordId: int):
		self.username = username
		self.discordId = discordId
		self.challongeId = 0
		self.dbName = ""
	
	def setChallongePlayerId(self, challongeId: int):
		self.challongeId = challongeId

	def setDbName(self, dbName:str):
		self.dbName = dbName

	def toJson(self):
		dictionary = {}
		dictionary[NAME_KEY] = self.username
		dictionary[ID_KEY] = self.discordId
		dictionary[CHALLONGE_PLAYER_ID_KEY] = self.challongeId
		dictionary[DB_NAME_KEY] = self.dbName
		return dictionary
	
	def getChallongePlayerId(self):
		return self.challongeId
	
	def getUsername(self):
		return self.username
	
	def getDiscordId(self):
		return self.discordId

def playerFromResponse(playerAsDict:dict):
	username = playerAsDict[NAME_KEY]
	discordId = playerAsDict[ID_KEY]
	player = Player(username, discordId)
	challongeId = playerAsDict[CHALLONGE_PLAYER_ID_KEY]
	player.setChallongePlayerId(challongeId)
	player.setDbName(playerAsDict[DB_NAME_KEY])
	return player

class OpenMatch:

	def __init__(self, playerA:Player, playerB:Player):
		self.playerA = playerA
		self.playerB = playerB

class Tournament:

	def __init__(self, serverId:int):
		self.serverId = serverId
		self.url = None
		self.id = None
		self.name = None
		self.format = None
		self.tournamentIsOpen = None
		self.players : List[Player] = []
		self.tournamentIsOpen = False

	def setUrl(self, url:str):
		self.url = url
		return self

	def getUrl(self):
		return self.url

	def setId(self, id:int):
		self.id = id
		return self
	
	def getId(self):
		return self.id

	def setName(self, name:str):
		self.name=name
		return self

	def setFormat(self, format:str):
		self.format=format
		return self

	def getFormat(self):
		return self.format

	def getName(self):
		return self.name

	def isOpen(self):
		return self.tournamentIsOpen

	def open(self):
		self.tournamentIsOpen = True
		return self
	
	def close(self):
		self.tournamentIsOpen = False
		return self

	def setPlayers(self, playerList : List[Player]):
		self.players = playerList
		return self
	
	def addPlayer(self, playername:str, discordId:int):
		if self.tournamentIsOpen:
			found = False
			for player in self.players:
				if player.discordId == discordId:
					found = True
			if not found:
				player = Player(playername, discordId)
				self.players.append(player)
				self.save()
				return OperationResult(True, Strings.BOT_MESSAGE_JOINED_TOURNAMENT)
		else:
			return OperationResult(False, Strings.ERROR_MESSAGE_SIGNUPS_CLOSED)
		return OperationResult(False, Strings.ERROR_MESSAGE_ALREADY_JOINED_TOURNAMENT)

	def getPlayerForName(self, playername:str) -> Union[Player|None]:
		for player in self.players:
			if player.getUsername() == playername:
				return player
		return None
	
	def getPlayerFromChallongeId(self, challongeId:int):
		for player in self.players:
			if player.getChallongePlayerId() == challongeId:
				return player

	def removePlayer(self, playername:str):
		player = self.getPlayerForName(playername)
		if player != None:
			self.players.remove(player)
			self.save()
			if self.isOpen():
				return OperationResult(True, Strings.BOT_MESSAGE_DROPPED % playername)
			else:
				return OperationResult(False, Strings.BOT_MESSAGE_UNREGISTERED % playername)
		else:
			return OperationResult(False, Strings.ERROR_MESSAGE_CANT_DROP % playername)

	def save(self):
		folder = foldername % self.serverId
		file = filename % self.serverId
		if not os.path.exists(folder):
			os.makedirs(folder)
		with open(file, 'w') as tournamentFile:
			json.dump(self.toJson(), tournamentFile, indent=4)
		return self
		
	def toJson(self):
		dictionary = {}
		dictionary[OPEN_KEY] = self.tournamentIsOpen
		dictionary[NAME_KEY] = self.name
		dictionary[ID_KEY] = self.id
		dictionary[URL_KEY] = self.url
		dictionary[FORMAT_KEY] = self.format
		playersAsDicts = []
		for player in self.players:
			playersAsDicts.append(player.toJson())
		dictionary[PLAYERS_KEY] = playersAsDicts
		return dictionary

def tournamentFromResponse(tournament:dict, serverId:int):
	challongeTournament = Tournament(serverId)
	players : List[Player] = []
	for playerDict in tournament[PLAYERS_KEY]:
		player = Player(playerDict[NAME_KEY], playerDict[ID_KEY])
		player.setChallongePlayerId(playerDict[CHALLONGE_PLAYER_ID_KEY])
		players.append(player)

	challongeTournament.setUrl(tournament[URL_KEY]).setId(tournament[ID_KEY]).setName(tournament[NAME_KEY]).setFormat(tournament[FORMAT_KEY]).setPlayers(players)
	if tournament.get(OPEN_KEY):
		return challongeTournament.open().save()
	else:
		return challongeTournament.close().save()

def getTournamentForServer(serverId:int):
	tournamentFile = filename % serverId
	if os.path.exists(tournamentFile):
		with open(tournamentFile) as file:
			dictionary = json.load(file)
			tournament = tournamentFromResponse(dictionary, serverId)
			return tournament

class TournamentManager:


	def __init__(self, credentials:CredentialsManager, serverId: int):
		dir(challonge)
		challonge.set_credentials(credentials.getChallongeUsername(), credentials.getChallongeApiKey())
		self.serverId = serverId

	def createTournament(self, tournamentName:str, formatName:str, tournament_type:str):
		try:
			params = {
				"pts_for_match_win":3.0,
				"pts_for_match_tie":1.0,
				"pts_for_bye":3.0
			}
			if not tournament_type in VALID_TOURNAMENT_TYPES:
				return OperationResult(False, Strings.ERROR_INVALID_TOURNAMENT_TYPE)
			tournamentDict = challonge.tournaments.create(tournamentName, sanitizedTournamentName(tournamentName), tournament_type, **params)
			tournament = Tournament(self.serverId)
			tournament.setUrl(tournamentDict[URL_KEY]).setId(tournamentDict[ID_KEY]).setName(tournamentName).setFormat(formatName).open().save()
			return OperationResult(True, Strings.BOT_MESSAGE_TOURNAMENT_CREATED % (tournamentName, tournament.getUrl()))
		except ChallongeException as exception:
			return OperationResult(False, str(exception))

	def getTournamentFromChallonge(self):
		tournament = getTournamentForServer(self.serverId)
		params = {
				"include_participants":1,
				"include_matches":1
			}
		response = challonge.tournaments.show(tournament.id, **params)
		participants = response[PARTICIPANTS_KEY]
		players = tournament.players
		for participant in participants:
			participant = participant[PARTICIPANT_KEY]
			playerName = participant[NAME_KEY]
			playerChallongeId = participant[ID_KEY]
			for player in players:
				if playerName == player.username:
					player.setChallongePlayerId(playerChallongeId)
		tournament.save()
		return response

	def getTournamentFormat(self):
		tournament = getTournamentForServer(self.serverId)
		return tournament.getFormat()
		
	def getMatches(self):
		tournament = getTournamentForServer(self.serverId)
		if tournament == None:
			return None
		response = self.getTournamentFromChallonge()
		matches = response[MATCHES_KEY]
		players = tournament.players

		openMatches : List[OpenMatch] = []
		for match in matches:
			match = match[MATCH_KEY]
			if match[STATE_KEY] == OPEN_KEY:
				playerAId = match[PLAYER_1_ID_KEY]
				playerBId = match[PLAYER_2_ID_KEY]
				playerA : Player = None
				playerB : Player = None
				for player in players:
					if (playerA == None or playerB == None):
						if player.challongeId == playerAId:
							playerA = player
						if player.challongeId == playerBId:
							playerB = player
				if (playerA != None and playerB != None):
					openMatches.append(OpenMatch(playerA, playerB))
		tournament.save()
		return openMatches

	def reportLoss(self, playerName:str):
		self.updateChallongeIdsForAllPlayers()
		tournament = getTournamentForServer(self.serverId)
		player = tournament.getPlayerForName(playerName)
		playerId = player.getChallongePlayerId()
		matches = self.get_active_matches()
		for match in matches:
			if match[PLAYER_1_ID_KEY] == playerId or match[PLAYER_2_ID_KEY] == playerId:
				# This is the match
				if match[PLAYER_1_ID_KEY] == playerId:
					winner = match[PLAYER_2_ID_KEY]
				else:
					winner = match[PLAYER_1_ID_KEY]

				winnerAsPlayer = tournament.getPlayerFromChallongeId(winner)
				loserAsPlayer = tournament.getPlayerForName(playerName)
				
				match[WINNER_ID_KEY] = winner
				match[SCORES_CSV_KEY] = "1-0"

				challonge.matches.update(tournament.id, match[ID_KEY], **match)
				newMatches = self.get_active_matches()
    
				return OperationResult(True, self.get_active_matchesAsString(matches, newMatches, tournament, loserAsPlayer, winnerAsPlayer))		

		return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_MATCH % playerName)

	def get_active_matchesAsString(self, matches, newMatches, tournament: Tournament, loser: Player, winner: Player):
		lossText = Strings.BOT_MESSAGE_LOSS_REGISTERED % (loser.getDiscordId(), winner.getDiscordId())
		activeMatches = []

		for newMatch in newMatches:
			found = False
			for oldMatch in matches:
				if oldMatch["id"] == newMatch["id"]:
					found = True
					break
			if not found:
				activeMatches.append(newMatch)
    
		activeMatchesAsText = ""
		if len(activeMatches) > 0:
			activeMatchesAsText = "There are new active matches!\n\n"
			for match in activeMatches:
				player1 = match[PLAYER_1_ID_KEY]
				player2 = match[PLAYER_2_ID_KEY]
				p1 = tournament.getPlayerFromChallongeId(player1)
				p2 = tournament.getPlayerFromChallongeId(player2)
				p1id = p1.discordId
				p2id = p2.discordId
				activeMatchesAsText = activeMatchesAsText + Strings.BOT_MESSAGE_NEW_MATCH % (p1id, p2id) + "\n"
			return lossText + "\n\n" + activeMatchesAsText
		return lossText
		

	def updateChallongeIdsForAllPlayers(self):
		tournament = getTournamentForServer(self.serverId)
		players = challonge.participants.index(tournament.id)
		for player in tournament.players:
			for challongePlayer in players:
				if player.username == challongePlayer['name']:
					player.challongeId = challongePlayer['id']
		tournament.save()

	def registerToTournament(self, playerName: str, playerId: int, path: str) -> OperationResult:
		tournament = getTournamentForServer(self.serverId)
		if tournament == None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		if tournament.isOpen():
			if tournament.getPlayerForName(playerName) == None:
				print("Adding %s to the tournament" % playerName)
				result = tournament.addPlayer(playerName, playerId)
				challonge.participants.create(tournament.id, playerName)
				return result
			else:
				return OperationResult(False, Strings.ERROR_MESSAGE_PLAYER_ALREADY_JOINED)
		else:
			return OperationResult(False, Strings.ERROR_MESSAGE_TOURNAMENT_ALREADY_STARTED)

	def drop(self, playerName:str):
		tournament = getTournamentForServer(self.serverId)
		if tournament == None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		print("Removing %s from the tournament" % playerName)
		participants = challonge.participants.index(tournament.id)
		activeMatches = self.get_active_matches()
		player = tournament.getPlayerForName(playerName)
		found = False
		if (player != None):
			for match in activeMatches:
				if match[PLAYER_1_ID_KEY] == player.challongeId:
					found = True
					continue
				if match[PLAYER_2_ID_KEY] == player.challongeId:
					found = True
					continue
			if found:
				self.reportLoss(playerName)
				newActiveMatches = self.get_active_matches()
				text = self.get_active_matchesAsString(activeMatches, newActiveMatches, tournament, player, self.getWinnerFromLoser(player))
			
		for participant in participants:
			if (participant['name'] == playerName):
				playerId = participant['id']
				challonge.participants.destroy(tournament.id,playerId)

		result = tournament.removePlayer(playerName)

		if found:
			result.message = result.message + text
			
		return result

	def getTournamentInfo(self):
		tournament = getTournamentForServer(self.serverId)
		if tournament == None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		return OperationResult(True, tournament.getUrl())

	def startTournament(self):
		tournament = getTournamentForServer(self.serverId)
		if tournament == None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		if tournament.isOpen():
			tournament.close().save()
			challonge.participants.randomize(str(tournament.getId()))
			challonge.tournaments.start(str(tournament.getId()))
			return OperationResult(True, Strings.BOT_MESSAGE_TOURNAMENT_STARTED % tournament.getUrl())
		else:
			return OperationResult(False, Strings.ERROR_MESSAGE_TOURNAMENT_ALREADY_STARTED)

	def endTournament(self):
		tournament = getTournamentForServer(self.serverId)
		if tournament == None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		if tournament.isOpen():
			return OperationResult(False, Strings.ERROR_MESSAGE_TOURNAMENT_HAS_NOT_STARTED)
		challonge.tournaments.finalize(str(tournament.getId()))
		return OperationResult(True, Strings.BOT_MESSAGE_TOURNAMENT_ENDED % tournament.getUrl())

	def get_active_matches(self) -> List:
		tournament = self.getTournamentForServer()
		params = {
				"state":"open"
			}
		matches = challonge.matches.index(tournament.getId(), **params)
		return matches

	def getWinnerFromLoser(self, player_name:str):
		tournament = getTournamentForServer(self.serverId)
		player = tournament.getPlayerForName(player_name)
		if (player != None):
			playerId = player.getChallongePlayerId()
			matches = self.get_active_matches()
			for match in matches:
				if match[PLAYER_1_ID_KEY] == playerId:
					return tournament.getPlayerFromChallongeId(match[PLAYER_2_ID_KEY])
				if match[PLAYER_2_ID_KEY] == playerId:
					return tournament.getPlayerFromChallongeId(match[PLAYER_1_ID_KEY])
		print(matches)
		print("Couldn't find a match for %s" % player_name)
				

	def getReadableActiveMatches(self):
		tournament = self.getTournamentForServer()
		if tournament == None:
			return OperationResult(False, Strings.ERROR_MESSAGE_NO_ACTIVE_TOURNAMENT)
		if not tournament.isOpen():
			return OperationResult(False, Strings.ERROR_MESSAGE_TOURNAMENT_HAS_NOT_STARTED)
		matches = self.get_active_matches()
		if len(matches) == 0:
			return OperationResult(False, Strings.BOT_MESSAGE_TOURNAMENT_ENDED % tournament.getUrl())
		activeMatches = "Active Matches:\n"
		for match in matches:
			player1 = match[PLAYER_1_ID_KEY]
			player2 = match[PLAYER_2_ID_KEY]
			p1 = tournament.getPlayerFromChallongeId(player1)
			p2 = tournament.getPlayerFromChallongeId(player2)
			activeMatches = activeMatches + "\n<@%d> vs <@%d>" % (p1.discordId, p2.discordId)
		return OperationResult(True, activeMatches)

	def setDbName(self, playername:str, dbname:str):
		tournament = self.getTournamentForServer()
		player = tournament.getPlayerForName(playername)
		if (player == None):
			return OperationResult(False, "You aren't registered for the tournament")
		player.setDbName(dbname)
		tournament.save()
		return OperationResult(True, "Your Duelingbook name was updated to: %s"%dbname)

	def getDbName(self, playername:str):
		tournament = self.getTournamentForServer()
		player = tournament.getPlayerForName(playername)
		if (player == None):
			return OperationResult(False, "%s isn't registered for the tournament" % playername)
		if (player.dbName == ""):
			return OperationResult(False, "%s hasn't set their Duelingbook username" % playername)
		return OperationResult(True, player.dbName)

	def cleardecks(self):
		tournament = self.getTournamentForServer()
		if not tournament == None:
			tournament.cleardecks()

	def getTournamentForServer(self):
		return getTournamentForServer(self.serverId)

	def getTournamentPlayers(self):
		tournament = self.getTournamentForServer()
		return tournament.players

	def getChallongePlayers(self):
		tournament = self.getTournamentForServer()
		participants = challonge.participants.index(tournament.id)
		playerList: List[str] = []
		for participant in participants:
			playerList.append(participant['name'])
		return playerList