import urllib
import json
from urllib import parse

DB_URL = "https://www.duelingbook.com/php-scripts/load-deck.php?id=%s"

MAIN_DECK_KEY = 'main'
EXTRA_DECK_KEY = 'extra'
SIDE_DECK_KEY = 'side'
CARD_ID_KEY = 'serial_number'

def getRequest(url:str):
    header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
              'AppleWebKit/537.11 (KHTML, like Gecko) '
                            'Chrome/23.0.1271.64 Safari/537.11',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                            'Accept-Encoding': 'none',
                            'Accept-Language': 'en-US,en;q=0.8',
                            'Connection': 'keep-alive'}
    request = urllib.request.Request(url, None, header)
    return request

def getDeckAsJSON(duelingbookURL:str):
    deckId = getIdFromUrl(duelingbookURL)
    requestUrl = DB_URL % deckId
    request = getRequest(requestUrl)
    with urllib.request.urlopen(request) as page:
        return json.load(page)

def getIdFromUrl(url:str):
    return parse.parse_qs(parse.urlparse(url).query)['id'][0]
    

def duelingbookDeckToYdk(deck:dict, playerName:str):
    mainDeck = deck[MAIN_DECK_KEY]
    extraDeck = deck[EXTRA_DECK_KEY]
    sideDeck = deck[SIDE_DECK_KEY]

    deck = "#Created by %s\n" % playerName
    deck = deck + "#main\n"
    for card in mainDeck:
        deck = deck + card[CARD_ID_KEY] + "\n"
    if len(extraDeck) > 0:
        deck = deck + "#extra\n"
        for card in extraDeck:
            deck = deck + card[CARD_ID_KEY] + "\n"
    if len(sideDeck) > 0:
        deck = deck + "!side\n"
        for card in sideDeck:
            deck = deck + card[CARD_ID_KEY] + "\n"

    return deck

class DuelingbookManager:

    def getYDKFromDuelingbookURL(self, playerName:str, duelingbookURL:str):
        deck = getDeckAsJSON(duelingbookURL)
        return duelingbookDeckToYdk(deck, playerName)