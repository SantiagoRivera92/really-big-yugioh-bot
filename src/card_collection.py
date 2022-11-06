import urllib.request
import json
import time

def getRequest():
	header= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
				'AppleWebKit/537.11 (KHTML, like Gecko) '
				'Chrome/23.0.1271.64 Safari/537.11',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
				'Accept-Encoding': 'none',
				'Accept-Language': 'en-US,en;q=0.8',
				'Connection': 'keep-alive'}
	url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
	request = urllib.request.Request(url, None, header)
	return request

DATA = 'data'

class CardCollection:
	
	def __init__(self):
		self.cards = []
		self.timestamp = time.time()
		self.refreshCards()


	def refreshCards(self):
		request = getRequest()
		if (len(self.cards) == 0 or time.time() - self.timestamp > 3600):
			with urllib.request.urlopen(request) as url:
				self.cards = json.loads(url.read().decode()).get(DATA)
				self.timestamp = time.time()

	def getCardFromCardName(self,cardName):
		self.refreshCards()
		for card in self.cards:
			if(card.get('name').lower() == cardName.lower()):
				return card
		return None

	def getCardsFromPartialCardName(self, cardName):
		self.refreshCards()
		partialMatches = []
		for card in self.cards:
			if cardName.lower() in card.get('name').lower():
				partialMatches.append(card.get('name'))
		return partialMatches


	def getCardNameFromId(self, cardId):
		self.refreshCards()
		cardIdAsInt = int(cardId)
		for card in self.cards:
			if cardIdAsInt == card.get('id'):
				return card.get('name')
			for variant in card.get('card_images'):
				if cardIdAsInt == variant.get('id'):
					return card.get('name')
