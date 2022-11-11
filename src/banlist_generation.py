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
		filename = "./lflist/%d/%s.lflist.conf" % (serverId,formatName)
		with open(filename, 'w', encoding="utf-8") as banlist:
			banlistAsLines = lflistFile.split("\n")
			for line in banlistAsLines:
				line = line.replace("\n", "").replace("\r", "")
				if len(line) > 0:
					banlist.write(line)
					banlist.write("\n")
		return OperationResult(True, "")

	def deleteBanlist(self, formatName, serverId):
		filename = "./lflist/%d/%s.lflist.conf" % (serverId,formatName)
		if os.path.exists(filename):
			os.remove(filename)
			return OperationResult(True, "")
		return OperationResult(False, Strings.ERROR_BANLIST_FILE_MISSING)