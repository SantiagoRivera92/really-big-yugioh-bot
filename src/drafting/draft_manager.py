import json
import os
import random
import requests
from src.utils.utils import OperationResult

class DraftManager:
    def __init__(self, server_id):
        self.server_id = server_id
        self.draft_data = self.load_draft_data()

    def init_cube_draft(self, cube_id, players, pack_size, pack_amount):
        try:
            if len(self.draft_data) == 0 or self.draft_data["finished"]:
                cube_data = download_cube(cube_id)
                self.draft_data = {
                    "cube_id": int(cube_id),
                    "players": int(players),
                    "pack_size": int(pack_size),
                    "pack_amount": int(pack_amount),
                    "cube": process_cube(cube_data),
                    "packs":[],
                    "players_data": [],
                    "current_round": 1,
                    "current_pick": 1,
                    "started":False,
                    "finished":False
                }
                self.save_draft_data()
                return OperationResult(True, "Draft initialized successfully!")
            else:
                return OperationResult(False, "There's already a draft going on! Finish that one before starting a new one.")
        except Exception as e:
            return OperationResult(False, f"Error loading cube: {str(e)}")

    def get_player_by_id(self, player_id):
        for player in self.draft_data["players_data"]:
            if player["id"] == player_id:
                return player
        return None

    def join_cube_draft(self, player_name, player_id):
        if not self.draft_data["finished"]:
            if len(self.draft_data["players_data"]) >= self.draft_data["players"]:
                return OperationResult(False, "Draft is full")
            if self.draft_data["started"]:
                return OperationResult(False, "Draft has already started")

        self.draft_data["players_data"].append({"name": player_name, "id": player_id, "seat":len(self.draft_data["players_data"])+1, "picked_cards": []})

        if len(self.draft_data["players_data"]) == self.draft_data["players"]:
            self.start_cube_draft()
        else:
            self.save_draft_data()

        return OperationResult(True, "Joined draft successfully")

    def drop_cube_draft(self, player_id):
        if self.draft_data["started"]:
            return OperationResult(False, "Draft has already started")
        self.draft_data["players_data"] = [player for player in self.draft_data["players_data"] if player["id"] != player_id]
        self.save_draft_data()
        return OperationResult(True, "Dropped from draft successfully")

    def start_cube_draft(self):
        # Generate packs and assign them to players
        pack_id = 0
        self.draft_data["started"] = True
        for _ in range(self.draft_data["pack_amount"] * len(self.draft_data["players_data"])):
            pack_id += 1
            pack = random.sample(self.draft_data["cube"], self.draft_data["pack_size"])
            for card in pack:
                self.draft_data["cube"].remove(card)
            self.draft_data["packs"].append({"pack":pack, "pack_id":pack_id})

        # Assign initial packs to players
        for i, player in enumerate(self.draft_data["players_data"]):
            player["current_pack"] = self.draft_data["packs"][i]
        self.draft_data["current_round"]= 1
        self.draft_data["current_pick"]= 1
        self.save_draft_data()

        return OperationResult(True, self.draft_data["players_data"])

    def pick(self, player_id, card_id):
        player = next(player for player in self.draft_data["players_data"] if player["id"] == player_id)
        player["picked_cards"].append(card_id)
        pack_id = player["current_pack"]["pack_id"]
        
        picked_pack = None
        new_pick = False
        
        # Find the pack
        for pack in self.draft_data["packs"]:
            if pack["pack_id"] == pack_id:
                picked_pack = pack
                break
        # Remove the pack from the draft
        if picked_pack is not None:
            self.draft_data["packs"].remove(picked_pack)
        
        # Remove the card from the pack
        picked_pack["pack"].remove(card_id)
        
        # Add the new pack to the draft
        self.draft_data["packs"].append(picked_pack)

        # Check if the round is complete
        if all_players_have_picked(self.draft_data):
            # Pass packs to the next player
            new_pick=True
            self.draft_data["current_pick"] += 1
            if self.draft_data["current_pick"] > self.draft_data["pack_size"]:
                # Last pick of a pack
                self.draft_data["current_pick"] = 1
                self.draft_data["current_round"] += 1
                
            
            if self.draft_data["current_round"] > self.draft_data["pack_amount"]:
                # Draft is done
                self.end_draft()
                return OperationResult(False, "The draft is over!")
            
            # Check if the current round is odd or even: If it's odd, we go counterclockwise. If it's even, we go clockwise.
            direction = self.draft_data["current_round"] % 2
            pack_number = self.draft_data["current_round"] - 1
            pick_number = self.draft_data["current_pick"]
            players = len(self.draft_data["players_data"])
            
            for player in self.draft_data["players_data"]:
                seat = player["seat"]
                pack_root = pack_number * players
                if direction == 1:
                    # Odd: We substract
                    pack_mod = ((seat + pick_number) % players) + 1
                else:
                    # Even, we add
                    pack_mod = ((seat - pick_number) % players) + 1
                pack_id = pack_root + pack_mod
                pack = next(_pack for _pack in self.draft_data["packs"] if _pack["pack_id"] == pack_id)
                player["current_pack"] = pack

        self.save_draft_data()
        return OperationResult(new_pick, "")

    def load_draft_data(self):
        try:
            with open(f"json/draft/{self.server_id}/draft.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_draft_data(self):
        os.makedirs(f"json/draft/{self.server_id}", exist_ok=True)
        with open(f"json/draft/{self.server_id}/draft.json", "w", encoding="utf-8") as f:
            json.dump(self.draft_data, f, indent=4)
            
    def end_draft(self):
        self.draft_data["finished"] = True
        with open(f"json/draft/{self.server_id}/draft.json", "w", encoding="utf-8") as f:
            json.dump(self.draft_data, f, indent=4)
    
    def kill_draft(self):
        with open(f"json/draft/{self.server_id}/draft.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

def download_cube(cube_id):
    url = "https://ygoprodeck.com/api/cube/downloadCube.php"
    data = {"cubeid": cube_id}
    response = requests.post(url, data=data, timeout=20)
    response.raise_for_status()
    return response.json()

def process_cube(cube_data):
    card_pool = []
    for card in cube_data["cube_list"]:
        card_pool.extend([card["id"]] * card["quantity"])
    return card_pool

def all_players_have_picked(draft_data):
    picked_cards_for_round = (draft_data["current_round"]-1) * draft_data["pack_size"] + draft_data["current_pick"]
    for player in draft_data["players_data"]:
        if len(player["picked_cards"]) < picked_cards_for_round:
            return False
    return True