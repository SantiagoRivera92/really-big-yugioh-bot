from typing import List
import json

from src.utils.utils import OperationResult
import src.strings as Strings


MAIN_DECK_START = "#main"
EXTRA_DECK_START = "#extra"
SIDE_DECK_START = "!side"

ALIAS_FILE_NAME = "./json/cardids.json"

def normalize_id(card_id:str):
	while card_id.startswith("0"):
		card_id = card_id[1:]
	return card_id

class Card:
	def __init__(self, card_id:str, copies:int):
		self.card_id = card_id
		self.copies = copies

	def add_copy(self):
		self.copies+=1

class Deck:
	def __init__(self, main:List[Card], extra:List[Card], side:List[Card], name:str=""):
		self.main = main
		self.extra = extra
		self.side = side
		self.name = name

	def get_main_deck(self):
		return self.main
	
	def get_extra_deck(self):
		return self.extra

	def get_side_deck(self):
		return self.side

class Ydk:
	def __init__(self, ydk_file:str):
		self.ydk_file = ydk_file.replace("\r", "").replace("\n\n", "\n")

	def get_copies(self):
		deck : List[Card] = []
		for line in self.ydk_file.split("\n"):
			found = False
			line = normalize_id(line)
			if line.isdigit():
				for card in deck:
					if card.card_id == line:
						card.add_copy()
						found = True
				if not found:
					deck.append(Card(line, 1))

		return deck

	def get_deck(self) -> Deck:
		main_deck:List[Card] = []
		side_deck:List[Card] = []
		extra_deck:List[Card] = []

		counting_main = False
		counting_extra = False
		counting_side = False

		with open(ALIAS_FILE_NAME, encoding="utf-8") as file:
			aliases = json.load(file)


		for line in self.ydk_file.split("\n"):
			a = line.isdigit()
			if a:
				for alias in aliases:
					if alias['before'] == line:
						line = alias['after']
				if counting_main:
					found = False
					for card in main_deck:
						if card.card_id == line:
							card.copies = card.copies + 1
							found = True
					if not found:
						main_deck.append(Card(line, 1))
				if counting_extra:
					found = False
					for card in extra_deck:
						if card.card_id == line:
							card.copies = card.copies + 1
							found = True
					if not found:
						extra_deck.append(Card(line, 1))
				if counting_side:
					found = False
					for card in side_deck:
						if card.card_id == line:
							card.copies = card.copies + 1
							found = True
					if not found:
						side_deck.append(Card(line, 1))


			if line == MAIN_DECK_START:
				counting_main = True
				counting_extra = False
				counting_side = False
			elif line == EXTRA_DECK_START:
				counting_main = False
				counting_extra = True
				counting_side = False
			elif line == SIDE_DECK_START:
				counting_main = False
				counting_extra = False
				counting_side = True 

		return Deck(main_deck, extra_deck, side_deck)

	def get_ydk_errors(self):
		main_deck_count = 0
		extra_deck_count = 0
		side_deck_count = 0
		counting_main = False
		counting_extra = False
		counting_side = False

		for line in self.ydk_file.split("\n"):
			a = line.isdigit()
			b = line.startswith("#")
			c = line.startswith("!")
			d = len(line) == 0

			if not (a or b or c or d):
				return OperationResult(False, Strings.ERROR_YDK_INVALID_LINE % line)

			if not (b or c or d):
				if counting_main:
					main_deck_count += 1
				if counting_extra:
					extra_deck_count += 1
				if counting_side:
					side_deck_count += 1


			if line == MAIN_DECK_START:
				counting_main = True
				counting_extra = False
				counting_side = False
			elif line == EXTRA_DECK_START:
				counting_main = False
				counting_extra = True
				counting_side = False
			elif line == SIDE_DECK_START:
				counting_main = False
				counting_extra = False
				counting_side = True 
		
		if main_deck_count < 40:
			return OperationResult(False, Strings.ERROR_YDK_SMALL_MAIN_DECK % main_deck_count)
		if main_deck_count > 60:
			return OperationResult(False, Strings.ERROR_YDK_BIG_MAIN_DECK % main_deck_count)
		if extra_deck_count > 15:
			return OperationResult(False, Strings.ERROR_YDK_BIG_EXTRA_DECK % extra_deck_count)
		if side_deck_count > 15:
			return OperationResult(False, Strings.ERROR_YDK_BIG_SIDE_DECK % side_deck_count)
		return OperationResult(True, "")

def error_messages_to_string(error_messages):
	em = "\n"
	for message in error_messages:
		em = f"{em}\n{message}"
	return em

def open_banlist(banlist_file):
	with open(banlist_file, encoding="utf-8") as banlist:
		return banlist.read()

class DeckValidator:

	def __init__(self, card_collection):
		self.card_collection = card_collection

	def validate_deck(self, ydk_deck_list:str, banlist_file:str):
		decklist = Ydk(ydk_deck_list)
		validation = decklist.get_ydk_errors()
		if validation.was_successful():
			banlist = open_banlist(banlist_file)
			validation = self.validate_against_banlist(decklist, banlist)

		return validation

	def validate_against_banlist(self, ydk:Ydk, banlist:str):
		banlist_as_lines = banlist.split("\n")
		error_messages = []
		copies = ydk.get_copies()
		for card in copies:
			card_name = self.card_collection.get_card_name_from_id(card.card_id)
			found = False
			for line in banlist_as_lines:
				if card.card_id in line:
					# This is just a way of finding how many copies are legal of a given card. Not pretty but it works.
					id_count = len(card.card_id)
					limit_as_string = line[id_count+1 : id_count+2]
					if limit_as_string == "-":
						limit_as_string = "-1"
					limit = int(limit_as_string)
					
					# Now we check whether the max number is less than 1 (which means illegal or forbidden) 
					# or whether there's more copies of a card than the legal limit (4 copies of anything, 3 of a semi-limited, etc)
					if limit < 1 or card.copies > limit:
						if card_name is None:
							error_messages.append(Strings.ERROR_YDK_NON_EXISTING_ID % card.card_id)
						elif limit == -1:
							error_messages.append(Strings.ERROR_YDK_ILLEGAL_CARD % card_name)
						elif limit == 0:
							error_messages.append(Strings.ERROR_YDK_FORBIDDEN_CARD % card_name)
						elif limit < card.copies:
							error_messages.append(Strings.ERROR_YDK_EXTRA_COPIES % (card.copies, card_name, limit))
					found = True
					break
			if not found:
				if card_name is not None:
					error_messages.append(Strings.ERROR_YDK_ILLEGAL_CARD % card_name)
				else:
					error_messages.append(Strings.ERROR_YDK_NON_EXISTING_ID % card.card_id)

		if len(error_messages) == 0:
			return OperationResult(True, "")

		return OperationResult(False, error_messages_to_string(error_messages))