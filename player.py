import random
from constants import *

class PlayerBase():
    NAME = None

    def __init__(self, suffix=''):
        self.__chips = 11
        self.__cards = []
        self.suffix = str(suffix)

    # Implement me: It's your turn. Decide whether you'd like to
    # take the current card, or decline and put a token on it
    def decide_impl(self, game):
        raise Exception("Decide not implemented!")

    # Implement me: A player just made a decision, but their decision
    # hasn't been evaluated yet (i.e. no additional tokens have been
    # placed and no cards have been taken). Feel free to update any
    # internal state as you'd like, or just pass
    def turn_update_impl(self, game, player, decision):
        raise Exception("Turn update not implemented!")

    def decide(self, game):
        try:
            decision = self.decide_impl(game)
        except:
            print(f"{self.get_name()} threw an exception! Defaulting to TAKE")
            raise e
            return TAKE

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
    def get_chips(self):
        return self.__chips

    def get_name(self):
        if self.NAME is None:
            raise Exception("No name given for player!")

        return self.NAME + self.suffix

    def get_cards(self):
        return self.__cards.copy()

    def get_score(self):
        score = -1 * self.__chips
        cards = self.get_cards()

        for i in range(len(cards)):
            if i == 0 or cards[i] != cards[i-1] + 1:
                score += cards[i]

        return score
