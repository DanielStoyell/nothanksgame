import random
try:
    from progressbar import progressbar
except:
    progressbar = lambda x:x

from game import *
from players.NoProbablem import *
from players.danbot import *
from players.dumboDan import *
from players.dumboSally import *
from players.basic import *


class Evolver(object):
    GAME_SIZE = 5
    ROUNDS = 50000
    LEARNING_RATE = 0.2
    POPULATION_SIZE = 6
    CULL_SIZE = 3

    def __init__(self, PlayerClass=NoProbablemPlayer):
        self.PlayerClass = PlayerClass
        self.population = [
            self.mutate_hyperparams(PlayerClass.HYPERPARAMS)
            for _ in range(self.POPULATION_SIZE)
        ]
        self.victories = {i: 0 for i, _ in enumerate(self.population)}
        self.games_played = {i: 0 for i, _ in enumerate(self.population)}

    def mutate_hyperparams(self, hyperparams):
        return {
            h: v * (random.random() * self.LEARNING_RATE * 2 + 1 - self.LEARNING_RATE)
            for h, v in hyperparams.items()
        }

    def optimize_individually(self):
        params = dict(self.PlayerClass.HYPERPARAMS)
        opt_params = dict(params)
        curr_wr = self.get_win_rate(params)
        for h, v in self.PlayerClass.HYPERPARAMS.items():
            print("\n\n\n===========================")
            print("Optimizing", h)
            start_wr = curr_wr
            print("Starting win rate: ", start_wr)
            print("Starting value: ", params[h])
            test_params = dict(opt_params)
            new_wr = None
            for sign in [1, -1]:
                while new_wr is None or curr_wr <= new_wr:
                    test_params[h] = opt_params[h] * (1 + sign * self.LEARNING_RATE)
                    print("Trying value: ", test_params[h])
                    new_wr = self.get_win_rate(test_params)
                    print("New WR:", new_wr)
                    if new_wr > curr_wr:
                        opt_params[h] = test_params[h]
                        print("Updated Value:", opt_params[h])
                        curr_wr = new_wr
                if curr_wr > start_wr:
                    print("Found an improvement - we're done!")
                    break
                else:
                    print("Trying negative direction")
                    new_wr = None
            print("New Value:", opt_params[h])

        for h, v in opt_params.items():
            print(h, v)

    def get_win_rate(self, params):
        wins = 0
        for n in progressbar(range(self.ROUNDS)):
            player = self.PlayerClass(hyperparams=params)

            game = Game([player, DumboSally(), NoProbablemPlayer(), DanBot(), DanBot()])
            winners = game.play_game()
            if player in winners:
                wins += 1
        return wins/self.ROUNDS

    def evolve(self):
        print("#### Starting Tournament ####")
        while True:
            for n in range(self.ROUNDS):
                players = {}
                for i in random.sample(range(len(self.population)), 1):
                    players[i] = self.PlayerClass(hyperparams=self.population[i])

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
