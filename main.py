import random
import argparse

from game import *
from player import *
from tournament import *
from player_register import *
from players.basic import *
from players.dumbo import *

from constants import *

PLAYERS = [
    DumboPlayer(),
    BasicPlayer(),
    DumboSally(),
    DanBot(),
    DumboDan(),
]

random.shuffle(PLAYERS)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='No Thanks game engine.')
    parser.add_argument('-v','--verbose', dest='verbose', action='store_const', const=True, default=False, help='Use verbose mode')
    parser.add_argument('-m','--manual', dest='manual', action='store_const', const=True, default=False, help='Use manual mode')
    parser.add_argument('-t','--tournament', dest='tournament', action='store_const', const=True, default=False, help='Use tournament')
    args = parser.parse_args()
    if args.tournament:
        tournament = Tournament(PLAYER_REGISTER, 1000)
        tournament.host_tournament()
    else:
        game = Game(PLAYERS, args.verbose, args.manual)
        game.play_game()
