import math

K_FACTOR = 32
BETA_FACTOR = 400

class Elo:
    def __init__(self, winnerScore:float, loserScore:float):
        self.winnerScore = winnerScore
        self.loserScore = loserScore
        self.matchFinished = False
        self.winnerProbability = getWinningProbability(self.loserScore, self.winnerScore)
        self.loserProbability = getWinningProbability(self.winnerScore, self.loserScore)

    def finishMatch(self):
        if not self.matchFinished:
            self.winnerScore = self.winnerScore + K_FACTOR * (1 - self.winnerProbability)
            self.loserScore = self.loserScore + K_FACTOR * (0 - self.loserProbability)
            self.matchFinished = True
    
    def getWinnerUpdatedScore(self):
        return self.winnerScore

    def getLoserUpdatedScore(self):
        return self.loserScore

def getWinningProbability(playerA:float, playerB:float):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (playerA - playerB) / BETA_FACTOR))