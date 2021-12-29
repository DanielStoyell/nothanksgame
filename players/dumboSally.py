from player import *
import random

class DumboSally(PlayerBase):
    NAME = "Sally"
    def __init__(self, *args, **kwargs):
        # Must call super if you define your own constructor
        super().__init__(*args, **kwargs)

        self.turns_elapsed = 0

    def decide_impl(self, game):
        if self.get_chips() == 0:
            return TAKE

        if game.get_chips_on_card() > 10:
            return TAKE
        else:
            return DECLINE

    def turn_update_impl(self, game, player, decision):
        self.turns_elapsed += 1
