import math

K_FACTOR = 32
BETA_FACTOR = 400

class Elo:
    def __init__(self, winner_score:float, loser_score:float):
        self.winner_score = winner_score
        self.loser_score = loser_score
        self.match_finished = False
        self.winner_probability = get_winning_probability(self.loser_score, self.winner_score)
        self.loser_probability = get_winning_probability(self.winner_score, self.loser_score)

    def finish_match(self):
        if not self.match_finished:
            self.winner_score = self.winner_score + K_FACTOR * (1 - self.winner_probability)
            self.loser_score = self.loser_score + K_FACTOR * (0 - self.loser_probability)
            self.match_finished = True
    
    def get_winner_updated_score(self):
        return self.winner_score

    def get_loser_updated_score(self):
        return self.loser_score

def get_winning_probability(player_1:float, player_2:float):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (player_1 - player_2) / BETA_FACTOR))