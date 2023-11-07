import json
from src.utils.utils import OperationResult
import src.strings as Strings

class ServerConfig:

    def __init__(self):
        self.filename = "json/enabledServers.json"

    def check_server_enabled(self, server_id):
        with open(self.filename, encoding="utf-8") as server_list:
            server_list = json.load(server_list)
        if server_id in server_list:
            return OperationResult(True, "")
        
        return OperationResult(False, Strings.ERROR_PAY_ME_MONEY % server_id)
    
    def get_enabled_servers(self):
        with open(self.filename, encoding="utf-8") as server_list:
            server_list = json.load(server_list)
        return server_list