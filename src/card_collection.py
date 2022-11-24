import urllib.request
from typing import List
import json
import time
import os
from PIL import Image

def getRequest():
    header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
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

def getImageRequest(imageUrl:str):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'} 
    request = urllib.request.Request(imageUrl, None, headers)
    return request

DATA = 'data'
KEY_NAME = 'name'
KEY_ID = 'id'
KEY_CARD_IMAGES = 'card_images'
KEY_IMAGE_URL = 'image_url'


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

    def getCardFromCardName(self, cardName):
        self.refreshCards()
        for card in self.cards:
            if (card.get(KEY_NAME).lower() == cardName.lower()):
                return card
        return None

    def getCardsFromPartialCardName(self, cardName):
        self.refreshCards()
        partialMatches: List[str] = []
        for card in self.cards:
            if cardName.lower() in card.get(KEY_NAME).lower():
                partialMatches.append(card.get(KEY_NAME))
        return partialMatches

    def getCardNameFromId(self, cardId):
        self.refreshCards()
        cardIdAsInt = int(cardId)
        for card in self.cards:
            if cardIdAsInt == card.get(KEY_ID):
                return card.get(KEY_NAME)
            for variant in card.get(KEY_CARD_IMAGES):
                if cardIdAsInt == variant.get(KEY_ID):
                    return card.get(KEY_NAME)

    def getCardImageFromId(self, cardId):
        self.refreshCards()
        cardIdAsInt = int(cardId)
        for card in self.cards:
            for variant in card.get(KEY_CARD_IMAGES):
                if cardIdAsInt == variant.get(KEY_ID):
                    localFile = "./img/%d.jpg"%cardIdAsInt
                    if not os.path.exists(localFile):
                        imageUrl = variant.get(KEY_IMAGE_URL)
                        request = getImageRequest(imageUrl)
                        img = Image.open(urllib.request.urlopen(request))
                        img.save(localFile)
                    return localFile
        return "./img/cardback.jpg"

    def downloadAllImages(self):
        for card in self.cards:
            for variant in card.get(KEY_CARD_IMAGES):
                self.getCardImageFromId(variant.get(KEY_ID))