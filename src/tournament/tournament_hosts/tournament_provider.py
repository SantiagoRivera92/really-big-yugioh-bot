from abc import ABC, abstractmethod
from typing import List

from src.credentials_manager import CredentialsManager
from src.utils.utils import OperationResult
from src.tournament.tournament_hosts.model.match import Match
from src.tournament.tournament_hosts.model.player import Player

class TournamentProvider(ABC):
    
    def __init__(self, credentials_manager: CredentialsManager, server_id:int):
        self.credentials_manager = credentials_manager
        self.server_id = server_id
        
    @abstractmethod
    def create_tournament(self, tournament_name:str, format_name:str, tournament_type:str) -> OperationResult:
        pass
    
    @abstractmethod
    def register_to_tournament(self, player_name: str, player_id: int, path: str) -> OperationResult:
        pass
    
    @abstractmethod
    def drop(self, player_name:str) -> OperationResult:
        pass
    
    @abstractmethod
    def report_loss(self, player_name:str) -> OperationResult:
        pass
    
    @abstractmethod
    def get_matches(self) -> List[Match]:
        pass
    
    @abstractmethod
    def get_active_matches(self) -> List[Match]:
        pass
    
    @abstractmethod
    def get_tournament_info(self) -> OperationResult:
        pass
    
    @abstractmethod
    def start_tournament(self) -> OperationResult:
        pass
    
    @abstractmethod
    def end_tournament(self) -> OperationResult:
        pass
    
