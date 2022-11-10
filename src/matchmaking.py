import json
import os
import time
from typing import List
from src.utils import OperationResult
from src.elo import Elo

eloFilename = "./json/elo/%d/%s/elo.json"
folderName = "./json/elo/%d/%s"

player1Key = "player1"
player2Key = "player2"
serverIdKey = "server_id"
formatNameKey = "format_name"
playersKey = "players"
activeMatchesKey = "active_matches"
playerIdKey = "player_id"
playerNameKey = "player_name"
playerScoreKey = "score"
queueKey = "queue"
playerInQueueKey = "player"
timestampInQueueKey = "timestamp"

class Player:
    
    def __init__(self, playerId:int, playerName:str, score:float):
        self.playerId = playerId
        self.playerName = playerName
        self.score = score

    def getPlayerId(self):
        return self.playerId

    def getPlayerName(self):
        return self.playerName

    def getPlayerScore(self):
        return self.score

    def setPlayerName(self, name:str):
        self.playerName = name
    
    def setScore(self, score:float):
        self.score = score

    def toDict(self):
        player = {}
        player[playerIdKey] = self.playerId
        player[playerNameKey] = self.playerName
        player[playerScoreKey] = self.score
        return player

def playerFromDict(playerAsDict):
    playerId = playerAsDict.get(playerIdKey)
    playerName = playerAsDict.get(playerNameKey)
    playerScore = playerAsDict.get(playerScoreKey)
    return Player(playerId, playerName, playerScore)

class ActiveMatch():
    def __init__(self, player1:int, player2:int):
        self.player1 = player1
        self.player2 = player2

    def toDict(self):
        match = {}
        match[player1Key] = self.player1
        match[player2Key] = self.player2
        return match

def matchFromDict(matchAsDict):
    player1 = matchAsDict.get(player1Key)
    player2 = matchAsDict.get(player2Key)
    return ActiveMatch(player1, player2)

class Queue():
    def __init__(self, player:Player):
        self.player = player
        self.timestamp = time.time()

    def setTimestamp(self, timestamp:float):
        self.timestamp = timestamp

    def isValid(self):
        newTimestamp = time.time()
        if newTimestamp - self.timestamp < 3600:
            return True
        return False

    def toDict(self):
        queueAsDict = {}
        queueAsDict[playerInQueueKey] = self.player.toDict()
        queueAsDict[timestampInQueueKey] = self.timestamp
        return queueAsDict

def queueFromDict(queueAsDict):
    playerInQueue = playerFromDict(queueAsDict.get(playerInQueueKey))
    timestampInQueue = queueAsDict.get(timestampInQueueKey)
    queue = Queue(playerInQueue)
    queue.setTimestamp(timestampInQueue)
    return queue

