import time
import math
from PIL import Image, ImageDraw, ImageFont
from src.deck.deck_validation import Deck
from src.card.card_collection import CardCollection

R, G, B = 0, 0, 0
BACKGROUND_COLOR = (R,G,B)

HEADER_MARGIN = 438
LATERAL_MARGIN = 60
BOTTOM_MARGIN = 20
RECTANGLE_MARGIN = 8
MAIN_DECK_MARGIN = 8
SECTION_MARGIN = 146

CARD_WIDTH = 421
CARD_HEIGHT = 614

DECKS_FOLDER_NAME = "./img/decks"

FONT_FILE = "font/Roboto-Medium.ttf"

IMAGE_LIMIT_MARGIN = 8
IMAGE_LIMIT_SIZE = int(0.3 * CARD_HEIGHT)

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

class DeckAsImageGenerator:

	def __init__(self, card_collection:CardCollection):
		self.card_collection = card_collection
	

	def build_image_with_format(self, deck:Deck, filename:str, deckname:str, banlist_file):
		start_time = time.time()

		img_forbidden = Image.open(IMAGE_FORBIDDEN).convert("RGBA")
		img_limited = Image.open(IMAGE_LIMITED).convert("RGBA")
		img_semilimited = Image.open(IMAGE_SEMILIMITED).convert("RGBA")

		img_forbidden = img_forbidden.resize((IMAGE_LIMIT_SIZE, IMAGE_LIMIT_SIZE))
		img_limited = img_limited.resize((IMAGE_LIMIT_SIZE, IMAGE_LIMIT_SIZE))
		img_semilimited = img_semilimited.resize((IMAGE_LIMIT_SIZE, IMAGE_LIMIT_SIZE))

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

		main_deck_rows = (len(main_deck_images) + 9) // 10
		has_extra_deck = extra_deck_count > 0
		has_side_deck = side_deck_count > 0

		# Calculate the overall image dimensions
		height = HEADER_MARGIN + main_deck_rows * (CARD_HEIGHT + MAIN_DECK_MARGIN) + BOTTOM_MARGIN + 2*RECTANGLE_MARGIN + 4

		if has_extra_deck:
			height += CARD_HEIGHT + SECTION_MARGIN + 2*RECTANGLE_MARGIN + 4

		if has_side_deck:
			height += CARD_HEIGHT + SECTION_MARGIN + 2*RECTANGLE_MARGIN + 4

		width = 2 * LATERAL_MARGIN + main_deck_width

		deck_image = Image.new("RGB", (width, height), BACKGROUND_COLOR)
		draw = ImageDraw.Draw(deck_image)

		# Draw white rectangular boxes for the main, extra, and side deck areas
		main_deck_rect = (
			LATERAL_MARGIN - RECTANGLE_MARGIN,
			HEADER_MARGIN - RECTANGLE_MARGIN,
			LATERAL_MARGIN + main_deck_width + RECTANGLE_MARGIN,
			HEADER_MARGIN + main_deck_rows * (CARD_HEIGHT + MAIN_DECK_MARGIN) + RECTANGLE_MARGIN
		)
		draw.rectangle(main_deck_rect, outline=(255, 255, 255), width=3)

		if has_extra_deck:
			extra_deck_rect = (
				LATERAL_MARGIN - RECTANGLE_MARGIN,
				HEADER_MARGIN + main_deck_rows * (CARD_HEIGHT + MAIN_DECK_MARGIN) + MAIN_DECK_MARGIN + SECTION_MARGIN - RECTANGLE_MARGIN,
				LATERAL_MARGIN + main_deck_width + RECTANGLE_MARGIN,
				HEADER_MARGIN + main_deck_rows * (CARD_HEIGHT + MAIN_DECK_MARGIN) + MAIN_DECK_MARGIN + SECTION_MARGIN + CARD_HEIGHT + RECTANGLE_MARGIN
			)
			draw.rectangle(extra_deck_rect, outline=(255, 255, 255), width=3)

		if has_side_deck:
			side_deck_rect = (
				LATERAL_MARGIN - RECTANGLE_MARGIN,
				HEADER_MARGIN + main_deck_rows * (CARD_HEIGHT + MAIN_DECK_MARGIN) + MAIN_DECK_MARGIN + SECTION_MARGIN + CARD_HEIGHT + SECTION_MARGIN - RECTANGLE_MARGIN,
				LATERAL_MARGIN + main_deck_width + RECTANGLE_MARGIN,
				HEADER_MARGIN + main_deck_rows * (CARD_HEIGHT + MAIN_DECK_MARGIN) + MAIN_DECK_MARGIN + SECTION_MARGIN + CARD_HEIGHT + SECTION_MARGIN + CARD_HEIGHT + RECTANGLE_MARGIN
			)
			draw.rectangle(side_deck_rect, outline=(255, 255, 255), width=3)

		# Draw main deck cards
		for i, card_id in enumerate(main_deck_images):
			image_url = card_id_to_image.get(card_id)
			img = Image.open(image_url)
			if img.size != (CARD_WIDTH, CARD_HEIGHT):
				img = img.resize((CARD_WIDTH, CARD_HEIGHT))
			x = LATERAL_MARGIN + (i % 10) * (CARD_WIDTH + MAIN_DECK_MARGIN)
			y = HEADER_MARGIN + (i // 10) * (CARD_HEIGHT + MAIN_DECK_MARGIN)
			deck_image.paste(img, (x, y))

			status = get_status_in_banlist(card_id, banlist)
			if status <= 0:
				deck_image.paste(img_forbidden, (x + IMAGE_LIMIT_MARGIN, y + IMAGE_LIMIT_MARGIN), img_forbidden)
			elif status == 1:
				deck_image.paste(img_limited, (x + IMAGE_LIMIT_MARGIN, y + IMAGE_LIMIT_MARGIN), img_limited)
			elif status == 2:
				deck_image.paste(img_semilimited, (x + IMAGE_LIMIT_MARGIN , y + IMAGE_LIMIT_MARGIN), img_semilimited)

		if has_extra_deck:
			if extra_deck_count > 1:
				extra_deck_margin = (10 * CARD_WIDTH + 9 * MAIN_DECK_MARGIN - extra_deck_count * CARD_WIDTH) / (extra_deck_count - 1)
			else:
				extra_deck_margin = 10 * CARD_WIDTH + 9 * MAIN_DECK_MARGIN - CARD_WIDTH

			# Draw extra deck cards
			for i, card_id in enumerate(extra_deck_images):
				image_url = card_id_to_image.get(card_id)
				img = Image.open(image_url)
				if img.size != (CARD_WIDTH, CARD_HEIGHT):
					img = img.resize((CARD_WIDTH, CARD_HEIGHT))
				x = LATERAL_MARGIN + i * CARD_WIDTH + i * extra_deck_margin
				y = HEADER_MARGIN + main_deck_rows * (CARD_HEIGHT + MAIN_DECK_MARGIN) + MAIN_DECK_MARGIN + SECTION_MARGIN
				deck_image.paste(img, (round(x), y))
				
				status = get_status_in_banlist(card_id, banlist)
				if status <= 0:
					deck_image.paste(img_forbidden, (round(x) + IMAGE_LIMIT_MARGIN, y + IMAGE_LIMIT_MARGIN), img_forbidden)
				elif status == 1:
					deck_image.paste(img_limited, (round(x) + IMAGE_LIMIT_MARGIN, y + IMAGE_LIMIT_MARGIN), img_limited)
				elif status == 2:
					deck_image.paste(img_semilimited, (round(x) + IMAGE_LIMIT_MARGIN, y + IMAGE_LIMIT_MARGIN), img_semilimited)

		if has_side_deck:
			if side_deck_count > 1:
				side_deck_margin = (10 * CARD_WIDTH + 9 * MAIN_DECK_MARGIN - side_deck_count * CARD_WIDTH) / (side_deck_count - 1)
			else:
				side_deck_margin = 10 * CARD_WIDTH + 9 * MAIN_DECK_MARGIN - CARD_WIDTH

			# Draw side deck cards
			for i, card_id in enumerate(side_deck_images):
				image_url = card_id_to_image.get(card_id)
				img = Image.open(image_url)
				if img.size != (CARD_WIDTH, CARD_HEIGHT):
					img = img.resize((CARD_WIDTH, CARD_HEIGHT))
				x = LATERAL_MARGIN + i * CARD_WIDTH + i * side_deck_margin
				y = HEADER_MARGIN + main_deck_rows * (CARD_HEIGHT + MAIN_DECK_MARGIN) + MAIN_DECK_MARGIN + SECTION_MARGIN + CARD_HEIGHT + SECTION_MARGIN
				deck_image.paste(img, (round(x), y))
    
				status = get_status_in_banlist(card_id, banlist)
				if status <= 0:
					deck_image.paste(img_forbidden, (round(x) + IMAGE_LIMIT_MARGIN, y + IMAGE_LIMIT_MARGIN), img_forbidden)
				elif status == 1:
					deck_image.paste(img_limited, (round(x) + IMAGE_LIMIT_MARGIN, y + IMAGE_LIMIT_MARGIN), img_limited)
				elif status == 2:
					deck_image.paste(img_semilimited, (round(x) + IMAGE_LIMIT_MARGIN, y + IMAGE_LIMIT_MARGIN), img_semilimited)

		# Draw white rectangle on top of the main deck
		main_deck_header_rect = (
			main_deck_rect[0],
			main_deck_rect[1] - 108,
			main_deck_rect[2],
			main_deck_rect[1] - 8
		)
		draw.rectangle(main_deck_header_rect, outline=(255, 255, 255), fill=(32, 32, 32), width=3)

		# Add text to the main deck header rectangle
		main_deck_header_text = f"Main deck: {main_deck_count}"
		text_font = ImageFont.truetype(FONT_FILE, 44)
		text_bounding_box = draw.textbbox((0, 0), main_deck_header_text, font=text_font)
		text_height = text_bounding_box[3] - text_bounding_box[1]
		text_x = main_deck_header_rect[0] + 30
		text_y = main_deck_header_rect[1] + (main_deck_header_rect[3] - main_deck_header_rect[1] - text_height) // 2
		draw.text((text_x, text_y), main_deck_header_text, font=text_font, fill=(255, 255, 255))

		# Draw white rectangle above the extra deck
		if has_extra_deck:
			extra_deck_header_rect = (
				extra_deck_rect[0],
				extra_deck_rect[1] - 92,
				extra_deck_rect[2],
				extra_deck_rect[1] - 8
			)
			draw.rectangle(extra_deck_header_rect, outline=(255, 255, 255), fill=(32, 32, 32), width=3)

			# Add text to the extra deck header rectangle
			extra_deck_header_text = f"Extra deck: {extra_deck_count}"
			text_bounding_box = draw.textbbox((0, 0), extra_deck_header_text, font=text_font)
			text_height = text_bounding_box[3] - text_bounding_box[1]
			text_x = extra_deck_header_rect[0] + 30
			text_y = extra_deck_header_rect[1] + (extra_deck_header_rect[3] - extra_deck_header_rect[1] - text_height) // 2
			draw.text((text_x, text_y), extra_deck_header_text, font=text_font, fill=(255, 255, 255))

		# Draw white rectangle above the side deck
		if has_side_deck:
			side_deck_header_rect = (
				side_deck_rect[0],
				side_deck_rect[1] - 92,
				side_deck_rect[2],
				side_deck_rect[1] - 8
			)
			draw.rectangle(side_deck_header_rect, outline=(255, 255, 255), fill=(32, 32, 32), width=3)

			# Add text to the side deck header rectangle
			side_deck_header_text = f"Side deck: {side_deck_count}"
			text_bounding_box = draw.textbbox((0, 0), side_deck_header_text, font=text_font)
			text_height = text_bounding_box[3] - text_bounding_box[1]
			text_x = side_deck_header_rect[0] + 30
			text_y = side_deck_header_rect[1] + (side_deck_header_rect[3] - side_deck_header_rect[1] - text_height) // 2
			draw.text((text_x, text_y), side_deck_header_text, font=text_font, fill=(255, 255, 255))

		# Add text to the header
		header_text = deckname
		font_size = 128
		header_font = ImageFont.truetype(FONT_FILE, font_size)
		header_bounding_box = draw.textbbox((0, 0), header_text, font=header_font)
		header_text_width = header_bounding_box[2] - header_bounding_box[0]
		header_text_x = (width - header_text_width) // 2
		header_text_y = (322 - font_size) // 2
		draw.text((header_text_x, header_text_y), header_text, font=header_font, fill=(255, 255, 255))

		filename = f"./img/decks/{filename}.jpg"
		deck_image = deck_image.resize((width//2, height//2))
		deck_image.save(filename)
		end_time = time.time() - start_time
		print(f"Time to generate the deck \"{filename}\": {end_time:.3f} seconds")
		return filename