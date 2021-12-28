import random
from constants import *

class Game():
    def __init__(self, players, verbose=False, manual=False):
        cards = list(range(3, 36))
        random.shuffle(cards)
        self._deck = cards[9:]
        self._players = players
        self._flip_card()
        self._chips_on_card = 0
        self._current_player = 0
        self.verbose = verbose
        self.manual = manual

    def play_game(self):
        while len(self._deck) > 0:
            self._take_turn()

        self._end_game()


    def _take_turn(self):
        player = self._players[self._current_player]

        decision = player.decide(self)
        for p in self._players:
            p.turn_update_impl(self, player, decision)

        if decision == TAKE:
            player.take_card(self._current_card)
            player.add_chips(self._chips_on_card)
            self._chips_on_card = 0
            self._flip_card()
        elif decision == DECLINE:
            player.remove_token()
            self._chips_on_card += 1
        else:
            raise Exception("Unknown player decision {}", decision)

        self._current_player = (self._current_player + 1) % len(self._players)

        if self.verbose:
            self._print_state()

        if self.manual:
            _ = input("...")



    def _flip_card(self):
        if len(self._deck) == 0:
            raise Exception("Cannot flip card from empty deck!")
        self._current_card = self._deck.pop()

    def _end_game(self):
        if self.verbose:
            print("##### GAME OVER!! #####")
            best_score = 100000
            winners = None
            for p in self._players:
                score = p.get_score()
                if score < best_score:
                    best_score = score
                    winners = [p]
                elif score == best_score:
                    winner.append(p)
                print("{}: {} points".format(p.get_name(), p.get_score()))

            print("WINNER(S): {}!".format(
                winners[0].get_name() if len(winners) == 1 else str([p.get_name() for p in winners]
            )))

    def _print_state(self):
        print("------ Current State -------")
        print("Current Card: {} | With {} chips".format(self._current_card, self._chips_on_card))
        print("Current Player: {}".format(self._players[self._current_player].get_name()))
        for p in self._players:
            print("{}: {} chips | Cards: {}".format(p.get_name(), p._get_chips(), p.get_cards()))


    ## GETTERS

    def get_current_card(self):
        return self._current_card

    def get_chips_on_card(self):
        return self._chips_on_card

    def get_deck_length(self):
        return len(self._deck)

    def get_players(self):
        return self._players.copy()
