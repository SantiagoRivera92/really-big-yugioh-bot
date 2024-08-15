import re
import json
from typing import List, Optional, Union
import requests
from src.deck.deck_validation import Card, Deck
from src.utils.utils import OperationResult

class YgoprodeckManager:
    def extract_deck(self, url: str) -> Optional[Union[Deck | OperationResult]]:
        # Check if the URL contains the necessary substring
        if "ygoprodeck.com/deck/" not in url:
            return OperationResult(False, f"{url} is not a YGOPRODECK deck URL.")

        # Download the HTML content
        response = requests.get(url)
        html_content = response.text

        # Extract the relevant parts using regex
        main_deck_match = re.search(r"var maindeckjs = '(\[.*?\])';", html_content)
        extra_deck_match = re.search(r"var extradeckjs = '(\[.*?\])';", html_content)
        side_deck_match = re.search(r"var sidedeckjs = '(\[.*?\])';", html_content)
        deck_name_match = re.search(r"var deckname = \"(.*?)\";", html_content)

        if not main_deck_match:
            return OperationResult(False, "Provided URL was a YGOPRODECK deck URL but it did not contain a Main Deck")

        main_deck_str = main_deck_match.group(1)
        main_deck_ids = json.loads(main_deck_str)
        
        if extra_deck_match:
            extra_deck_str = extra_deck_match.group(1)
            extra_deck_ids = json.loads(extra_deck_str)
        else:
            extra_deck_ids = []
            
        if side_deck_match:
            side_deck_str = side_deck_match.group(1)
            side_deck_ids = json.loads(side_deck_str)
        else:
            side_deck_ids = []
            
        if deck_name_match:
            deck_name = deck_name_match.group(1)
        else:
            deck_name = ""

        # Helper function to convert list of ids to list of Card objects
        def convert_to_cards(card_ids: List[str]) -> List[Card]:
            card_dict = {}
            for card_id in card_ids:
                if card_id in card_dict:
                    card_dict[card_id].add_copy()
                else:
                    card_dict[card_id] = Card(card_id, 1)
            return list(card_dict.values())

        # Create lists of Card objects
        main_deck = convert_to_cards(main_deck_ids)
        extra_deck = convert_to_cards(extra_deck_ids)
        side_deck = convert_to_cards(side_deck_ids)

        # Create and return the Deck object
        return Deck(main=main_deck, extra=extra_deck, side=side_deck, name=deck_name)