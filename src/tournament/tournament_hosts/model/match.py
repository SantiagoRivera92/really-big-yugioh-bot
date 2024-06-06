from src.tournament.tournament_hosts.model.player import Player

class Match:

	def __init__(self, player_1:Player, player_2:Player):
		self.player_1 = player_1
		self.player_2 = player_2
		self.finished = False
		self.tie = False
		self.winner: Player = None

	def set_winner(self, player_id: int):
		if not self.finished:
			if(self.player_1.discord_id == player_id):
				self.finished = True
				self.winner = self.player_1
			elif(self.player_2.discord_id == player_id):
				self.finished = True
				self.winner = self.player_2

	def set_tie(self):
		if not self.finished:
			self.tie = True