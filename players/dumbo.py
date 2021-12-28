from player import *
import random

class DumboPlayer(PlayerBase):
    NAME = "Dumbo"
    def __init__(self, *args, **kwargs):
        # Must call super if you define your own constructor
        super().__init__(*args, **kwargs)

        self.turns_elapsed = 0

    def decide_impl(self, game):
        if self._get_chips() == 0:
            return TAKE

        if random.random() > .2:
            return DECLINE
        else:
            return TAKE

    def turn_update_impl(self, game, player, decision):
        self.turns_elapsed += 1
