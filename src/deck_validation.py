from src.utils import OperationResult

class Card:
	def __init__(self, cardId, copies):
		self.cardId = cardId
		self.copies = copies

	def addCopy(self):
		self.copies+=1

class Ydk:
	def __init__(self, ydkFile):
		self.ydkFile = ydkFile.decode("utf-8").split('\r\n')

	def getDeck(self):
		deck = []
		for line in self.ydkFile:
			found = False
			if line.isdigit():
				for card in deck:
					if card.cardId == line:
						card.addCopy()
						found = True
				if not found:
					deck.append(Card(line, 1))


		return deck

	def getYdkErrors(self):
		maindeckCount = 0
		extradeckCount = 0
		sidedeckCount = 0
		countingMain = False
		countingExtra = False
		countingSide = False

		for line in self.ydkFile:
			a = line.isdigit()
			b = line.startswith("#")
			c = line.startswith("!")
			d = len(line) == 0

			if not (a or b or c or d):
				return OperationResult(False, "Invalid line in ydk: %s"%line)

			if not (b or c or d):
				if countingMain:
					maindeckCount += 1
				if countingExtra:
					extradeckCount += 1
				if countingSide:
					sidedeckCount += 1


			if line == mainDeckStart:
				countingMain = True
				countingExtra = False
				countingSide = False
			elif line == extraDeckStart:
				countingMain = False
				countingExtra = True
				countingSide = False
			elif line == sideDeckStart:
				countingMain = False
				countingExtra = False
				countingSide = True 
		
		if maindeckCount < 40:
			return OperationResult(False, "Main Deck has %d cards, minimum is 40"%maindeckCount)
		if maindeckCount > 60:
			return OperationResult(False, "Main Deck has %d cards, maximum is 60"%maindeckCount)
		if extradeckCount > 15:
			return OperationResult(False, "Extra Deck has %d cards, maximum is 15"%extradeckCount)
		if sidedeckCount > 15:
			return OperationResult(False, "Side Deck has %d cards, maximum is 15"%sidedeckCount)
		return OperationResult(True, "")

mainDeckStart = "#main"
extraDeckStart = "#extra"
sideDeckStart = "!side"


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

	def validateDeck(self, ydkDeckList, banlistFile):
		decklist = Ydk(ydkDeckList)
		validation = decklist.getYdkErrors()
		if (validation.wasSuccessful()):
			banlist = openBanlist(banlistFile)
			validation = self.validateAgainstBanlist(decklist, banlist)

		return validation


	def validateAgainstBanlist(self, ydk, banlist):
		banlistAsLines = banlist.split("\n")

		errorMessages = []

		for card in ydk.getDeck():
			cardName = self.cardCollection.getCardNameFromId(card.cardId)
			found = False
			for line in banlistAsLines:
				if card.cardId in line:
					# This is just a way of finding how many copies are legal of a given card. Not pretty but it works.
					idCount = len(card.cardId)
					line = line[idCount+1:idCount+2]
					if line == "-":
						line = "-1"
					limit = int(line)
					# Now we check whether the max number is less than 1 (which means illegal or forbidden) 
					# or whether there's more copies of a card than the legal limit (4 copies of anything, 3 of a semi-limited, etc)
					if limit < 1 or card.copies > limit:
						if cardName == None:
							errorMessages.append("Card with id %s doesn't seem to exist."%card.cardId)
						elif limit == -1:
							errorMessages.append("%s is illegal in the format."%cardName)
						elif limit == 0:
							errorMessages.append("%s is Forbidden."%cardName)
						elif limit < card.copies:
							errorMessages.append("You are running %d copies of %s, maximum is %d."%(card.copies, cardName, limit))
					found = True
					break
			if not found:
				if cardName != None:
					errorMessages.append("%s is not legal."%cardName)
				else:
					errorMessages.append("Card with id %s is not legal or doesn't exist"%card.cardId)

		if len(errorMessages) == 0:
			return OperationResult(True, "")

		return OperationResult(False, errorMessagesToString(errorMessages))


