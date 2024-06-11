import time
import math
from PIL import Image, ImageDraw, ImageFont

BACKGROUND_COLOR = (0, 0, 0)

MAIN_DECK_MARGIN = 8
HORIZONTAL_MARGIN = 148

CARD_WIDTH = 164
CARD_HEIGHT = 242
VERTICAL_MARGIN = 233

IMAGE_LIMIT_MARGIN = 8
IMAGE_LIMIT_SIZE = int(0.25 * CARD_HEIGHT)

FONT_SIZE_MEDIUM = 86
FONT_SIZE_LARGE = 120

FONT_FILE = "font/Yu-Gi-Oh! Matrix Regular Small Caps 1.ttf"
DECKLIST_BACKGROUND_FILE = "./img/static/decklist_background.png"

IMAGE_FORBIDDEN = "./img/static/forbidden.png"
IMAGE_LIMITED = "./img/static/limited.png"
IMAGE_SEMILIMITED = "./img/static/semi-limited.png"

def get_status_in_banlist(card_id, banlist):
    banlist_as_lines = banlist.split("\n")
    card_id = int(card_id)
    id_as_string = str(card_id)
    for line in banlist_as_lines:
        id_in_line = line.split(' ')[0]
        if id_as_string == id_in_line:
            id_count = int(math.log10(card_id))+1
            line = line[id_count+1:id_count+2]
            if line == "-":
                line = "-1"
            return int(line)
    return -1

def draw_main_deck(deck_images, main_deck_width, banlist, card_id_to_image):
    deck_count = len(deck_images)
    rows = math.ceil(deck_count / 10)  # Number of rows in the main deck

    deck_image = Image.new("RGBA", (main_deck_width, rows * (CARD_HEIGHT + MAIN_DECK_MARGIN)), (0, 0, 0, 0))

    img_forbidden = Image.open(IMAGE_FORBIDDEN).convert("RGBA")
    img_limited = Image.open(IMAGE_LIMITED).convert("RGBA")
    img_semilimited = Image.open(IMAGE_SEMILIMITED).convert("RGBA")
    img_forbidden = img_forbidden.resize((IMAGE_LIMIT_SIZE, IMAGE_LIMIT_SIZE))
    img_limited = img_limited.resize((IMAGE_LIMIT_SIZE, IMAGE_LIMIT_SIZE))
    img_semilimited = img_semilimited.resize((IMAGE_LIMIT_SIZE, IMAGE_LIMIT_SIZE))

    for row in range(rows):
        for col in range(10):
            index = row * 10 + col
            if index < deck_count:
                card_id = deck_images[index]
                image_url = card_id_to_image.get(card_id)
                img = Image.open(image_url)
                if img.size != (CARD_WIDTH, CARD_HEIGHT):
                    img = img.resize((CARD_WIDTH, CARD_HEIGHT))
                x = col * (CARD_WIDTH + MAIN_DECK_MARGIN)
                y = row * (CARD_HEIGHT + MAIN_DECK_MARGIN)
                deck_image.paste(img, (round(x), round(y)))

                status = get_status_in_banlist(card_id, banlist)
                if status <= 0:
                    deck_image.paste(img_forbidden, (round(x + IMAGE_LIMIT_MARGIN), round(y + IMAGE_LIMIT_MARGIN)), img_forbidden)
                elif status == 1:
                    deck_image.paste(img_limited, (round(x + IMAGE_LIMIT_MARGIN), round(y + IMAGE_LIMIT_MARGIN)), img_limited)
                elif status == 2:
                    deck_image.paste(img_semilimited, (round(x + IMAGE_LIMIT_MARGIN), round(y + IMAGE_LIMIT_MARGIN)), img_semilimited)

    return deck_image

def draw_extra_side_deck(deck_images, deck_type, main_deck_width, banlist, card_id_to_image):
    deck_count = len(deck_images)
    if deck_count < 1:
        return None
    extra_side_deck_margin = (10 * CARD_WIDTH + 9 * MAIN_DECK_MARGIN - deck_count * CARD_WIDTH) / (deck_count - 1)

    deck_image = Image.new("RGBA", (main_deck_width, CARD_HEIGHT), (0, 0, 0, 0))

    img_forbidden = Image.open(IMAGE_FORBIDDEN).convert("RGBA")
    img_limited = Image.open(IMAGE_LIMITED).convert("RGBA")
    img_semilimited = Image.open(IMAGE_SEMILIMITED).convert("RGBA")
    img_forbidden = img_forbidden.resize((IMAGE_LIMIT_SIZE, IMAGE_LIMIT_SIZE))
    img_limited = img_limited.resize((IMAGE_LIMIT_SIZE, IMAGE_LIMIT_SIZE))
    img_semilimited = img_semilimited.resize((IMAGE_LIMIT_SIZE, IMAGE_LIMIT_SIZE))

    for i, card_id in enumerate(deck_images):
        image_url = card_id_to_image.get(card_id)
        img = Image.open(image_url)
        if img.size != (CARD_WIDTH, CARD_HEIGHT):
            img = img.resize((CARD_WIDTH, CARD_HEIGHT))
        x = MAIN_DECK_MARGIN + i * CARD_WIDTH + i * extra_side_deck_margin
        y = 0
        deck_image.paste(img, (round(x), round(y)))

        status = get_status_in_banlist(card_id, banlist)
        if status <= 0:
            deck_image.paste(img_forbidden, (round(x + IMAGE_LIMIT_MARGIN), round(y + IMAGE_LIMIT_MARGIN)), img_forbidden)
        elif status == 1:
            deck_image.paste(img_limited, (round(x + IMAGE_LIMIT_MARGIN), round(y + IMAGE_LIMIT_MARGIN)), img_limited)
        elif status == 2:
            deck_image.paste(img_semilimited, (round(x + IMAGE_LIMIT_MARGIN), round(y + IMAGE_LIMIT_MARGIN)), img_semilimited)

    return deck_image

    
