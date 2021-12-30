import random

from game import *
from players.NoProbablem import *
from players.danbot import *
from players.dumboDan import *
from players.basic import *


class Evolver(object):
    GAME_SIZE = 5
    ROUNDS = 1000
    LEARNING_RATE = 0.2
    POPULATION_SIZE = 6
    CULL_SIZE = 3

    def __init__(self):
        self.population = [
            self.mutate_hyperparams(NoProbablemPlayer.HYPERPARAMS)
            for _ in range(self.POPULATION_SIZE)
        ]
        self.victories = {i: 0 for i, _ in enumerate(self.population)}
        self.games_played = {i: 0 for i, _ in enumerate(self.population)}

    def mutate_hyperparams(self, hyperparams):
        return {
            h: v * (random.random() * self.LEARNING_RATE + 1)
            for h, v in hyperparams.items()
        }

    def optimize_individually(self):
        params = dict(NoProbablemPlayer.HYPERPARAMS)
        for h, v in NoProbablemPlayer.HYPERPARAMS.items():
            print("Optimizing", h)

    # def get_win_rate

    def evolve(self):
        print("#### Starting Tournament ####")
        while True:
            for n in range(self.ROUNDS):
                players = {}
                for i in random.sample(range(len(self.population)), 1):
                    players[i] = NoProbablemPlayer(hyperparams=self.population[i])

                game = Game(list(players.values()) + [BasicPlayer(), DanBot(), DanBot(), DumboDan()])
                winners = game.play_game()
                for i, p in players.items():
                    self.games_played[i] += 1
                    if p in winners:
                        self.victories[i] += 1

                # print(f"Round {n+1}: {','.join(p.get_name() for p in winners)} wins!")

            scores = []
            for i, _ in enumerate(self.population):
                plays = self.games_played[i]
                wins = self.victories[i]
                scores.append(wins / plays)
            sorted_population = list(sorted(zip(scores, self.population), key=lambda x:-x[0]))[:self.CULL_SIZE]
            best_scores = [x[0] for x in sorted_population]
            self.population = [x[1] for x in sorted_population]
            print("\n\n\n##############################################")
            print(best_scores)
            for h,v in self.population[0].items():
                print(h, v)
            print("##############################################\n\n\n")
            offspring = []
            while len(self.population) + len(offspring) < self.POPULATION_SIZE:
                offspring.extend(self.mutate_hyperparams(h) for h in self.population)
            self.population.extend(offspring)
            self.victories = {i: 0 for i, _ in enumerate(self.population)}
            self.games_played = {i: 0 for i, _ in enumerate(self.population)}
