import os
from src.utils import OperationResult
import src.strings as Strings


class BanlistGenerator:

	def __init__(self, cardCollection):
		self.cardCollection = cardCollection

	def createFolderForServer(self, serverId):
		folderName = "./lflist/%d" % serverId
		if not os.path.exists(folderName):
			os.makedirs(folderName)

	def writeBanlist(self, formatName, lflistFile, serverId):
		self.createFolderForServer(serverId)
		filename = "./lflist/%d/%s.lflist.conf" % (serverId, formatName)
		with open(filename, 'w', encoding="utf-8") as banlist:
			banlistAsLines = lflistFile.split("\n")
			for line in banlistAsLines:
				line = line.replace("\n", "").replace("\r", "")
				if len(line) > 0:
					banlist.write(line)
					banlist.write("\n")
		return OperationResult(True, Strings.BOT_MESSAGE_FORMAT_ADDED)

	def fixBanlist(self, formatName, serverId, cardId, cardName, newStatus):
		filename = "./lflist/%d/%s.lflist.conf" % (serverId, formatName)
		lines = []
		with open(filename, encoding="utf-8") as banlist:
			banlistAsLines = banlist.read().split("\n")
			for line in banlistAsLines:
				if not str(cardId) in line:
					if len(line) > 0:
						lines.append(line)
			lines.append("%d %d -- %s"%(cardId, newStatus, cardName))
		with open(filename, 'w', encoding="utf-8") as banlist:
			for line in lines:
				banlist.write(line)
				banlist.write("\n")
		return OperationResult(True, Strings.BOT_MESSAGE_CARD_ADDED_TO_BANLIST)

	def deleteBanlist(self, formatName, serverId):
		filename = "./lflist/%d/%s.lflist.conf" % (serverId, formatName)
		if os.path.exists(filename):
			os.remove(filename)
			return OperationResult(True, "")
		return OperationResult(False, Strings.ERROR_BANLIST_FILE_MISSING)
