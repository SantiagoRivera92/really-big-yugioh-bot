import json
import os
import time
from typing import List, Union
from src.utils.utils import OperationResult
from src.league.elo import Elo
import src.strings as Strings

ELO_FILE_NAME = "./json/elo/%d/%s/elo.json"
FOLDER_NAME = "./json/elo/%d/%s"

PLAYER_1_KEY = "player1"
PLAYER_2_KEY = "player2"
SERVER_ID_KEY = "server_id"
FORMAT_NAME_KEY = "format_name"
PLAYERS_KEY = "players"
ACTIVE_MATCHES_KEY = "active_matches"
PLAYER_ID_KEY = "player_id"
PLAYER_NAME_KEY = "player_name"
PLAYER_SCORE_KEY = "score"
QUEUE_KEY = "queue"
PLAYER_IN_QUEUE_KEY = "player"
TIMESTAMP_IN_QUEUE_KEY = "timestamp"

class Player:
    
    def __init__(self, player_id:int, player_name:str, score:float):
        self.player_id = player_id
        self.player_name = player_name
        self.score = score

    def set_player_name(self, name:str):
        self.player_name = name
    
    def set_score(self, score:float):
        self.score = score
        
    def decay_score(self):
        if self.score > 700:
            # Players over 700 ELO lose 0.75% of their score every day
            self.score = self.score * 0.9925
        elif self.score > 550:
            # Players over 550 ELO but under 700 lose (11/14)^(1/60) of their score every day. This number was chosen so it takes 60 days to go from 700 to 550.
            self.score = self.score * 0.9959886
            # 550 is the minimum score you can reach from above 550.
            self.score = max(self.score, 550)

    def to_dict(self):
        player = {}
        player[PLAYER_ID_KEY] = self.player_id
        player[PLAYER_NAME_KEY] = self.player_name
        player[PLAYER_SCORE_KEY] = self.score
        return player

def player_from_dict(player_as_dict):
    player_id = player_as_dict.get(PLAYER_ID_KEY)
    player_name = player_as_dict.get(PLAYER_NAME_KEY)
    player_score = player_as_dict.get(PLAYER_SCORE_KEY)
    return Player(player_id, player_name, player_score)

class ActiveMatch():
    def __init__(self, player1:int, player2:int):
        self.player1 = player1
        self.player2 = player2

    def to_dict(self):
        active_match = {}
        active_match[PLAYER_1_KEY] = self.player1
        active_match[PLAYER_2_KEY] = self.player2
        return active_match

def match_from_dict(match_as_dict):
    player1 = match_as_dict.get(PLAYER_1_KEY)
    player2 = match_as_dict.get(PLAYER_2_KEY)
    return ActiveMatch(player1, player2)

class Queue():
    def __init__(self, player:Player):
        self.player = player
        self.timestamp = time.time()

    def set_timestamp(self, timestamp:float):
        self.timestamp = timestamp

    def is_valid(self):
        new_timestamp = time.time()
        return new_timestamp - self.timestamp < 3600

    def to_dict(self):
        queue_as_dict = {}
        queue_as_dict[PLAYER_IN_QUEUE_KEY] = self.player.to_dict()
        queue_as_dict[TIMESTAMP_IN_QUEUE_KEY] = self.timestamp
        return queue_as_dict

def queue_from_dict(queue_as_dict):
    player_in_queue = player_from_dict(queue_as_dict.get(PLAYER_IN_QUEUE_KEY))
    ts_in_queue = queue_as_dict.get(TIMESTAMP_IN_QUEUE_KEY)
    queue = Queue(player_in_queue)
    queue.set_timestamp(ts_in_queue)
    return queue