def draw_text(text, font_size):
    font = ImageFont.truetype(FONT_FILE, font_size)
    text_width = font.getlength(text)
    text_box_width = text_width + 8
    text_box_height = font_size
    text_box = Image.new("RGBA", (round(text_box_width), round(text_box_height)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_box)

    # Calculate text position
    text_x = 8
    text_y = 0

    # Draw text
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
    
    return text_box
    

def draw_text_boxes(deck_name, deck_format):
    deck_format_text = "Format:"
    
    deck_name_value_text = draw_text(deck_name, FONT_SIZE_LARGE)
    deck_format_text = draw_text(deck_format_text, FONT_SIZE_MEDIUM)
    deck_format_value_text = draw_text(f"  {deck_format}", FONT_SIZE_LARGE)
    
    final_image = append_images_vertically(deck_name_value_text, deck_format_text, margin=64)
    final_image = append_images_vertically(final_image, deck_format_value_text, margin=0)
    
    return final_image

def draw_disclaimer():
    text_1 = "Deck image provided by"
    text_2 = "Really Big Yu-Gi-Oh Bot"
    
    draw1 = draw_text(text_1, FONT_SIZE_MEDIUM)
    draw2 = draw_text(text_2, FONT_SIZE_LARGE)
    return append_images_vertically(draw1, draw2, margin=0)


def append_images_vertically(image1, image2, margin=8):
    if image1 is None:
        if image2 is None:
            return None
        return image2
    
    if image2 is None:
        return image1
    
    width = max(image1.width, image2.width)
    height = image1.height + margin + image2.height
    new_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (0, image1.height + margin))
    return new_image

class DeckAsImageGenerator:

    def __init__(self, card_collection):
        self.card_collection = card_collection
    
    def build_image_with_format(self, deck, filename, deckname, formatname, banlist_file):
        start_time = time.time()

        with open(banlist_file, encoding="utf-8") as file:
            banlist = file.read()

        card_id_to_image = {}

        # Populate the main_deck_images with card IDs and update the card_id_to_image set
        main_deck_images = []
        for card in deck.get_main_deck():
            main_deck_images.extend([card.card_id] * card.copies)
            card_id_to_image[card.card_id] = self.card_collection.get_card_image_from_id(card.card_id)

        # Populate the extra_deck_images with card IDs and update the card_id_to_image set
        extra_deck_images = []
        for card in deck.get_extra_deck():
            extra_deck_images.extend([card.card_id] * card.copies)
            card_id_to_image[card.card_id] = self.card_collection.get_card_image_from_id(card.card_id)

        # Populate the side_deck_images with card IDs and update the card_id_to_image set
        side_deck_images = []
        for card in deck.get_side_deck():
            side_deck_images.extend([card.card_id] * card.copies)
            card_id_to_image[card.card_id] = self.card_collection.get_card_image_from_id(card.card_id)

        main_deck_width = 10 * CARD_WIDTH + 9 * MAIN_DECK_MARGIN

        # Load the background image
        background_image = Image.open(DECKLIST_BACKGROUND_FILE)
        bg_width, bg_height = background_image.size


        main_deck_image = draw_main_deck(main_deck_images, main_deck_width, banlist, card_id_to_image)
        extra_deck_image = draw_extra_side_deck(extra_deck_images, "Extra Deck", main_deck_width, banlist, card_id_to_image)
        side_deck_image = draw_extra_side_deck(side_deck_images, "Side Deck", main_deck_width, banlist, card_id_to_image)

        # Append images vertically
        final_image = main_deck_image
        final_image = append_images_vertically(final_image, extra_deck_image, margin=32)
        final_image = append_images_vertically(final_image, side_deck_image, margin=32)

        # Calculate position to paste the deck image onto the background
        final_image_width, final_image_height = final_image.size
        paste_x = bg_width - final_image_width - HORIZONTAL_MARGIN
        paste_y = (bg_height - final_image_height) // 2

        # Paste the deck image onto the background
        background_image.paste(final_image, (round(paste_x), round(paste_y)), final_image)
        
        # Add the deck metadata
        deck_metadata = draw_text_boxes(deckname, formatname)
        
        background_image.paste(deck_metadata, (round(HORIZONTAL_MARGIN), round(VERTICAL_MARGIN)), deck_metadata)

        disclaimer = draw_disclaimer()
        _, disclaimer_height = disclaimer.size
        background_image.paste(disclaimer, (round(HORIZONTAL_MARGIN), round(bg_height - disclaimer_height - VERTICAL_MARGIN)), disclaimer)

        # Convert to RGB to make the jpg image
        background_image = background_image.convert("RGB")

        # Save the final image
        output_filename = f"./img/decks/{filename}.jpg"
        background_image.save(output_filename)
        end_time = time.time() - start_time
        print(f"Time to generate the deck \"{filename}\": {end_time:.3f} seconds")
        return output_filename