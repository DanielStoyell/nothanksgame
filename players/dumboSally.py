from player import *
import random

class DumboSally(PlayerBase):
    NAME = "Sally"
    def __init__(self, *args, **kwargs):
        # Must call super if you define your own constructor
        super().__init__(*args, **kwargs)

        self.others_cards = []

    def opponents(self, game):
        self.others = [p for p in game.get_players() if p is not self]
        # print(self.others)
        return self.others

    def decide_impl(self, game):
        if self.get_chips() == 0:
            return TAKE

        elif ((game.get_current_card() + 1) in self.get_cards()) or ((game.get_current_card() - 1) in self.get_cards()):
            #Steal
            if ((game.get_current_card() + 1) in self.others_cards) or ((game.get_current_card() - 1) in self.others_cards):
                return TAKE
            current_chips = [p.get_chips for p in opponents()]
            if 0 in current_chips:
                return TAKE #if any person has 0 chips, just take the card in the run
            #Extort
            else:
                if game.get_chips_on_card() / game.get_current_card() > .2:
                    return TAKE
                else:
                    return DECLINE

        elif game.get_chips_on_card() / game.get_current_card() > .4:
            return TAKE

        else:
            return DECLINE

    def turn_update_impl(self, game, player, decision):
        if decision == TAKE and game.get_current_card() not in self.others_cards:
            self.others_cards.append(game.get_current_card())
        # print(f"Others cards: {self.others_cards}")
        # print(f"My cards: {self.get_cards()}")
