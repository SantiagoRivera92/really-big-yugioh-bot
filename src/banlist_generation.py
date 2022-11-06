import os
from src.utils import OperationResult

class BanlistGenerator:

	def __init__(self, cardCollection):
		self.cardCollection = cardCollection

	def createFolderForServer(self, serverId):
		folderName = "./lflist/%d"
		if not os.path.exists(folderName):
			os.makedirs(folderName)

	def writeBanlist(self, formatName, lflistFile, serverId):
		self.createFolderForServer(serverId)
		filename = "./lflist/%d/%s.lflist.conf" % formatName
		while "\n\n" in lflistFile:
			lflistFile = lflistFile.replace("\n\n", "\n")
		print(lflistFile, flush=True)
		with open(filename, 'w', encoding="utf-8") as banlist:
			banlist.write(lflistFile)

		return OperationResult(True, "")