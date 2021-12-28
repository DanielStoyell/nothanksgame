from player import *

class BasicPlayer(PlayerBase):
    NAME = "Basic"

    def decide_impl(self, game):
        if self._get_chips() == 0:
            return TAKE

        if game.get_chips_on_card() / game.get_current_card() > .4:
            return TAKE

        return DECLINE
