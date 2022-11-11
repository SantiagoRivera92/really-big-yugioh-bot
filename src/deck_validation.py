from src.utils import OperationResult
import src.strings as Strings
from typing import List

MAIN_DECK_START = "#main"
EXTRA_DECK_START = "#extra"
SIDE_DECK_START = "!side"




class Card:
	def __init__(self, cardId, copies):
		self.cardId = cardId
		self.copies = copies

	def addCopy(self):
		self.copies+=1

class Deck:
	def __init__(self, main:List[Card], extra, side):
		self.main = main
		self.extra = extra
		self.side = side

class Ydk:
	def __init__(self, ydkFile:str):
		self.ydkFile = ydkFile.replace("\r", "").replace("\n\n", "\n")

	def getCopies(self):
		deck = []
		for line in self.ydkFile.split("\n"):
			found = False
			if line.isdigit():
				for card in deck:
					if card.cardId == line:
						card.addCopy()
						found = True
				if not found:
					deck.append(Card(line, 1))


		return deck

	def getDeck(self):
		mainDeck:List[Card] = []
		sideDeck:List[Card] = []
		extraDeck:List[Card] = []

		countingMain = False
		countingExtra = False
		countingSide = False

		for line in self.ydkFile.split("\n"):
			a = line.isdigit()
			if a:
				if countingMain:
					found = False
					for card in mainDeck:
						if card.cardId == line:
							card.copies = card.copies + 1
							found = True
					if not found:
						mainDeck.append(Card(line, 1))
				if countingExtra:
					found = False
					for card in extraDeck:
						if card.cardId == line:
							card.copies = card.copies + 1
							found = True
					if not found:
						extraDeck.append(Card(line, 1))
				if countingSide:
					found = False
					for card in sideDeck:
						if card.cardId == line:
							card.copies = card.copies + 1
							found = True
					if not found:
						sideDeck.append(Card(line, 1))


			if line == MAIN_DECK_START:
				countingMain = True
				countingExtra = False
				countingSide = False
			elif line == EXTRA_DECK_START:
				countingMain = False
				countingExtra = True
				countingSide = False
			elif line == SIDE_DECK_START:
				countingMain = False
				countingExtra = False
				countingSide = True 

		return Deck(mainDeck, extraDeck, sideDeck)

	def getYdkErrors(self):
		maindeckCount = 0
		extradeckCount = 0
		sidedeckCount = 0
		countingMain = False
		countingExtra = False
		countingSide = False

		for line in self.ydkFile.split("\n"):
			a = line.isdigit()
			b = line.startswith("#")
			c = line.startswith("!")
			d = len(line) == 0

			if not (a or b or c or d):
				return OperationResult(False, Strings.ERROR_YDK_INVALID_LINE % line)

			if not (b or c or d):
				if countingMain:
					maindeckCount += 1
				if countingExtra:
					extradeckCount += 1
				if countingSide:
					sidedeckCount += 1


			if line == MAIN_DECK_START:
				countingMain = True
				countingExtra = False
				countingSide = False
			elif line == EXTRA_DECK_START:
				countingMain = False
				countingExtra = True
				countingSide = False
			elif line == SIDE_DECK_START:
				countingMain = False
				countingExtra = False
				countingSide = True 
		
		if maindeckCount < 40:
			return OperationResult(False, Strings.ERROR_YDK_SMALL_MAIN_DECK % maindeckCount)
		if maindeckCount > 60:
			return OperationResult(False, Strings.ERROR_YDK_BIG_MAIN_DECK % maindeckCount)
		if extradeckCount > 15:
			return OperationResult(False, Strings.ERROR_YDK_BIG_EXTRA_DECK % extradeckCount)
		if sidedeckCount > 15:
			return OperationResult(False, Strings.ERROR_YDK_BIG_SIDE_DECK % sidedeckCount)
		return OperationResult(True, "")




def errorMessagesToString(errorMessages):
	em = "\n"
	for message in errorMessages:
		em += "\n%s"%message
	return em

def openBanlist(banlistFile):
	with open(banlistFile) as banlist:
		return banlist.read()

class DeckValidator:

	def __init__(self, cardCollection):
		self.cardCollection = cardCollection

	def validateDeck(self, ydkDeckList:str, banlistFile:str):
		decklist = Ydk(ydkDeckList)
		validation = decklist.getYdkErrors()
		if (validation.wasSuccessful()):
			banlist = openBanlist(banlistFile)
			validation = self.validateAgainstBanlist(decklist, banlist)

		return validation

	def validateAgainstBanlist(self, ydk:Ydk, banlist:str):
		banlistAsLines = banlist.split("\n")
		errorMessages = []

		for card in ydk.getCopies():
			cardName = self.cardCollection.getCardNameFromId(card.cardId)
			found = False
			for line in banlistAsLines:
				if card.cardId in line:
					# This is just a way of finding how many copies are legal of a given card. Not pretty but it works.
					legality = line.split(" ")[1]
					idCount = len(card.cardId)
					line = line[idCount+1 : idCount+2]
					if line == "-":
						line = "-1"
					limit = 0
					limit = int(line)
					
					
					# Now we check whether the max number is less than 1 (which means illegal or forbidden) 
					# or whether there's more copies of a card than the legal limit (4 copies of anything, 3 of a semi-limited, etc)
					if limit < 1 or card.copies > limit:
						if cardName == None:
							errorMessages.append(Strings.ERROR_YDK_NON_EXISTING_ID % card.cardId)
						elif limit == -1:
							errorMessages.append(Strings.ERROR_YDK_ILLEGAL_CARD % cardName)
						elif limit == 0:
							errorMessages.append(Strings.ERROR_YDK_FORBIDDEN_CARD % cardName)
						elif limit < card.copies:
							errorMessages.append(Strings.ERROR_YDK_EXTRA_COPIES % (card.copies, cardName, limit))
				found = True
				break
			if not found:
				if cardName != None:
					errorMessages.append(Strings.ERROR_YDK_ILLEGAL_CARD % cardName)
				else:
					errorMessages.append(Strings.ERROR_YDK_NON_EXISTING_ID % card.cardId)

		if len(errorMessages) == 0:
			return OperationResult(True, "")

		return OperationResult(False, errorMessagesToString(errorMessages))


