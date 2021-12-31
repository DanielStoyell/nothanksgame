from player import *
import random

class DumboSally(PlayerBase):
    NAME = "Sally"
    def __init__(self, *args, **kwargs):
        # Must call super if you define your own constructor
        super().__init__(*args, **kwargs)

        self.others_cards = set()

    def opponents(self, game):
        self.others = [p for p in game.get_players() if p is not self]
        # print(self.others)
        return self.others

    def decide_impl(self, game):
        CONSERVATIVE_TAKE_RATIO = 0.4+((24-game.get_deck_length())*0.002)
        TAKE_RATIO = 0.35+((24-game.get_deck_length())*0.002)
        RUN_TAKE_RATIO = 0.3+((24-game.get_deck_length())*0.004)

        if self.get_chips() == 0:
            return TAKE

        #Is it in a run?
        elif ((game.get_current_card() + 1) in self.get_cards()) or ((game.get_current_card() - 1) in self.get_cards()):
            #Steal
            if ((game.get_current_card() + 1) in self.others_cards) or ((game.get_current_card() - 1) in self.others_cards):
                return TAKE
            current_chips = [p.get_chips for p in self.opponents(game)]
            if 0 in current_chips:
                return TAKE #if any person has 0 chips, just take the card in the run
            #Extort
            else:
                if ((game.get_current_card() + 2) in self.others_cards) or ((game.get_current_card() - 2) in self.others_cards):
                    #AND RUN STILL AVAILABLE FOR THEM
                    if game.get_chips_on_card() / game.get_current_card() > .1:
                        return TAKE
                if game.get_chips_on_card() / game.get_current_card() > .2:
                    return TAKE
                else:
                    return DECLINE
        
        #Is it in a potential run?
        elif ((game.get_current_card() + 2) in self.get_cards() and (game.get_current_card() + 1) not in self.others_cards) or ((game.get_current_card() - 2) in self.get_cards() and (game.get_current_card() - 1) not in self.others_cards):
            if game.get_chips_on_card() / game.get_current_card() > RUN_TAKE_RATIO:
                    return TAKE
            else:
                return DECLINE
        
        #Otherwise
        elif game.get_current_card() < 28 and game.get_current_card() > 5 and game.get_chips_on_card() / game.get_current_card() > TAKE_RATIO:
            return TAKE
        elif game.get_chips_on_card() / game.get_current_card() > CONSERVATIVE_TAKE_RATIO:
            return TAKE

        else:
            return DECLINE

    #Account for other people's potential runs 
    #Think more about chip ratios when extorting
    #Ratio tbd on if other people want card (their potential runs)

    #Distance of card from any of my cards : Ratio of chips
    #Distance of card from any of anyone else's cards : Ratio of chips

    def turn_update_impl(self, game, player, decision):
        if decision == TAKE and player!=self and game.get_current_card() not in self.others_cards:
            self.others_cards.add(game.get_current_card())
        #game._print_state()
