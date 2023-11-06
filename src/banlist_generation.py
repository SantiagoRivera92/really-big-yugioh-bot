import os
from src.utils import OperationResult
import src.strings as Strings
import urllib.request, json, datetime
from os import walk

header= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
				'AppleWebKit/537.11 (KHTML, like Gecko) '
				'Chrome/23.0.1271.64 Safari/537.11',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
				'Accept-Encoding': 'none',
				'Accept-Language': 'en-US,en;q=0.8',
				'Connection': 'keep-alive'}

ignoredSets = [
	"DL1", "DL2", "DL3", "DL4", "DL5", "DL6", "DL7", "DL8", "DL9", "DL10", "DL11", "DL12", "DL13", "DL14", "DL15", "DL16", "DL17", "DL18",
	"HL1", "HL2", "HL03", "HL04", "HL05", "HL06", "HL07", 
	"LART", "RA01",
	"DTP1","DT01","DT02","DT03", "DT04", "DT05", "DT06", "DT07", 
	"OP01", "OP02", "OP03", "OP04", "OP05", "OP06", "OP07", "OP08", "OP09", "OP10", "OP11", "OP12", "OP13", "OP14", "OP15", "OP16", "OP17", "OP18", "OP19", "OP20", "OP21", "OP22", "OP23", "OP24", "OP25", "OP26", "OP27", "OP28", "OP29", "OP30"
	]


def dateFromString(dateAsString):
	year = int(dateAsString[0:4])
	month = int(dateAsString[5:7])
	day = int(dateAsString[8:10])
	return datetime.datetime(year, month, day)

def getFullSetList():
	setsUrl = "https://db.ygoprodeck.com/api/v7/cardsets.php"
	setsRequest = urllib.request.Request(setsUrl, None, header)
	with urllib.request.urlopen(setsRequest) as url:
		return json.loads(url.read().decode())

def getSetList(date):
	sets = getFullSetList()
	legalSets = []
	for tcgSet in sets:
		if tcgSet['set_code'] == "BLCR":
			tcgSet['tcg_date'] = "2022-11-18"
		if 'tcg_date' in tcgSet:
			setReleaseDateAsString = tcgSet['tcg_date']
			releaseYear = int(setReleaseDateAsString[0:4])
			releaseMonth = int(setReleaseDateAsString[5:7])
			releaseDay = int(setReleaseDateAsString[8:10])
			setReleaseDate = datetime.datetime(releaseYear, releaseMonth, releaseDay)
			if setReleaseDate <= date:
				code = tcgSet['set_code']
				ignore = False
				for ignoredCode in ignoredSets:
					if (ignoredCode == code):
						ignore = True
				if not ignore:
					legalSets.append(tcgSet['set_name'])
	setList = list(dict.fromkeys(legalSets))
	return setList

def findBanlist(date):
	filenames = getBanlistFileNames()
	lastbanlist = "2002-03-01.json"
	for filename in filenames:
		banlistDate = dateFromString(filename)
		if (banlistDate > date):
			break
		else:
			lastbanlist = filename
	return lastbanlist

def getBanlistFileNames():
	filenames = next(walk("./banlist"), (None, None, []))[2]
	return filenames

def getBanlistObject(banlistFile):
	with open("./banlist/%s"%banlistFile) as jsonFile:
		banlist = json.load(jsonFile)
		jsonFile.close()
		return banlist

def getCardListFromAPI():
	cardsUrl = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
	cardsRequest = urllib.request.Request(cardsUrl, None, header)
	with urllib.request.urlopen(cardsRequest) as url:
		return json.loads(url.read().decode()).get('data')

def getDateAsString(date):
	return "%04d-%02d-%02.d"%(date.year, date.month, date.day)

class BanlistConverter:

	def __init__(self, cardCollection):
		self.cardCollection = cardCollection

	def createFolderForServer(self, serverId):
		folderName = "./lflist/%d" % serverId
		if not os.path.exists(folderName):
			os.makedirs(folderName)

	def writeBanlist(self, formatName, lflistFile, serverId):
		self.createFolderForServer(serverId)
		filename = "./lflist/%d/%s.lflist.conf" % (serverId, formatName)
		with open(filename, 'w', encoding="utf-8") as banlist:
			banlistAsLines = lflistFile.split("\n")
			for line in banlistAsLines:
				line = line.replace("\n", "").replace("\r", "")
				if len(line) > 0:
					banlist.write(line)
					banlist.write("\n")
		return OperationResult(True, Strings.BOT_MESSAGE_FORMAT_ADDED)

	def fixBanlist(self, formatName, serverId, cardId, cardName, newStatus):
		filename = "./lflist/%d/%s.lflist.conf" % (serverId, formatName)
		lines = []
		with open(filename, encoding="utf-8") as banlist:
			banlistAsLines = banlist.read().split("\n")
			for line in banlistAsLines:
				if not str(cardId) in line:
					if len(line) > 0:
						lines.append(line)
			lines.append("%d %d -- %s"%(cardId, newStatus, cardName))
		with open(filename, 'w', encoding="utf-8") as banlist:
			for line in lines:
				banlist.write(line)
				banlist.write("\n")
		return OperationResult(True, Strings.BOT_MESSAGE_CARD_ADDED_TO_BANLIST)

	def deleteBanlist(self, formatName, serverId):
		filename = "./lflist/%d/%s.lflist.conf" % (serverId, formatName)
		if os.path.exists(filename):
			os.remove(filename)
			return OperationResult(True, "")
		return OperationResult(False, Strings.ERROR_BANLIST_FILE_MISSING)

