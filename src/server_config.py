import json
from src.utils import OperationResult
import src.strings as Strings

class ServerConfig:

    def __init__(self, filename):
        self.filename = filename

    def checkServerEnabled(self, serverId):
        with open(self.filename) as serverList:
            serverList = json.load(serverList)
        if serverId in serverList:
            return OperationResult(True, "")
        
        return OperationResult(False, Strings.ERROR_PAY_ME_MONEY % serverId)
    
    def getEnabledServers(self):
        with open(self.filename) as serverList:
            serverList = json.load(serverList)
        return serverList