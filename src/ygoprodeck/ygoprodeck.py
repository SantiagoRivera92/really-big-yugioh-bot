import requests
import re
from typing import List, Optional
from src.deck.deck_validation import Card, Deck

class YgoprodeckManager:
    def extract_deck(self, url: str) -> Optional[Deck]:
        # Check if the URL contains the necessary substring
        if "ygoprodeck.com/deck/" not in url:
            return None

        # Download the HTML content
        response = requests.get(url)
        html_content = response.text

        # Extract the relevant parts using regex
        main_deck_match = re.search(r"var maindeckjs = '(\[.*?\])';", html_content)
        extra_deck_match = re.search(r"var extradeckjs = '(\[.*?\])';", html_content)
        side_deck_match = re.search(r"var sidedeckjs = '(\[.*?\])';", html_content)
        deck_name_match = re.search(r"var deckname = \"(.*?)\";", html_content)

        # If any part is missing, return None
        if not all([main_deck_match, extra_deck_match, side_deck_match, deck_name_match]):
            return None

        # Extracted strings from the HTML
        main_deck_str = main_deck_match.group(1)
        extra_deck_str = extra_deck_match.group(1)
        side_deck_str = side_deck_match.group(1)
        deck_name = deck_name_match.group(1)

        # Convert strings to lists of card IDs
        main_deck_ids = eval(main_deck_str)
        extra_deck_ids = eval(extra_deck_str)
        side_deck_ids = eval(side_deck_str)

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