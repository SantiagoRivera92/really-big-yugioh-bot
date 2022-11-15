from PIL import Image
from urllib.request import urlopen
from urllib.request import Request
from src.deck_validation import Deck, Card
from src.card_collection import CardCollection
from typing import List
import time

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'} 
mainDeckMargin = 6
cardWidth = 100
cardHeight = 146
class DeckAsImageGenerator:

    def __init__(self, cardCollection:CardCollection):
        self.cardCollection = cardCollection
        
    def getImageFromDeck(self, deck:Deck):
        mainDeckImages : List[str]= []
        extraDeckImages : List[str] = []
        sideDeckImages : List[str] = []
        
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



        rowWidth = 10*cardWidth + 9*mainDeckMargin

        extraDeckCount = len(extraDeckImages)
        extraDeckWidth = extraDeckCount * cardWidth
        extraDeckMarginCount = extraDeckCount - 1
        extraDeckMarginWidth = int((rowWidth - extraDeckWidth)/extraDeckMarginCount) - 1

        sideDeckCount = len(sideDeckImages)
        sideDeckWidth = sideDeckCount * cardWidth
        sideDeckMarginCount = sideDeckCount - 1
        sideDeckMarginWidth = int((rowWidth - sideDeckWidth)/sideDeckMarginCount) - 1

        rows = 5
        mainDeckRows = rows

        totalImage = None
        lastImage = None
        lastUrl = None
        for i in range(0, mainDeckRows):
            rowImage = None
            isRowEmpty = True
            for j in range (0, 10):
                index = i*10 + j
                if len(mainDeckImages) > index:
                    imageUrl = mainDeckImages[index]
                    if (imageUrl == lastUrl):
                        img = lastImage
                    else:
                        request = Request(imageUrl, None, headers)
                        img = Image.open(urlopen(request))
                    lastUrl = imageUrl
                    lastImage = img
                    img = img.resize((cardWidth, cardHeight))
                    if (rowImage == None):
                        rowImage = createFirstImageInRow(img, mainDeckMargin)
                        isRowEmpty = False
                    else:
                        rowImage = mergeHorizontally(rowImage, img, mainDeckMargin, mainDeckMargin)
                        isRowEmpty = False
            if not isRowEmpty:
                rowImage = addRightMargin(rowImage, mainDeckMargin)
                if totalImage == None:
                    totalImage = rowImage
                else:
                    totalImage = mergeVertically(totalImage, rowImage, 0)
        
        extraImage = None
        if len(extraDeckImages) > 0:
            for imageUrl in extraDeckImages:
                if (imageUrl == lastUrl):
                    img = lastImage
                else:
                    request = Request(imageUrl, None, headers)
                    img = Image.open(urlopen(request))
                lastUrl = imageUrl
                lastImage = img
                img = img.resize((cardWidth, cardHeight))
                if (extraImage == None):
                    extraImage = createFirstImageInRow(img, mainDeckMargin)
                else:
                    extraImage = mergeHorizontally(extraImage, img, mainDeckMargin, extraDeckMarginWidth)
            totalImage = mergeVertically(totalImage, extraImage, mainDeckMargin)

        sideImage = None
        if len(sideDeckImages) > 0:
            for imageUrl in sideDeckImages:
                if (imageUrl == lastUrl):
                    img = lastImage
                else:
                    request = Request(imageUrl, None, headers)
                    img = Image.open(urlopen(request))
                lastUrl = imageUrl
                lastImage = img
                img = img.resize((cardWidth, cardHeight))
                if (sideImage == None):
                    sideImage = createFirstImageInRow(img, mainDeckMargin)
                else:
                    sideImage = mergeHorizontally(sideImage, img, mainDeckMargin, sideDeckMarginWidth)
            totalImage = mergeVertically(totalImage, sideImage, mainDeckMargin)


        timestamp = int(time.time())
        timestampAsString = str(timestamp)
        filename = "./img/%s.png"%timestampAsString
 
        totalImage.save(filename)
        return filename

def createFirstImageInRow(im1:Image, margin:int):
    w = im1.size[0] + margin
    h = im1.size[1] + margin
    im = Image.new("RGBA", (w, h))
    im.paste(im1, (margin, margin))
    return im

def mergeHorizontally(im1:Image, im2:Image, marginTop:int, marginLeft:int):
    w = im1.size[0] + im2.size[0] + marginLeft
    h = max(im1.size[1], im2.size[1])
    im = Image.new("RGBA", (w, h))
    im.paste(im1)
    im.paste(im2, (im1.size[0] + marginLeft, marginTop))
    return im

def mergeVertically(im1:Image, im2:Image, marginTop:int):
    w = max(im1.size[0], im2.size[0])
    h = im1.size[1] + im2.size[1]
    im = Image.new("RGBA", (w, h))
    im.paste(im1)
    im.paste(im2, (0, im1.size[1]))
    return im

def addRightMargin(im1:Image, marginRight:int):
    w = im1.size[0] + marginRight
    h = im1.size[1]
    im = Image.new("RGBA", (w, h))
    im.paste(im1)
    return im