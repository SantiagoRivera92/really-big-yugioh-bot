import os
import json
import shutil
from typing import List
from src.utils import OperationResult
from src.deck_validation import Ydk
import src.strings as Strings

FOLDER_NAME = "./json/deckcollection/%d/%s/"
COLLECTION_FILE_NAME = "./json/deckcollection/%d/%s/collection.json"
DECKS_FOLDER_NAME = "./ydk/%d/%s/decks"
DECK_FILE_NAME = "./ydk/%d/%s/decks/%s.ydk"

COLLECTION_ENABLED_KEY = "collection_enabled"
DECKS_KEY = "decks"
PLAYER_NAME_KEY = "player"
DECK_FILENAME_KEY = "deck"

class Deck:
    def __init__(self, playerName:str, deckFileName:str):
        self.playerName = playerName
        self.deckFileName = deckFileName

    def toDict(self):
        deck = {}
        deck[PLAYER_NAME_KEY] = self.playerName
        deck[DECK_FILENAME_KEY] = self.deckFileName
        return deck

def deckFromDict(dictionary:dict):
    return Deck(dictionary.get(PLAYER_NAME_KEY), dictionary.get(DECK_FILENAME_KEY))

class DeckCollection:
    
    def __init__(self, formatName:str, serverId:int):
        self.formatName = formatName
        self.serverId = serverId
        self.filename = COLLECTION_FILE_NAME%(serverId, formatName)
        self.folderName = FOLDER_NAME%(serverId, formatName)
        if not os.path.exists(self.folderName):
            os.makedirs(self.folderName)
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as file:
                json.dump(self.getDefaultDeckCollectionContent(), file, indent=4)
        with open(self.filename) as file:
            collection = json.load(file)
            decks = collection[DECKS_KEY]
            self.decks:List[Deck] = []
            self.collectionEnabled:bool = collection[COLLECTION_ENABLED_KEY]
            for deck in decks:
                self.decks.append(deckFromDict(deck))

    def zipAllDecks(self):
        shutil.make_archive("./ydk/archive", 'zip', DECKS_FOLDER_NAME % (self.serverId, self.formatName))
        return "./ydk/archive.zip"

    def toDict(self):
        collection = {}
        decks = []
        for deck in self.decks:
            decks.append(deck.toDict())
        collection[DECKS_KEY] = decks
        collection[COLLECTION_ENABLED_KEY] = self.collectionEnabled
        return collection

    def save(self):
        with open(self.filename, 'w') as file:
            json.dump(self.toDict(), file, indent=4)

    def addDeck(self, playerName:str, deck:str):
        if not self.collectionEnabled:
            return OperationResult(False, Strings.ERROR_DECK_COLLECTION_SUBMISSION_DISABLED)
        deckFileName = DECK_FILE_NAME%(self.serverId, self.formatName, playerName)
        folderName = DECKS_FOLDER_NAME%(self.serverId, self.formatName)
        if not os.path.exists(folderName):
            os.makedirs(folderName)
        with open(deckFileName, 'w') as file:
            deckAsLines = deck.split("\n")
            for line in deckAsLines:
                line = line.replace("\n", "").replace("\r", "")
                if len(line) > 0:
                    file.write(line)
                    file.write("\n")
        deck = Deck(playerName, deckFileName)
        newDecks = []
        for savedDeck in self.decks:
            if savedDeck.playerName != playerName:
                newDecks.append(savedDeck)
            
        newDecks.append(deck)
        self.decks = newDecks
        self.save()
        return OperationResult(True, Strings.MESSAGE_DECK_COLLECTION_SUBMISSION_SUCCESSFUL)
        
    def clearDecks(self):
        for deck in self.decks:
            filename = deck.deckFileName
            if os.path.exists(filename):
                os.remove(filename)
        self.decks = []
        self.save()
        return OperationResult(True, Strings.MESSAGE_DECK_COLLECTION_CLEAR_SUCCESSFUL)

    def enableDeckCollection(self):
        if not self.collectionEnabled:
            self.collectionEnabled = True
            self.save()
            return OperationResult(True, Strings.MESSAGE_DECK_COLLECTION_ENABLED)
        else:
            return OperationResult(False, Strings.ERROR_DECK_COLLECTION_ALREADY_ENABLED)

    def disableDeckCollection(self):
        if self.collectionEnabled:
            self.collectionEnabled = False
            self.save()
            return OperationResult(True, Strings.MESSAGE_DECK_COLLECTION_DISABLED)
        else:
            return OperationResult(False, Strings.ERROR_DECK_COLLECTION_ALREADY_DISABLED)

    def getDefaultDeckCollectionContent(self):
        collection = {}
        collection[DECKS_KEY] = []
        collection[COLLECTION_ENABLED_KEY] = False
        return collection

    def getRegisteredPlayers(self):
        players:List[str] = []
        for deck in self.decks:
            players.append(deck.playerName)
        return players
    
    def getDecklistForPlayer(self, playerName:str):
        for deck in self.decks:
            if deck.playerName == playerName:
                return deck.deckFileName
        return None

    def getReadableDecklistForPlayer(self, playerName:str):
        for deck in self.decks:
            if deck.playerName == playerName:
                filename = deck.deckFileName
                with open(filename) as file:
                    decklist = file.read()
                    ydk = Ydk(decklist)
                    readableDecklist = ydk.getDeck()
                    return readableDecklist
        return None



class DeckCollectionManager:

    def __init__(self, formatName:str, serverId:int):
        self.deckCollection = DeckCollection(formatName, serverId)

    def getRegisteredPlayers(self):
        return self.deckCollection.getRegisteredPlayers()

    def cleardecks(self):
        return self.deckCollection.clearDecks()

    def addDeck(self, playerName:str, deck:str):
        return self.deckCollection.addDeck(playerName, deck)

    def beginCollection(self):
        return self.deckCollection.enableDeckCollection()

    def endCollection(self):
        return self.deckCollection.disableDeckCollection()

    def getDecklistForPlayer(self, playerName:str):
        return self.deckCollection.getDecklistForPlayer(playerName)

    def getReadableDecklistForPlayer(self, playerName:str):
        return self.deckCollection.getReadableDecklistForPlayer(playerName)

    def getAllDecks(self):
        return self.deckCollection.decks

    def zipAllDecks(self):
        return self.deckCollection.zipAllDecks()