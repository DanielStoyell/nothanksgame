import random

from game import *

class Tournament(object):
    GAME_SIZE = 5

    def __init__(self, players, rounds):
        self.players = players
        while len(self.players) < 5:
            self.players = self.players + players
        self.rounds = rounds
        self.victories = {i:0 for i,_ in enumerate(self.players)}
        self.games_played = {i:0 for i,_ in enumerate(self.players)}

    def host_tournament(self):
        print("#### Starting Tournament ####")
        for n in range(self.rounds):
            players = random.sample(range(len(self.players)), Tournament.GAME_SIZE)
            players = {i: self.players[i](i) for i in players}
            game = Game(list(players.values()))
            winners = game.play_game()
            for i, p in players.items():
                self.games_played[i] += 1
                if p in winners:
                    self.victories[i] += 1

            print(f"Round {n+1}: {','.join(p.get_name() for p in winners)} wins!")

        for i, P in enumerate(self.players):
            plays = self.games_played[i]
            wins = self.victories[i]
            print(f"{P(i).get_name()} | Win %: {round(wins/plays * 100.0,2)}% | Games: {plays} | Wins: {wins}")
