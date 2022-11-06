import json
from src.utils import OperationResult

class ServerConfig:

    def __init__(self, filename):
        self.filename = filename

    def checkServerEnabled(self, serverId):
        with open(self.filename) as serverList:
            serverList = json.load(serverList)
        if serverId in serverList:
            return OperationResult(True, "")
        
        return OperationResult(False, "Server %d is not enabled. Contact @DiamondDudeYGO#5198 to enable the bot in this server."%serverId)