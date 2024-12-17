import math
import os
from PIL import Image

MAIN_DECK_MARGIN = 32

CARD_WIDTH = 813
CARD_HEIGHT = 1185

def draw_pool(cards, card_id_to_image):
    deck_count = len(cards)
    rows = math.ceil(deck_count/10)
    if deck_count >= 10:
        width = CARD_WIDTH + 9 * (CARD_WIDTH + MAIN_DECK_MARGIN)
    else:
        width = CARD_WIDTH + (deck_count - 1) * (CARD_WIDTH + MAIN_DECK_MARGIN)
    
    pool_image = Image.new("RGBA", (width, rows*(CARD_HEIGHT + MAIN_DECK_MARGIN)), (0,0,0,0))
    
    for row in range(rows):
        for col in range(10):
            index = row * 10 + col
            if index < deck_count:
                card_id = cards[index]
                image_url = card_id_to_image.get(card_id)
                img = Image.open(image_url)
                if img.size != (CARD_WIDTH, CARD_HEIGHT):
                    img = img.resize((CARD_WIDTH, CARD_HEIGHT))
                x = col * (CARD_WIDTH + MAIN_DECK_MARGIN)
                y = row * (CARD_HEIGHT + MAIN_DECK_MARGIN)
                pool_image.paste(img, (round(x), round(y)))
    return pool_image

class DraftPoolAsImageGenerator:

    def __init__(self, card_collection, server_id):
        self.card_collection = card_collection
        self.server_id = server_id
    
    def build_pool_image(self, pool, filename):
        card_id_to_image = {}

        for card in pool:
            card_id_to_image[card] = self.card_collection.get_card_image_from_id(card)

        # Load the background image
        main_deck_image = draw_pool(pool, card_id_to_image)

        # Convert to RGB to make the jpg image
        background_image = main_deck_image.convert("RGB")

        # Save the final image
        os.makedirs(f"./img/pools/{self.server_id}", exist_ok=True)
        output_filename = f"./img/pools/{self.server_id}/{filename}.jpg"
        background_image.save(output_filename)
        return output_filename