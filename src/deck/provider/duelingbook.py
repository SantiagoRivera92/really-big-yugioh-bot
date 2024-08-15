import urllib
import json
from urllib import parse
from src.utils.utils import OperationResult

DB_URL = "https://www.duelingbook.com/php-scripts/load-deck.php?id=%s&app=FormatLibrary"

MAIN_DECK_KEY = 'main'
EXTRA_DECK_KEY = 'extra'
SIDE_DECK_KEY = 'side'
CARD_ID_KEY = 'serial_number'

def get_request(url:str):
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

def get_deck_as_json(db_url:str):
    deck_id = get_id_from_url(db_url)
    request_url = DB_URL % deck_id
    request = get_request(request_url)
    with urllib.request.urlopen(request) as page:
        return json.load(page)

def get_id_from_url(url:str):
    return parse.parse_qs(parse.urlparse(url).query)['id'][0]
    
def db_to_ydk(deck:dict, player_name:str) -> str:
    main = deck[MAIN_DECK_KEY]
    extra = deck[EXTRA_DECK_KEY]
    side = deck[SIDE_DECK_KEY]

    ydk = f"#Created by {player_name}\n"
    ydk = ydk + "#main\n"
    for card in main:
        ydk = ydk + card[CARD_ID_KEY] + "\n"
    if len(extra) > 0:
        ydk = ydk + "#extra\n"
        for card in extra:
            ydk = ydk + card[CARD_ID_KEY] + "\n"
    if len(side) > 0:
        ydk = ydk + "!side\n"
        for card in side:
            ydk = ydk + card[CARD_ID_KEY] + "\n"

    return ydk

class DuelingbookManager:

    def get_ydk_from_db(self, player_name:str, db_url:str):
        deck = get_deck_as_json(db_url)
        return db_to_ydk(deck, player_name)
    
    def get_deck_name_from_db(self, db_url:str):
        deck = get_deck_as_json(db_url)
        return deck['name']

    def is_valid_url(self, db_url:str):
        if "duelingbook.com/deck" in db_url:
            if "id=" in db_url:
                _id = get_id_from_url(db_url)
                if _id.isdigit():
                    return OperationResult(True, "")
                return OperationResult(False, "Duelingbook URL ids are numbers")
            return OperationResult(False, "This Duelingbook URL doesn't have an ID")
        return OperationResult(False, "This is not a Duelingbook URL. Duelingbook URLs look like duelingbook.com/deck?id=11963395")