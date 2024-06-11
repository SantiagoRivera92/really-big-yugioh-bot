import json
import os
import textwrap
from typing import List, Dict
import matplotlib.pyplot as plt
from src.deck.deck_validation import Deck, Ydk


class SampleDeck:
    def __init__(self, deck: Deck, deck_name: str):
        self.deck = deck
        self.deck_name = deck_name

class DeckAnalysis:
    def __init__(self, deck_name: str, deck_count: int):
        self.deck_name = deck_name
        self.deck_count = deck_count

class DeckAnalysisResults:
    def __init__(self, analyses: List[DeckAnalysis]):
        self.analyses = analyses

    def count_results(self) -> int:
        return sum(analysis.deck_count for analysis in self.analyses)
    
    def format_results(self) -> str:
        total_count = self.count_results()
        lines = [
            f"{analysis.deck_name}: {analysis.deck_count} ({(analysis.deck_count * 100 / total_count):.2f}%)"
            for analysis in self.analyses
        ]
        return "\n".join(lines)

class DeckAnalysisManager:
    def __init__(self, server_id: int):
        self.server_id = server_id
        self.json_file = f"json/decks/{self.server_id}/analysis.json"
        self.ensure_directory_and_file()
        self.sample_decks = self.load_sample_decks(self.json_file)

    def ensure_directory_and_file(self):
        directory = os.path.dirname(self.json_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.isfile(self.json_file):
            with open(self.json_file, 'w', encoding="utf-8") as file:
                json.dump([], file)  # Initialize with an empty array

    def load_sample_decks(self, json_file: str) -> List[SampleDeck]:
        with open(json_file, 'r', encoding="utf-8") as file:
            deck_data = json.load(file)
        sample_decks = []
        for entry in deck_data:
            with open(f"json/decks/{self.server_id}/decks/{entry['deck_location']}", 'r', encoding="utf-8") as deck_file:
                deck_content = deck_file.read()
            ydk = Ydk(deck_content)
            deck = ydk.get_deck()
            sample_decks.append(SampleDeck(deck, entry['deck_name']))
        return sample_decks


    def analyze_decks(self, deck_filenames: List[str]) -> DeckAnalysisResults:
        sample_deck_counts: Dict[str, DeckAnalysis] = {}
        
        for filename in deck_filenames:
            with open(filename, 'r', encoding="utf-8") as file:
                deck_content = file.read()
            
            ydk = Ydk(deck_content)  
            deck = ydk.get_deck()
            deck_analyzed = False

            for sample_deck in self.sample_decks:
                if self.compare_decks(deck, sample_deck.deck):
                    if sample_deck.deck_name in sample_deck_counts:
                        sample_deck_counts[sample_deck.deck_name].deck_count += 1
                    else:
                        sample_deck_counts[sample_deck.deck_name] = DeckAnalysis(sample_deck.deck_name, 1)
                    deck_analyzed = True
                    break

            if not deck_analyzed:
                if "Other" in sample_deck_counts:
                    sample_deck_counts["Other"].deck_count += 1
                else:
                    sample_deck_counts["Other"] = DeckAnalysis("Other", 1)
                print(f"{filename} could not be analyzed. Review manually.")

        deck_analyses = list(sample_deck_counts.values())
        deck_analyses.sort(key=lambda x: x.deck_count, reverse=True)
        return DeckAnalysisResults(deck_analyses)

    def compare_decks(self, deck1: Deck, deck2: Deck) -> bool:
        deck1_main_ids = {int(card.card_id) for card in deck1.get_main_deck()}
        deck2_main_ids = {int(card.card_id) for card in deck2.get_main_deck()}

        for card_id in deck2_main_ids:
            if card_id not in deck1_main_ids:
                return False

        return True


    def create_pie_chart(self, results: DeckAnalysisResults, floor=3, output_filename="img/plot/plot.jpg"):
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_filename)
        os.makedirs(output_dir, exist_ok=True)

        # Separate decks that meet the floor and those that don't
        decks = results.analyses
        above_floor = [deck for deck in decks if deck.deck_count >= floor]
        below_floor = [deck for deck in decks if deck.deck_count < floor]

        # Sum the counts for the 'Other' category
        other_count = sum(deck.deck_count for deck in below_floor)
        
        # If there are any below-floor decks or an existing "Other" deck, include "Other" category
        if other_count > 0 or any(deck.deck_name == "Other" for deck in above_floor):
            # Combine with existing "Other" count if it exists
            existing_other = next((deck for deck in above_floor if deck.deck_name == "Other"), None)
            if existing_other:
                existing_other.deck_count += other_count
            else:
                above_floor.append(DeckAnalysis("Other", other_count))

        # Ensure "Other" is the last category
        above_floor = [deck for deck in above_floor if deck.deck_name != "Other"]
        above_floor.append(DeckAnalysis("Other", other_count))

        # Prepare data for pie chart
        labels = [deck.deck_name for deck in above_floor]
        sizes = [deck.deck_count for deck in above_floor]

        # Wrap text for labels to fit within the chart
        wrapped_labels = [textwrap.fill(label, 15) for label in labels]

        # Create pie chart
        plt.figure(figsize=(16, 16))  # Increase size to provide more space for labels
        wedges, texts, autotexts = plt.pie(
            sizes, labels=wrapped_labels, autopct='%1.1f%%', startangle=90, counterclock=False, pctdistance=0.6
        )
        
        # Adjust the position of the labels
        for text in texts:
            text.set_fontsize(10)  # Adjust font size if needed
            text.set_horizontalalignment('center')  # Center-align the text

        for autotext in autotexts:
            autotext.set_fontsize(10)  # Adjust font size if needed
            autotext.set_color('white')

        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Save the pie chart as a JPG image
        plt.savefig(output_filename, format='jpg', bbox_inches='tight')
        plt.close()
        return output_filename