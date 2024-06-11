import os

from src.deck.deck_analysis import DeckAnalysisManager


if __name__ == "__main__":
    server_id = 1037146331258556488
    manager = DeckAnalysisManager(server_id)
    deck_dir = f"ydk/{server_id}/Edison/decks"
    
    deck_filenames = [os.path.join(deck_dir, filename) for filename in os.listdir(deck_dir)]
    deck_filenames = [filename for filename in deck_filenames if filename.endswith(".ydk")]
    
    analysis_result = manager.analyze_decks(deck_filenames)
    print(analysis_result.format_results())