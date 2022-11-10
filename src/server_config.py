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
        
        return OperationResult(False, "This server is not enabled.\n\nTo enable this server you have to be a member in https://patreon.com/DiamondDudeYGO \n\nOnce you've done that, contact @DiamondDudeYGO#5198 with this server ID: %d."%serverId)