class Matchmaking:
    def __init__(self, format_name:str, server_id:int):
        self.format_name = format_name
        self.server_id = server_id
        self.filename = ELO_FILE_NAME%(server_id, format_name)
        self.foldername = FOLDER_NAME%(server_id, format_name)
        if not os.path.exists(self.foldername):
            os.makedirs(self.foldername)
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', encoding="utf-8") as file:
                json.dump(self.get_default_matchmaking_file(), file, indent=4)
        with open(self.filename, encoding="utf-8") as file:
            file = json.load(file)
            self.players:List[Player] = []
            for player in file.get(PLAYERS_KEY):
                self.players.append(player_from_dict(player))
            self.active_matches:List[ActiveMatch] = []
            for match in file.get(ACTIVE_MATCHES_KEY):
                self.active_matches.append(match_from_dict(match))
            self.queue:Queue = None
            queue_in_file = file.get(QUEUE_KEY)
            if queue_in_file is not None:
                queue = queue_from_dict(queue_in_file)
                if queue.is_valid():
                    self.queue = queue
                    
    def decay(self):
        new_players = []
        for player in self.players:
            player.decay_score()
            new_players.append(player)
        self.players = new_players
        self.save()
    
    def get_default_matchmaking_file(self):
        matchmaking = {}
        matchmaking[SERVER_ID_KEY] = self.server_id
        matchmaking[FORMAT_NAME_KEY] = self.format_name
        matchmaking[PLAYERS_KEY] = []
        matchmaking[ACTIVE_MATCHES_KEY] = []
        return matchmaking       

    def to_dict(self):
        matchmaking = {}
        matchmaking[SERVER_ID_KEY] = self.server_id
        matchmaking[FORMAT_NAME_KEY] = self.format_name
        mm_players = []
        for player in self.players:
            mm_players.append(player.to_dict())
        matchmaking[PLAYERS_KEY] = mm_players
        mm_matches = []
        for match in self.active_matches:
            mm_matches.append(match.to_dict())
        matchmaking[ACTIVE_MATCHES_KEY] = mm_matches
        queue = self.queue
        if queue is None:
            matchmaking[QUEUE_KEY] = None
        elif not queue.is_valid():
            matchmaking[QUEUE_KEY] = None
        else:
            matchmaking[QUEUE_KEY] = queue.to_dict()
        return matchmaking
    
    def save(self):
        if (self.queue is not None) and (not self.queue.is_valid()):
            self.queue = None
        with open(self.filename, 'w', encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=4)

    def get_player_for_id(self, player_id:int) -> Union[Player | None]:
        for player in self.get_players():
            if player.player_id == player_id:
                return player
        return None
    
    def register_player(self, player_id:int, player_name:str):
        player = self.get_player_for_id(player_id)
        if player is not None:
            # Update username just in case
            player.set_player_name(player_name)
            self.save()
            return OperationResult(False, Strings.ERROR_MATCHMAKING_USER_ALREADY_REGISTERED % (player_id, self.format_name))
        
        player = Player(player_id, player_name, 500)
        self.players.append(player)
        self.save()
        return OperationResult(True, Strings.MESSAGE_MATCHMAKING_USER_REGISTERED % (player_id, self.format_name))

    def join_queue(self, player_id: int):
        player = self.get_player_for_id(player_id)
        if player is not None:
            current_queue = self.queue
            if current_queue is None or not current_queue.is_valid():
                # Create a queue
                self.queue = Queue(player)
                self.save()
                return OperationResult(True, Strings.MESSAGE_MATCHMAKING_JOINED_QUEUE)
            
            # Is this the same player?
            if player_id == self.queue.player.player_id:
                result = OperationResult(False, Strings.ERROR_MATCHMAKING_ALREADY_IN_QUEUE)
                return result
            
            # Start a match
            match = ActiveMatch(current_queue.player.player_id, player.player_id)
            result = OperationResult(True, Strings.MESSAGE_MATCHMAKING_MATCH_STARTED % (self.format_name, current_queue.player.player_id, player.player_id))
            self.queue = None
            self.active_matches.append(match)
            self.save()
            return result
        return OperationResult(False, Strings.ERROR_MATCHMAKING_REGISTER_FIRST)

    def cancel_match(self, player_id: int):
        match = self.get_match_for_player(player_id)
        if match is not None:
            self.active_matches.remove(match)
            self.save()
            if match.player1 == player_id:
                return OperationResult(True, Strings.MESSAGE_MATCHMAKING_MATCH_CANCELLED % (match.player1, match.player1, match.player1))
            return OperationResult(True, Strings.MESSAGE_MATCHMAKING_MATCH_CANCELLED % (match.player1, match.player2, match.player2))
        return OperationResult(False, Strings.ERROR_MATCHMAKING_NO_ACTIVE_MATCHES)

    def start_match(self, player1:int, player2:int, force:bool):
        is_match_valid = self.is_new_match_valid(player1, player2)

        if is_match_valid.was_successful() or force:
            match = ActiveMatch(player1, player2)
            self.active_matches.append(match)
            self.save()
        
        return is_match_valid

    def get_match_for_player(self, player_id:int):
        for match in self.active_matches:
            if match.player1 == player_id:
                return match
            if match.player2 == player_id:
                return match
        return None

    def end_match(self, winner_id:int):
        winner = self.get_player_for_id(winner_id)
        match = self.get_match_for_player(winner_id)
        if winner is not None and match is not None:
            loser_id = 0
            if match.player1 == winner_id:
                loser_id = match.player2
            else:
                loser_id = match.player1
            loser = self.get_player_for_id(loser_id)
            winner_score = winner.score
            loser_score = loser.score
            elo = Elo(winner_score, loser_score)
            elo.finish_match()
            winner.set_score(elo.get_winner_updated_score())
            loser.set_score(elo.get_loser_updated_score())
            self.active_matches.remove(match)
            self.save()
            return OperationResult(True, Strings.MESSAGE_MATCHMAKING_WON_ELO_UPDATED % 
                            (winner.player_id, winner_score, elo.get_winner_updated_score(), loser.player_id, loser_score, elo.get_loser_updated_score()))
        return OperationResult(False, Strings.ERROR_MATCHMAKING_NO_ACTIVE_MATCHES)

    def is_new_match_valid(self, player1:int, player2:int):
        player_ids = [player1, player2]
        for match in self.active_matches:
            if match.player1 in player_ids:
                return OperationResult(False, Strings.ERROR_MATCHMAKING_ACTIVE_MATCH_IN_PROGRESS % player1)
            if match.player2 in player_ids:
                return OperationResult(False, Strings.ERROR_MATCHMAKING_ACTIVE_MATCH_IN_PROGRESS % player2)
        return OperationResult(True, "")

    def get_score_for_player(self, player_id:int):
        player = self.get_player_for_id(player_id)
        if player is not None:
            return player.score
        return -1

    def get_highest_ranked_players(self):
        sorted_list : List[Player] = []
        for player in self.players:
            sorted_list.append(player)
        length = len(sorted_list)
        for i in range(length-1):
            for j in range(0, length-i-1):
                if sorted_list[j].score < sorted_list[j+1].score:
                    sorted_list[j], sorted_list[j+1] = sorted_list[j+1], sorted_list[j]
        return sorted_list[:10]

    def get_id_for_player_name(self, player_name:str):
        for player in self.players:
            if player.player_name == player_name:
                return player.player_id
        return -1

    def get_players(self):
        return self.players

    def get_active_matches(self):
        return self.active_matches
                

