import os
from src.utils import OperationResult

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
			banlist.write(lflistFile)
		return OperationResult(True, "")