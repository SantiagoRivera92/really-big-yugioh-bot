from PIL import Image
from src.deck_validation import Deck as ValidationDeck
from src.deck_collection import Deck as CollectionDeck
from src.card_collection import CardCollection
from typing import List
import shutil
import os

mainDeckMargin = 6

cardWidth = 200
cardHeight = 292

DECKS_FOLDER_NAME = "./img/decks"

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
			files.append(self.buildImageFromDeck(deck.toReadableDeck(), deck.playerName))

		shutil.make_archive("./img/zip/decks", 'zip', DECKS_FOLDER_NAME)
		return "./img/zip/decks.zip"

	def buildImageFromDeck(self, deck:ValidationDeck, filename:str):
		mainDeckImages : List[str]= []
		extraDeckImages : List[str] = []
		sideDeckImages : List[str] = []
		
		#Populate the card image url arrays

		for card in deck.getMainDeck():
			for i in range(0,card.copies):
				imageUrl = self.cardCollection.getCardImageFromId(card.cardId)
				mainDeckImages.append(imageUrl)
		for card in deck.getExtraDeck():
			for i in range(0, card.copies):
				imageUrl = self.cardCollection.getCardImageFromId(card.cardId)
				extraDeckImages.append(imageUrl)
		for card in deck.getSideDeck():
			for i in range(0, card.copies):
				imageUrl = self.cardCollection.getCardImageFromId(card.cardId)
				sideDeckImages.append(imageUrl)

		
		# This is the width *without* the outer margins
		rowWidth = 10*cardWidth + 9*mainDeckMargin

		extraDeckCount = len(extraDeckImages)
		extraDeckWidth = extraDeckCount * cardWidth
		extraDeckMarginCount = extraDeckCount - 1

		# This is the margin for the extra deck. For values larger than 10, it will likely be negative (so cards will pile on top of each other to fit)
		extraDeckMargin = int((rowWidth - extraDeckWidth)/extraDeckMarginCount) - 1

		sideDeckCount = len(sideDeckImages)
		sideDeckWidth = sideDeckCount * cardWidth
		sideDeckMarginCount = sideDeckCount - 1

		# This is the margin for the side deck. For values larger than 10, it will likely be negative (so cards will pile on top of each other to fit)
		sideDeckMargin = int((rowWidth - sideDeckWidth)/sideDeckMarginCount) - 1

		# This is the width for the image, including the margins
		width = 10*cardWidth + 11*mainDeckMargin

		mainDeckRows = int(len(mainDeckImages) / 10)
		if len(mainDeckImages) > mainDeckRows*10:
			mainDeckRows +=1
		hasExtraDeck = len(extraDeckImages) != 0
		hasSideDeck = len(sideDeckImages) != 0

		# This part calculates the height of the image. The width is always gonna be constant, but the height depends on how many cards are in the main deck
		height = mainDeckRows * cardHeight + (mainDeckRows + 1) * mainDeckMargin
		extraDeckStart = height
		if hasExtraDeck:
			height += cardHeight + mainDeckMargin
		sideDeckStart = height
		if hasSideDeck:
			height += cardHeight + mainDeckMargin
		
		
		deckImage = Image.new("RGB", (width, height))
		lastImage = None
		lastUrl = None

		for i in range(0, mainDeckRows):
			for j in range (0, 10):
				# i is the row number, j is the column number
				index = i*10 + j
				if len(mainDeckImages) > index:
					imageUrl = mainDeckImages[index]
					if (imageUrl == lastUrl):
						img = lastImage
					else:
						img = Image.open(imageUrl)
					lastUrl = imageUrl
					if lastImage != img:
						img = img.resize((cardWidth, cardHeight))
					lastImage = img
					x = j * cardWidth + (j+1) * mainDeckMargin
					y = i * cardHeight + (i+1) * mainDeckMargin
					deckImage.paste(img, (x,y))
		
		if hasExtraDeck:
			column = 0
			# Extra Deck is displayed in just 1 row, so we just need column number
			for imageUrl in extraDeckImages:
				if (imageUrl == lastUrl):
					img = lastImage
				else:
					img = Image.open(imageUrl)
				lastUrl = imageUrl
				if lastImage != img:
					img = img.resize((cardWidth, cardHeight))
				lastImage = img
				x = column * (cardWidth + extraDeckMargin) + mainDeckMargin
				y = extraDeckStart
				deckImage.paste(img, (x,y))
				column+=1
		
		if hasSideDeck:
			column = 0
			# Same for the Side Deck.
			for imageUrl in sideDeckImages:
				if (imageUrl == lastUrl):
					img = lastImage
				else:
					img = Image.open(imageUrl)
				lastUrl = imageUrl
				if lastImage != img:
					img = img.resize((cardWidth, cardHeight))
				lastImage = img
				x = column * (cardWidth + sideDeckMargin) + mainDeckMargin
				y = sideDeckStart
				deckImage.paste(img, (x,y))
				column+=1
		

		filename = "./img/decks/%s.jpg" % filename
 
		deckImage.save(filename)
		return filename