class MatchmakingManager:

    def __init__(self, format_name:str, server_id:int):
        self.matchmaking = Matchmaking(format_name, server_id)

    def register_player(self, player_id: int, player_name: str):
        return self.matchmaking.register_player(player_id, player_name)
            
    def create_match(self, player_1: int, player_2: int, force: bool):
        return self.matchmaking.start_match(player_1, player_2, force)

    def end_match(self, winner_id:int):
        return self.matchmaking.end_match(winner_id)

    def get_leaderboard(self):
        return self.matchmaking.get_highest_ranked_players()

    def get_score_for_player(self, player_id:int):
        return self.matchmaking.get_score_for_player(player_id)

    def get_active_matches(self):
        return self.matchmaking.get_active_matches()
    
    def get_player_for_id(self, player_id:int):
        return self.matchmaking.get_player_for_id(player_id)

    def get_match_for_player(self, player_id:int):
        return self.matchmaking.get_match_for_player(player_id)

    def join_queue(self, player_id:int):
        return self.matchmaking.join_queue(player_id)

    def cancel_match(self, player_id: int):
        return self.matchmaking.cancel_match(player_id)

    def get_id_for_player_name(self, player_name:str):
        return self.matchmaking.get_id_for_player_name(player_name)
    
    def get_players(self):
        return self.matchmaking.get_players()
    
    def decay(self):
        self.matchmaking.decay()