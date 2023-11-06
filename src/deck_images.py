from PIL import Image, ImageDraw, ImageFont
from src.deck_validation import Deck as ValidationDeck
from src.deck_collection import Deck as CollectionDeck
from src.card_collection import CardCollection
from typing import List
import shutil
import os


R, G, B = 0, 0, 0
backgroundColor = (R,G,B)

headerMargin = 438
lateralMargin = 60
bottomMargin = 20
rectangleMargin = 8
mainDeckMargin = 8
sectionMargin = 146

cardWidth = 421
cardHeight = 614

DECKS_FOLDER_NAME = "./img/decks"

FONT_FILE = "font/Roboto-Medium.ttf"

class DeckAsImageGenerator:

	def __init__(self, cardCollection:CardCollection):
		self.cardCollection = cardCollection

	def zipDecks(self, decks:List[CollectionDeck]):
		files: List[str] = []

		with os.scandir(DECKS_FOLDER_NAME) as entries:
			for entry in entries:
				if entry.is_dir() and not entry.is_symlink():
					shutil.rmtree(entry.path)
				else:
					os.remove(entry.path)
		
		for deck in decks:
			files.append(self.buildImageFromDeck(deck.toReadableDeck(), deck.playerName, deck.playerName))

		shutil.make_archive("./img/zip/decks", 'zip', DECKS_FOLDER_NAME)
		return "./img/zip/decks.zip"

	def buildImageFromDeck(self, deck: ValidationDeck, filename: str, deckname:str):
		mainDeckImages = [self.cardCollection.getCardImageFromId(card.card_id) for card in deck.get_main_deck() for _ in range(card.copies)]
		extraDeckImages = [self.cardCollection.getCardImageFromId(card.card_id) for card in deck.get_extra_deck() for _ in range(card.copies)]
		sideDeckImages = [self.cardCollection.getCardImageFromId(card.card_id) for card in deck.get_side_deck() for _ in range(card.copies)]

		mainDeckCount = len(mainDeckImages)
		extraDeckCount = len(extraDeckImages)
		sideDeckCount = len(sideDeckImages)

		mainDeckWidth = 10 * cardWidth + 9 * mainDeckMargin

		mainDeckRows = (len(mainDeckImages) + 9) // 10
		hasExtraDeck = extraDeckCount > 0
		hasSideDeck = sideDeckCount > 0

		# Calculate the overall image dimensions
		height = headerMargin + mainDeckRows * (cardHeight + mainDeckMargin) + bottomMargin + 2*rectangleMargin + 4

		if hasExtraDeck:
			height += cardHeight + sectionMargin + 2*rectangleMargin + 4

		if hasSideDeck:
			height += cardHeight + sectionMargin + 2*rectangleMargin + 4

		width = 2 * lateralMargin + mainDeckWidth

		deckImage = Image.new("RGB", (width, height), backgroundColor)
		draw = ImageDraw.Draw(deckImage)

		# Draw white rectangular boxes for the main, extra, and side deck areas
		mainDeckRect = (
			lateralMargin - rectangleMargin,
			headerMargin - rectangleMargin,
			lateralMargin + mainDeckWidth + rectangleMargin,
			headerMargin + mainDeckRows * (cardHeight + mainDeckMargin) + rectangleMargin
		)
		draw.rectangle(mainDeckRect, outline=(255, 255, 255), width=3)

		if hasExtraDeck:
			extraDeckRect = (
				lateralMargin - rectangleMargin,
				headerMargin + mainDeckRows * (cardHeight + mainDeckMargin) + mainDeckMargin + sectionMargin - rectangleMargin,
				lateralMargin + mainDeckWidth + rectangleMargin,
				headerMargin + mainDeckRows * (cardHeight + mainDeckMargin) + mainDeckMargin + sectionMargin + cardHeight + rectangleMargin
			)
			draw.rectangle(extraDeckRect, outline=(255, 255, 255), width=3)

		if hasSideDeck:
			sideDeckRect = (
				lateralMargin - rectangleMargin,
				headerMargin + mainDeckRows * (cardHeight + mainDeckMargin) + mainDeckMargin + sectionMargin + cardHeight + sectionMargin - rectangleMargin,
				lateralMargin + mainDeckWidth + rectangleMargin,
				headerMargin + mainDeckRows * (cardHeight + mainDeckMargin) + mainDeckMargin + sectionMargin + cardHeight + sectionMargin + cardHeight + rectangleMargin
			)
			draw.rectangle(sideDeckRect, outline=(255, 255, 255), width=3)

		# Draw main deck cards
		for i, imageUrl in enumerate(mainDeckImages):
			img = Image.open(imageUrl)
			x = lateralMargin + (i % 10) * (cardWidth + mainDeckMargin)
			y = headerMargin + (i // 10) * (cardHeight + mainDeckMargin)
			deckImage.paste(img, (x, y))

		if hasExtraDeck:
			if (extraDeckCount > 1):
				extraDeckMargin = (10 * cardWidth + 9 * mainDeckMargin - extraDeckCount * cardWidth) / (extraDeckCount - 1)
			else:
				extraDeckMargin = (10 * cardWidth + 9 * mainDeckMargin - cardWidth)
       

			# Draw extra deck cards
			for i, imageUrl in enumerate(extraDeckImages):
				img = Image.open(imageUrl)
				x = lateralMargin + i * cardWidth + i * extraDeckMargin
				y = headerMargin + mainDeckRows * (cardHeight + mainDeckMargin) + mainDeckMargin + sectionMargin
				deckImage.paste(img, (round(x), y))
   
		if hasSideDeck:
			if (sideDeckCount > 1):
				sideDeckMargin = (10 * cardWidth + 9 * mainDeckMargin - sideDeckCount * cardWidth) / (sideDeckCount - 1)
			else:
				sideDeckMargin = (10 * cardWidth + 9 * mainDeckMargin - cardWidth)

			# Draw side deck cards
			for i, imageUrl in enumerate(sideDeckImages):
				img = Image.open(imageUrl)
				x = lateralMargin + i * cardWidth + i * sideDeckMargin
				y = headerMargin + mainDeckRows * (cardHeight + mainDeckMargin) + mainDeckMargin + sectionMargin + cardHeight + sectionMargin
				deckImage.paste(img, (round(x), y))
   
		# Draw count rectangles
  
		# Draw white rectangle on top of the main deck
		mainDeckHeaderRect = (
			mainDeckRect[0],
			mainDeckRect[1] - 108,
			mainDeckRect[2],
			mainDeckRect[1] - 8
		)
		draw.rectangle(mainDeckHeaderRect, outline=(255, 255, 255), fill=(32, 32, 32), width=3)

		# Add text to the main deck header rectangle
		mainDeckHeaderText = "Main deck: %d" % mainDeckCount
		textFont = ImageFont.truetype(FONT_FILE, 44)
		textBoundingBox = draw.textbbox((0, 0), mainDeckHeaderText, font=textFont)
		textWidth = textBoundingBox[2] - textBoundingBox[0]
		textHeight = textBoundingBox[3] - textBoundingBox[1]
		textX = mainDeckHeaderRect[0] + 30
		textY = mainDeckHeaderRect[1] + (mainDeckHeaderRect[3] - mainDeckHeaderRect[1] - textHeight) // 2
		draw.text((textX, textY), mainDeckHeaderText, font=textFont, fill=(255, 255, 255))

		# Draw white rectangle above the extra deck
		if hasExtraDeck:
			extraDeckHeaderRect = (
				extraDeckRect[0],
				extraDeckRect[1] - 100 - 8,
				extraDeckRect[2],
				extraDeckRect[1] - 8
			)
			draw.rectangle(extraDeckHeaderRect, outline=(255, 255, 255), fill=(32, 32, 32), width=3)

			# Add text to the extra deck header rectangle
			extraDeckHeaderText = "Extra deck: %d" % extraDeckCount
			textBoundingBox = draw.textbbox((0, 0), extraDeckHeaderText, font=textFont)
			textWidth = textBoundingBox[2] - textBoundingBox[0]
			textHeight = textBoundingBox[3] - textBoundingBox[1]
			textX = extraDeckHeaderRect[0] + 30
			textY = extraDeckHeaderRect[1] + (extraDeckHeaderRect[3] - extraDeckHeaderRect[1] - textHeight) // 2
			draw.text((textX, textY), extraDeckHeaderText, font=textFont, fill=(255, 255, 255))

		# Draw white rectangle above the side deck
		if hasSideDeck:
			sideDeckHeaderRect = (
				sideDeckRect[0],
				sideDeckRect[1] - 100 - 8,
				sideDeckRect[2],
				sideDeckRect[1] - 8
			)
			draw.rectangle(sideDeckHeaderRect, outline=(255, 255, 255), fill=(32, 32, 32), width=3)

			# Add text to the side deck header rectangle
			sideDeckHeaderText = "Side deck: %d" % sideDeckCount
			textBoundingBox = draw.textbbox((0, 0), sideDeckHeaderText, font=textFont)
			textWidth = textBoundingBox[2] - textBoundingBox[0]
			textHeight = textBoundingBox[3] - textBoundingBox[1]
			textX = sideDeckHeaderRect[0] + 30
			textY = sideDeckHeaderRect[1] + (sideDeckHeaderRect[3] - sideDeckHeaderRect[1] - textHeight) // 2
			draw.text((textX, textY), sideDeckHeaderText, font=textFont, fill=(255, 255, 255))

		# Add text to the header
		headerText = deckname
		headerFont = ImageFont.truetype(FONT_FILE, 86)
		headerBoundingBox = draw.textbbox((0, 0), headerText, font=headerFont)
		headerTextWidth = headerBoundingBox[2] - headerBoundingBox[0]
		headerTextHeight = headerBoundingBox[3] - headerBoundingBox[1]
		headerTextX = (width - headerTextWidth) // 2
		headerTextY = (100 - headerTextHeight) // 2
		draw.text((headerTextX, headerTextY), headerText, font=headerFont, fill=(255, 255, 255))

		filename = "./img/decks/%s.jpg" % filename
		deckImage = deckImage.resize((width//2, height//2))
		deckImage.save(filename)
		return filename