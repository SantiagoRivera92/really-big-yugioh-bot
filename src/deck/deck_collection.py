import os
import json
from typing import List
from src.utils.utils import OperationResult
import src.strings as Strings

FOLDER_NAME = "./json/deckcollection/%d/%s/"
COLLECTION_FILE_NAME = "./json/deckcollection/%d/%s/collection.json"
DECKS_FOLDER_NAME = "./ydk/%d/%s/decks"
DECK_FILE_NAME = "./ydk/%d/%s/decks/%s.ydk"

COLLECTION_ENABLED_KEY = "collection_enabled"
DECKS_KEY = "decks"
PLAYER_NAME_KEY = "player"
DECK_FILENAME_KEY = "deck"

class CollectionDeck:
	def __init__(self, player_name:str, deck_file_name:str):
		self.player_name = player_name
		self.deck_file_name = deck_file_name

	def to_dict(self):
		deck = {}
		deck[PLAYER_NAME_KEY] = self.player_name
		deck[DECK_FILENAME_KEY] = self.deck_file_name
		return deck

def deck_from_dict(dictionary:dict):
	return CollectionDeck(dictionary.get(PLAYER_NAME_KEY), dictionary.get(DECK_FILENAME_KEY))

class DeckCollection:
	
	def __init__(self, format_name:str, server_id:int):
		self.format_name = format_name
		self.server_id = server_id
		self.filename = COLLECTION_FILE_NAME%(server_id, format_name)
		self.folder_name = FOLDER_NAME%(server_id, format_name)
		if not os.path.exists(self.folder_name):
			os.makedirs(self.folder_name)
		if not os.path.exists(self.filename):
			with open(self.filename, 'w', encoding="utf-8") as file:
				json.dump(self.get_default_deck_collection_content(), file, indent=4)
		with open(self.filename, encoding="utf-8") as file:
			collection = json.load(file)
			decks = collection[DECKS_KEY]
			self.decks:List[CollectionDeck] = []
			self.collection_enabled:bool = collection[COLLECTION_ENABLED_KEY]
			for deck in decks:
				self.decks.append(deck_from_dict(deck))

	def to_dict(self):
		collection = {}
		decks = []
		for deck in self.decks:
			decks.append(deck.to_dict())
		collection[DECKS_KEY] = decks
		collection[COLLECTION_ENABLED_KEY] = self.collection_enabled
		return collection

	def save(self):
		with open(self.filename, 'w', encoding="utf-8") as file:
			json.dump(self.to_dict(), file, indent=4)

	def add_deck(self, player_name:str, deck:str):
		if not self.collection_enabled:
			return OperationResult(False, Strings.ERROR_DECK_COLLECTION_SUBMISSION_DISABLED)
		deck_file_name = DECK_FILE_NAME%(self.server_id, self.format_name, player_name)
		folder_name = DECKS_FOLDER_NAME%(self.server_id, self.format_name)
		if not os.path.exists(folder_name):
			os.makedirs(folder_name)
		with open(deck_file_name, 'w', encoding="utf-8") as file:
			deck_as_lines = deck.split("\n")
			for line in deck_as_lines:
				line = line.replace("\n", "").replace("\r", "")
				if len(line) > 0:
					file.write(line)
					file.write("\n")
		deck = CollectionDeck(player_name, deck_file_name)
		new_decks = []
		for saved_deck in self.decks:
			if saved_deck.player_name != player_name:
				new_decks.append(saved_deck)
			
		new_decks.append(deck)
		self.decks = new_decks
		self.save()
		return OperationResult(True, Strings.MESSAGE_DECK_COLLECTION_SUBMISSION_SUCCESSFUL)
		
	def clear_decks(self):
		for deck in self.decks:
			filename = deck.deck_file_name
			if os.path.exists(filename):
				os.remove(filename)
		self.decks = []
		self.save()
		return OperationResult(True, Strings.MESSAGE_DECK_COLLECTION_CLEAR_SUCCESSFUL)

	def enable_deck_collection(self):
		if not self.collection_enabled:
			self.collection_enabled = True
			self.save()
			return OperationResult(True, Strings.MESSAGE_DECK_COLLECTION_ENABLED)
		return OperationResult(False, Strings.ERROR_DECK_COLLECTION_ALREADY_ENABLED)

	def disable_deck_collection(self):
		if self.collection_enabled:
			self.collection_enabled = False
			self.save()
			return OperationResult(True, Strings.MESSAGE_DECK_COLLECTION_DISABLED)
		return OperationResult(False, Strings.ERROR_DECK_COLLECTION_ALREADY_DISABLED)

	def get_default_deck_collection_content(self):
		collection = {}
		collection[DECKS_KEY] = []
		collection[COLLECTION_ENABLED_KEY] = False
		return collection

	def get_registered_players(self):
		players:List[str] = []
		for deck in self.decks:
			players.append(deck.player_name)
		return players
	
	def get_decklist_for_player(self, player_name:str):
		for deck in self.decks:
			if deck.player_name == player_name:
				return deck.deck_file_name
		return None

	def get_readable_deck_for_player(self, player_name:str):
		for deck in self.decks:
			if deck.player_name == player_name:
				return deck.toReadableCollectionDeck()
		return None



class DeckCollectionManager:

	def __init__(self, format_name:str, server_id:int):
		self.deck_collection = DeckCollection(format_name, server_id)

	def get_registered_players(self):
		return self.deck_collection.get_registered_players()

	def clear_decks(self):
		return self.deck_collection.clear_decks()

	def add_deck(self, player_name:str, deck:str):
		return self.deck_collection.add_deck(player_name, deck)

	def begin_collection(self):
		self.clear_decks()
		return self.deck_collection.enable_deck_collection()

	def end_collection(self):
		return self.deck_collection.disable_deck_collection()

	def get_decklist_for_player(self, player_name:str):
		return self.deck_collection.get_decklist_for_player(player_name)

	def get_readable_decklist_for_player(self, player_name:str):
		return self.deck_collection.get_readable_deck_for_player(player_name)