class Matchmaking:
    def __init__(self, formatName:str, serverId:int):
        self.formatName = formatName
        self.serverId = serverId
        self.filename = eloFilename%(serverId, formatName)
        self.foldername = folderName%(serverId, formatName)
        if not os.path.exists(self.foldername):
            os.makedirs(self.foldername)
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as file:
                json.dump(self.getDefaultMatchmakingFile(), file, indent=4)
        with open(self.filename) as file:
            file = json.load(file)
            self.players:List[Player] = []
            for player in file.get(playersKey):
                self.players.append(playerFromDict(player))
            self.activeMatches:List[ActiveMatch] = []
            for match in file.get(activeMatchesKey):
                self.activeMatches.append(matchFromDict(match))
            self.queue:Queue = None
            queueInFile = file.get(queueKey)
            if queueInFile != None:
                queue = queueFromDict(queueInFile)
                if queue.isValid():
                    self.queue = queue
    
    def getDefaultMatchmakingFile(self):
        matchmaking = {}
        matchmaking[serverIdKey] = self.serverId
        matchmaking[formatNameKey] = self.formatName
        matchmaking[playersKey] = []
        matchmaking[activeMatchesKey] = []
        return matchmaking       

    def toDict(self):
        matchmaking = {}
        matchmaking[serverIdKey] = self.serverId
        matchmaking[formatNameKey] = self.formatName
        matchmakingPlayers = []
        for player in self.players:
            matchmakingPlayers.append(player.toDict())
        matchmaking[playersKey] = matchmakingPlayers
        matchmakingMatches = []
        for match in self.activeMatches:
            matchmakingMatches.append(match.toDict())
        matchmaking[activeMatchesKey] = matchmakingMatches
        queue = self.queue
        if queue == None:
            matchmaking[queueKey] = None
        elif not queue.isValid():
            matchmaking[queueKey] = None
        else:
            matchmaking[queueKey] = queue.toDict()
        return matchmaking
    
    def save(self):
        if self.queue != None and not self.queue.isValid():
            self.queue = None
        with open(self.filename, 'w') as file:
            json.dump(self.toDict(), file, indent=4)

    def getPlayerForId(self, playerId:int):
        for player in self.getPlayers():
            if player.getPlayerId() == playerId:
                return player
    
    def registerPlayer(self, playerId:int, playerName:str):
        registeredPlayer = self.getPlayerForId(playerId)
        if registeredPlayer != None:
            # Update username just in case
            registeredPlayer.setPlayerName(playerName)
            self.save()
            return OperationResult(False, "User <@%d> was already registered for %s!"%(playerId, self.formatName))
        else:
            registeredPlayer = Player(playerId, playerName, 1000)
            self.players.append(registeredPlayer)
            self.save()
            return OperationResult(True, "User <@%d> was registered for %s with a rating of 1000!"%(playerId, self.formatName))

    def joinQueue(self, playerId: int):
        player = self.getPlayerForId(playerId)
        if player != None:
            currentQueue = self.queue
            if currentQueue == None or not currentQueue.isValid():
                # Create a queue
                self.queue = Queue(player)
                self.save()
                return OperationResult(True, "You have joined the queue! If someone else joins the queue in 10 minutes, a ranked match will start.")
            else:
                # Is this the same player?
                if playerId == self.queue.player.getPlayerId():
                    result = OperationResult(False, "You are already in queue!")
                    return result
                else:
                # Start a match
                    match = ActiveMatch(currentQueue.player.getPlayerId(), player.getPlayerId())
                    result = OperationResult(True, "A %s ranked match has started between <@%d> and <@%d>" % (self.formatName, currentQueue.player.getPlayerId(), player.getPlayerId()))
                    result.addExtras(match)
                    self.queue = None
                    self.activeMatches.append(match)
                    self.save()
                    return result
        else:
            return OperationResult(False, "You aren't registered to the league. Please register using /register_for_league before joining the queue!")

    def cancelMatch(self, playerId: int):
        match = self.getMatchForPlayer(playerId)
        if match != None:
            self.activeMatches.remove(match)
            self.save()
            if match.player1 == playerId:
                return OperationResult(True, "The match between <@%d> and <@%d> has been cancelled by <@%d>'s request."%(match.player1, match.player1, match.player1))
            else:
                return OperationResult(True, "The match between <@%d> and <@%d> has been cancelled by <@%d>'s request."%(match.player1, match.player2, match.player2))
        else:
            return OperationResult(False, "You have no active matches")


    def startMatch(self, player1:int, player2:int):
        isMatchValid = self.isNewMatchValid(player1, player2)

        if isMatchValid.wasSuccessful():
            activeMatch = ActiveMatch(player1, player2)
            self.activeMatches.append(activeMatch)
            self.save()
        
        return isMatchValid

    def getMatchForPlayer(self, playerId:int):
        for match in self.activeMatches:
            if match.player1 == playerId:
                return match
            if match.player2 == playerId:
                return match
        return None

    def endMatch(self, winnerId:int):
        winner = self.getPlayerForId(winnerId)
        match = self.getMatchForPlayer(winnerId)
        if winner != None and match != None:
            loserId = 0
            if match.player1 == winnerId:
                loserId = match.player2
            else:
                loserId = match.player1
            loser = self.getPlayerForId(loserId)
            winnerScore = winner.getPlayerScore()
            loserScore = loser.getPlayerScore()
            elo = Elo(winnerScore, loserScore)
            elo.finishMatch()
            winner.setScore(elo.getWinnerUpdatedScore())
            loser.setScore(elo.getLoserUpdatedScore())
            self.activeMatches.remove(match)
            self.save()
            return OperationResult(True, "<@%d> won their match against <@%d>!"%(winner.getPlayerId(), loser.getPlayerId()))
        else:
            return OperationResult(False, "You don't have any pending active matches")

    def isNewMatchValid(self, player1:int, player2:int):
        playerIds = [player1, player2]
        for match in self.activeMatches:
            if match.player1 in playerIds:
                return OperationResult(False, "<@%d> has an active match already"%player1)
            if match.player2 in playerIds:
                return OperationResult(False, "<@%d> has an active match already"%player2)
        return OperationResult(True, "")

    def getScoreForPlayer(self, userId:int):
        player = self.getPlayerForId(userId)
        if player != None:
            return player.getPlayerScore()
        else:
            return -1

    def getHighestRankedPlayers(self):
        sortedList : List[Player] = []
        for player in self.players:
            sortedList.append(player)
        length = len(sortedList)
        for i in range(length-1):
            for j in range(0, length-i-1):
                if sortedList[j].getPlayerScore() < sortedList[j+1].getPlayerScore():
                    sortedList[j], sortedList[j+1] = sortedList[j+1], sortedList[j]
        return sortedList[:10]

    def getPlayers(self):
        return self.players

    def getServerId(self):
        return self.serverId

    def getFormatName(self):
        return self.formatName

    def getActiveMatches(self):
        return self.activeMatches
                

class MatchmakingManager:

    def __init__(self, formatName:str, serverId:int):
        self.matchmaking = Matchmaking(formatName, serverId)

    def registerPlayer(self, playerId: int, playerName: str):
        return self.matchmaking.registerPlayer(playerId, playerName)
            
    def createMatch(self, playerA: int, playerB: int):
        return self.matchmaking.startMatch(playerA, playerB)

    def endMatch(self, winnerId:int):
        return self.matchmaking.endMatch(winnerId)

    def getLeaderboard(self):
        return self.matchmaking.getHighestRankedPlayers()

    def getRatingForPlayer(self, playerId:int):
        return self.matchmaking.getScoreForPlayer(playerId)

    def getActiveMatches(self):
        return self.matchmaking.getActiveMatches()
    
    def getPlayerForId(self, playerId:int):
        return self.matchmaking.getPlayerForId(playerId)

    def getMatchForPlayer(self, playerId:int):
        return self.matchmaking.getMatchForPlayer(playerId)

    def joinQueue(self, playerId:int):
        return self.matchmaking.joinQueue(playerId)

    def cancelMatch(self, playerId: int):
        return self.matchmaking.cancelMatch(playerId)
    