from player import *
import random

class DumboPlayer(PlayerBase):
    NAME = "Dumbo"

    def decide_impl(self, game):
        if self._get_chips() == 0:
            return TAKE

        if random.random() > .2:
            return DECLINE
        else:
            return TAKE

    def turn_update_impl(self, game, player, decision):
        pass
