import time
import math
from PIL import Image, ImageDraw, ImageFont

BACKGROUND_COLOR = (0, 0, 0)

MAIN_DECK_MARGIN = 8
HORIZONTAL_MARGIN = 148

CARD_WIDTH = 168
CARD_HEIGHT = 246

IMAGE_LIMIT_MARGIN = 8
IMAGE_LIMIT_SIZE = int(0.25 * CARD_HEIGHT)

FONT_FILE = "font/Roboto-Medium.ttf"
DECKLIST_BACKGROUND_FILE = "./img/static/decklist_background.png"

IMAGE_FORBIDDEN = "./img/static/forbidden.png"
IMAGE_LIMITED = "./img/static/limited.png"
IMAGE_SEMILIMITED = "./img/static/semi-limited.png"

def draw_deck_text_box(deck_type, has_deck, deck_count, main_deck_width):
    if not has_deck:
        return None

    text = f"{deck_type}: {deck_count}"

    font_size = 36
    return draw_text(text, font_size, main_deck_width, True)


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

    
def draw_text(text, font_size, width, with_rectangle):
    font = ImageFont.truetype(FONT_FILE, font_size)
    text_width, text_height = font.getsize(text)
    if width:
        text_box_width = width
    else:
        text_box_width = text_width + 8
    text_box_height = text_height * 1.5 
    text_box = Image.new("RGBA", (round(text_box_width), round(text_box_height)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_box)

    # Calculate text position
    text_x = 8
    text_y = text_height // 4

    # Draw text
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
    
    if with_rectangle:
        draw.rectangle([0, 0, text_box_width, text_box_height], outline=(255, 255, 255), width=3)
    
    return text_box
    

def draw_text_boxes(deck_name, deck_format):
    font_size_small = 48
    font_size = 64
    deck_format_text = "Format:"
    
    deck_name_value_text = draw_text(deck_name, font_size, None, False)
    margin_text = draw_text(" ", font_size_small, None, False)
    deck_format_text = draw_text(deck_format_text, font_size_small, None, False)
    deck_format_value_text = draw_text(deck_format, font_size, None, False)
    
    final_image = append_images_vertically(deck_name_value_text, margin_text)
    final_image = append_images_vertically(final_image, deck_format_text)
    final_image = append_images_vertically(final_image, deck_format_value_text)
    
    return final_image

def draw_disclaimer():
    font_size = 48
    text = "Deck image provided by Really Big Yugioh Bot"
    return draw_text(text, font_size, None, False)


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

        main_deck_count = len(main_deck_images)
        extra_deck_count = len(extra_deck_images)
        side_deck_count = len(side_deck_images)

        main_deck_width = 10 * CARD_WIDTH + 9 * MAIN_DECK_MARGIN
        has_extra_deck = extra_deck_count > 0
        has_side_deck = side_deck_count > 0

        # Load the 4K background image
        background_image = Image.open(DECKLIST_BACKGROUND_FILE)
        bg_width, bg_height = background_image.size

        # Draw Main Deck Text Box
        main_deck_text_box = draw_deck_text_box("Main Deck", has_deck=main_deck_count > 0, deck_count=main_deck_count, main_deck_width=main_deck_width)

        # Draw Main Deck
        main_deck_image = draw_main_deck(main_deck_images, main_deck_width, banlist, card_id_to_image)

        # Draw Extra Deck Text Box
        extra_deck_text_box = draw_deck_text_box("Extra Deck", has_deck=has_extra_deck, deck_count=extra_deck_count, main_deck_width=main_deck_width)

        # Draw Extra Deck
        extra_deck_image = draw_extra_side_deck(extra_deck_images, "Extra Deck", main_deck_width, banlist, card_id_to_image)

        # Draw Side Deck Text Box
        side_deck_text_box = draw_deck_text_box("Side Deck", has_deck=has_side_deck, deck_count=side_deck_count, main_deck_width=main_deck_width)

        # Draw Side Deck
        side_deck_image = draw_extra_side_deck(side_deck_images, "Side Deck", main_deck_width, banlist, card_id_to_image)

        # Append images vertically
        final_image = append_images_vertically(main_deck_text_box, main_deck_image)
        if extra_deck_image:
            final_image = append_images_vertically(final_image, extra_deck_text_box)
            final_image = append_images_vertically(final_image, extra_deck_image)
        if side_deck_image:
            final_image = append_images_vertically(final_image, side_deck_text_box)
            final_image = append_images_vertically(final_image, side_deck_image)

        # Calculate position to paste the deck image onto the background
        final_image_width, final_image_height = final_image.size
        paste_x = bg_width - final_image_width - HORIZONTAL_MARGIN
        paste_y = (bg_height - final_image_height) // 2

        # Paste the deck image onto the background
        background_image.paste(final_image, (round(paste_x), round(paste_y)), final_image)
        
        # Add the deck metadata
        deck_metadata = draw_text_boxes(deckname, formatname)
        
        background_image.paste(deck_metadata, (round(HORIZONTAL_MARGIN), round(paste_y)), deck_metadata)

        disclaimer = draw_disclaimer()
        _, disclaimer_height = disclaimer.size
        paste_y = (bg_height - 3*disclaimer_height)
        background_image.paste(disclaimer, (round(HORIZONTAL_MARGIN), round(paste_y)), disclaimer)

        # Convert to RGB to make the jpg image
        background_image = background_image.convert("RGB")

        # Save the final image
        output_filename = f"./img/decks/{filename}.jpg"
        background_image.save(output_filename)
        end_time = time.time() - start_time
        print(f"Time to generate the deck \"{filename}\": {end_time:.3f} seconds")
        return output_filename