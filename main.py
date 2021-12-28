from game import *
from player import *
from players.basic import *
from players.dumbo import *

from constants import *

import random

PLAYERS = [
    DumboPlayer(),
    DumboPlayer(),
    BasicPlayer(),
    BasicPlayer(),
]

random.shuffle(PLAYERS)

game = Game(PLAYERS, True, True)

game.play_game()
