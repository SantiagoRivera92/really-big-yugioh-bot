import challonge
from challonge.api import ChallongeException
from src.utils import OperationResult
import os
import json
from typing import List

foldername = "json/tournaments/%d"
filename = "json/tournaments/%d/tournament.json"

URL_KEY = 'full_challonge_url'
ID_KEY = 'id'
NAME_KEY = 'name'
PLAYERS_KEY = 'players'
OPEN_KEY = 'open'


def sanitizedTournamentName(tournamentName:str):
    legalCharacters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_"
    sanitizedTournamentName = ""
    for character in tournamentName:
        if character in legalCharacters:
            sanitizedTournamentName = "%s%s" % (sanitizedTournamentName, character)
        else:
            sanitizedTournamentName = "%s_" % (sanitizedTournamentName)
    return sanitizedTournamentName

def tournamentFromResponse(tournament:dict, serverId:int):
    challongeTournament = Tournament(serverId)

    challongeTournament.setUrl(tournament[URL_KEY]).setId(tournament[ID_KEY]).setName(tournament[NAME_KEY]).setPlayers(tournament[PLAYERS_KEY])
    if tournament.get(OPEN_KEY):
        return challongeTournament.open()
    else:
        return challongeTournament.close()

def getTournamentForServer(serverId:int):
    tournamentFile = filename % serverId
    if os.path.exists(tournamentFile):
        with open(tournamentFile) as file:
            dict = json.load(file)
            tournament = tournamentFromResponse(dict, serverId)
            return tournament


class Tournament:

    def __init__(self, serverId:int):
        self.serverId = serverId
        self.url = None
        self.id = None
        self.name = None
        self.tournamentIsOpen = None
        self.players = []
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

    def setPlayers(self, playerList:List[str]):
        self.players = playerList
        return self
    
    def addPlayer(self, playername:str):
        if self.tournamentIsOpen:
            if not playername in self.players:
                self.players.append(playername)
                self.save()
                return OperationResult(True, "You have registered to the tournament!")
        else:
            return OperationResult(False, "Sign ups for the tournament are closed")
        return OperationResult(False, "You were already registered to the tournament")

    def removePlayer(self, playername:str):
        if playername in self.players:
            self.players.remove(playername)
            self.save()
            if self.isOpen():
                return OperationResult(True, "You have dropped from the tournament. Better luck next time!")
            else:
                return OperationResult(False, "You have unregistered from the tournament.")
        else:
            return OperationResult(False, "You weren't registered for this tournament")

    def save(self):
        folder = foldername % self.serverId
        file = filename % self.serverId
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(file, 'w') as tournamentFile:
            json.dump(self.toJson(), tournamentFile, indent=4)
        return self
        
    def toJson(self):
        dict = {}
        dict[OPEN_KEY] = self.tournamentIsOpen
        dict[NAME_KEY] = self.name
        dict[ID_KEY] = self.id
        dict[URL_KEY] = self.url
        dict[PLAYERS_KEY] = self.players
        return dict
            

class TournamentManager:
    def __init__(self, challongeUsername:str, apiKey:str, serverId: int):
        challonge.set_credentials(challongeUsername, apiKey)
        self.serverId = serverId

    def createTournament(self, tournamentName:str):
        try:
            params = {
                "pts_for_match_win":3.0,
                "pts_for_match_tie":1.0,
                "pts_for_bye":3.0
            }
            tournamentDict = challonge.tournaments.create(tournamentName, sanitizedTournamentName(tournamentName), "swiss", **params)
            tournament = Tournament(self.serverId)
            tournament.setUrl(tournamentDict[URL_KEY]).setId(tournamentDict[ID_KEY]).setName(tournamentName).open().save()
            return OperationResult(True, "Your tournament \"%s\" was created! You can find it at %s" % (tournamentName, tournament.getUrl()))
        except ChallongeException as exception:
            return OperationResult(False, str(exception))

    def registerToTournament(self, playerName: str):
        tournament = getTournamentForServer(self.serverId)
        if tournament == None:
            return OperationResult(False, "There is no ongoing tournament in this server")
        if tournament.isOpen():
            challonge.participants.create(tournament.id, playerName)
        return tournament.addPlayer(playerName)

    def drop(self, playerName:str):
        tournament = getTournamentForServer(self.serverId)
        if tournament == None:
            return OperationResult(False, "There is no ongoing tournament in this server")
        challonge.participants.destroy(tournament.id, playerName)
        return tournament.removePlayer(playerName)

    def startTournament(self):
        tournament = getTournamentForServer(self.serverId)
        if tournament == None:
            return OperationResult(False, "There is no ongoing tournament in this server")
        if tournament.isOpen():
            tournament.close()
            challonge.tournaments.start(str(tournament.getId()))
            return OperationResult(True, "Tournament has started! You can check round 1 in %s" % tournament.url)
        else:
            return OperationResult(False, "Tournament had already started.")

    def addMockPlayers(self):
        for i in range(0, 20):
            self.registerToTournament("player %d" % i)


    def getTournamentStatus(self, tournamentName:str):
        try:
            params = {
                "include_participants":1,
                "include_matches":1
            }
            tournamentDict = challonge.tournaments.show(sanitizedTournamentName(tournamentName), **params)
            print(tournamentDict)
            return OperationResult(True, "")
        except ChallongeException as exception:
            return OperationResult(False, str(exception))

    def getTournamentForServer(self, serverId:int):
        return getTournamentForServer(serverId)
        
