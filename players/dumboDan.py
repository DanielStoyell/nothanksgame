from player import *


class DumboDan(PlayerBase):
    NAME = "DumboDan"
    MIN_TAKE_RATIO = .4
    EXTORT_RATIO = .35

    def __init__(self, *args, **kwargs):
        # Must call super if you define your own constructor
        super().__init__(*args, **kwargs)

        self.potential_deck = set(range(3, 36))

    def decide_impl(self, game):
        if self.get_chips() == 0:
            return TAKE

        ratio = self.get_ratio(game)
        if ratio >= self.MIN_TAKE_RATIO:
            return TAKE

        opponents = [p for p in game.get_players() if p is not self]

        is_run_with_self = game.get_current_card() in self.get_run_cards_for_player(self.get_cards(), game.get_current_card())
        is_run_with_other = True in [
            game.get_current_card() in self.get_run_cards_for_player(p.get_cards(), game.get_current_card()) for p in opponents
        ]

        if is_run_with_self and is_run_with_other:
            return TAKE

        if is_run_with_self and not is_run_with_other and ratio >= self.EXTORT_RATIO:
            return TAKE

        return DECLINE

    def turn_update_impl(self, game, player, decision):
        if game.get_current_card() in self.potential_deck:
            self.potential_deck.remove(game.get_current_card())

    def get_ratio(self, game):
        return game.get_chips_on_card() / game.get_current_card()

    def get_run_cards_for_player(self, cards, current_card):
        run_cards = set()
        for card in cards:
            if card-1 >=3 and (card-1 in self.potential_deck or card-1 == current_card):
                run_cards.add(card-1)
            if card+1 <= 35 and (card+1 in self.potential_deck or card+1 == current_card):
                run_cards.add(card+1)

        return run_cards



def DumboDanFactory():
    extort_ratio = round(random.gauss(DanBot.EXTORT_RATIO, .15), 2)
    min_take_ratio = round(random.gauss(DanBot.MIN_TAKE_RATIO, .2), 2)

    class DumboDanVariant(DumboDan):
        NAME = f"DumboDanVariant (min_take: {min_take_ratio} | extort {extort_ratio})"
        MIN_TAKE_RATIO = min_take_ratio
        EXTORT_RATIO = extort_ratio

    return DumboDanVariant