class BanlistGenerator:

	def __init__(self, serverId:int):
		self.serverId = serverId

	def validateDate(self, dateAsString:str):
		year = dateAsString[0:4]
		month = dateAsString[5:7]
		day = dateAsString[8:10]
		
		if not year.isnumeric():
			return OperationResult(False, "Date must be in format YYYY-MM-DD")
		if not month.isnumeric():
			return OperationResult(False, "Date must be in format YYYY-MM-DD")
		if not day.isnumeric():
			return OperationResult(False, "Date must be in format YYYY-MM-DD")

		year = int(year)
		month = int(month)
		day = int(day)

		try:
			date = dateFromString(dateAsString)
		except ValueError:
			return OperationResult(False, "The date is not valid")

		firstDate = dateFromString("2002-03-08")
		now = datetime.datetime.now()

		if date > now:
			return OperationResult(False, "This bot cannot predict the future. Yet.")
		if date < firstDate:
			return OperationResult(False, "I, too, long for a time when Yu-Gi-Oh didn't exist.")

		return OperationResult(True, "")

	def getCardList(self, setList, banlistFile):
		banlist = getBanlistObject(banlistFile)
		cards = getCardListFromAPI()
		cardList = []
		for card in cards:
			if card.get('card_sets') != None:
				includeInList = False
				for cardSet in card['card_sets']:
					setName = cardSet['set_name']
					for validSet in setList:
						if validSet == setName:
							includeInList = True
				if includeInList:
					banlistStatus = 3
					for forbiddenCard in banlist.get('forbidden'):
						if forbiddenCard == card['name']:
							banlistStatus = 0
					for limitedCard in banlist.get('limited'):
						if limitedCard == card['name']:
							banlistStatus = 1
					for semiCard in banlist.get('semilimited'):
						if semiCard == card['name']:
							banlistStatus = 2
					simpleCard = {}
					simpleCard['name'] = card['name']
					ids = []
					images = card['card_images']
					if images != None:
						for variant in images:
							ids.append(variant['id'])
					else:
						ids.append(card['id'])
					simpleCard['id'] = ids
					simpleCard['status'] = banlistStatus
					cardList.append(simpleCard)
		return cardList

	def printCards(self, cardList, date, name):
		if not os.path.exists("./lflist/%d"%self.serverId):
			os.makedirs("./lflist/%d" % self.serverId)
		filename = "./lflist/%d/%s.lflist.conf" % (self.serverId, name)
		with open(filename, 'w', encoding="utf-8") as outfile:		
			if len(name) > 0:
				outfile.write("#[%s format]\n"%name)
				outfile.write("!%s (%04d.%02d.%02d)\n" % (name, date.year, date.month, date.day))
			else:
				outfile.write("#[%04d.%02d.%02d]\n" % (date.year, date.month, date.day))
				outfile.write("!%04d.%02d.%02d\n" % (date.year, date.month, date.day))
			outfile.write("$whitelist\n")
			for card in cardList:
				for cardId in card['id']:
					line = "%d %d-- %s\n" % (cardId, card.get('status'), card.get('name'))
					outfile.write(line)

	def generateBanlist(self, dateAsString: str, name: str):
		#try:
		date = dateFromString(dateAsString)
		banlistFile = findBanlist(date)
		setList = getSetList(date)
		cardList = self.getCardList(setList, banlistFile)
		self.printCards(cardList, date, name)
		return OperationResult(True, "./lflist/%d/%s.lflist.conf" % (self.serverId, name))
		#except:
		#	return OperationResult(False, "Something wrong happened during banlist generation")

	def generateAdvancedBanlist(self):
		date = datetime.datetime.now()
		banlistFile = findBanlist(date)
		setList = getFullSetList(date)
		cardList = self.getCardList(setList, banlistFile)
		self.printCards(cardList, date, "Advanced")