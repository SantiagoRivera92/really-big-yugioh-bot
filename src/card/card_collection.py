import urllib.request
from typing import List
import json
import time
import os
from PIL import Image

def get_request():
    header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.11 (KHTML, like Gecko) '
            'Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
            }
    url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    request = urllib.request.Request(url, None, header)
    return request

def get_edison_request():
    header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.11 (KHTML, like Gecko) '
            'Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
            }
    url = "https://raw.githubusercontent.com/SantiagoRivera92/yugioh-card-errata/main/Errata%20Texts%20(Edison).json"
    request = urllib.request.Request(url, None, header)
    return request

def get_image_request(image_url:str):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'} 
    request = urllib.request.Request(image_url, None, headers)
    return request

DATA = 'data'
KEY_NAME = 'name'
KEY_ID = 'id'
KEY_CARD_IMAGES = 'card_images'
KEY_IMAGE_URL = 'image_url'

class CardCollection:

    def __init__(self):
        self.cards = []
        self.edison_errata = []
        self.timestamp = time.time()
        self.refresh_cards()

    def refresh_cards(self):
        if (len(self.cards) == 0 or time.time() - self.timestamp > 3600):
            request = get_request()
            with urllib.request.urlopen(request) as url:
                self.cards = json.loads(url.read().decode()).get(DATA)
                self.timestamp = time.time()
        if len(self.edison_errata) == 0:
            request = get_edison_request()
            with urllib.request.urlopen(request) as url:
                self.edison_errata = json.loads(url.read().decode())
    
    
    def get_card_from_card_name_edison(self, cardName):
        card = self.get_card_from_card_name(cardName)
        if card is not None:
            _id = card.get('id')
            # Find the Edison card text
            text = None
            for errata in self.edison_errata:
                if errata.get('id') == _id:
                    text = errata.get('last_legal_text')
                    card['desc'] = text
                    card['is_edison_errata'] = True
                    return card 
        return card

        
    
    def get_card_from_card_name(self, cardName):
        self.refresh_cards()
        for card in self.cards:
            if (card.get(KEY_NAME).lower() == cardName.lower()):
                return card
        return None

    def get_cards_from_partial_card_name(self, cardName):
        self.refresh_cards()
        partialMatches: List[str] = []
        for card in self.cards:
            if cardName.lower() in card.get(KEY_NAME).lower():
                partialMatches.append(card.get(KEY_NAME))
        return partialMatches

    def get_card_name_from_id(self, card_id):
        self.refresh_cards()
        card_id_as_int = int(card_id)
        for card in self.cards:
            if card_id_as_int == card.get(KEY_ID):
                return card.get(KEY_NAME)
            for variant in card.get(KEY_CARD_IMAGES):
                if card_id_as_int == variant.get(KEY_ID):
                    return card.get(KEY_NAME)

    def get_card_image_from_id(self, card_id):
        self.refresh_cards()
        card_id_as_int = int(card_id)
        for card in self.cards:
            for variant in card.get(KEY_CARD_IMAGES):
                if card_id_as_int == variant.get(KEY_ID):
                    local_file = "./img/card/%d.jpg"%card_id_as_int
                    if not os.path.exists(local_file):
                        image_url = variant.get(KEY_IMAGE_URL)
                        request = get_image_request(image_url)
                        with Image.open(urllib.request.urlopen(request)) as img:
                            img.save(local_file)
                    return local_file
        return "./img/card/cardback.jpg"