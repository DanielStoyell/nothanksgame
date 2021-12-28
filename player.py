import random
from constants import *

class PlayerBase():
    NAME = None

    def __init__(self):
        self.__chips = 11
        self.__cards = []

    def decide_impl(self, game):
        raise Exception("Decide not implemented!")

    def decide(self, game):
        decision = self.decide_impl(game)

        if self.__chips == 0 and decision == DECLINE:
            print("Cannot decline with no chips! Overriding decision!")
            return TAKE

        return decision

    def remove_token(self):
        if self.__chips == 0:
            raise Exception("Cannot remove token from player with no chips!")

        self.__chips -= 1

    def add_chips(self, num_chips):
        self.__chips += num_chips

    def take_card(self, card):
        self.__cards.append(card)
        self.__cards.sort()

    ## GETTERS

    # ONLY call within your implementation, not for other players
    def _get_chips(self):
        return self.__chips

    @classmethod
    def get_name(cls):
        if cls.NAME is None:
            raise Exception("No name given for player!")

        return cls.NAME

    def get_cards(self):
        return self.__cards.copy()

    def get_score(self):
        score = -1 * self.__chips
        cards = self.get_cards()

        for i in range(len(cards)):
            if i == 0 or cards[i] != cards[i-1] + 1:
                score += cards[i]

        return score
