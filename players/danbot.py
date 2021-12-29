from player import *

class DanBot(PlayerBase):
    NAME = "DanBot"
    TAKE_RATIO = .4
    EXTORT_RATIO = .25

    def __init__(self, *args, **kwargs):
        # Must call super if you define your own constructor
        super().__init__(*args, **kwargs)

        self.potential_deck = set(range(3,36))

    def decide_impl(self, game):
        if self.get_chips() == 0:
            return TAKE

        opponents = [p for p in game.get_players() if p is not self]

        ratio = self.get_ratio(game)
        if ratio >= self.TAKE_RATIO:
            return TAKE

        is_run_with_self = game.get_current_card() in self.get_run_cards_for_player(self, game)
        is_run_with_other = True in [
            game.get_current_card() in self.get_run_cards_for_player(p, game) for p in opponents
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

    def get_run_cards_for_player(self, player, game):
        cards = player.get_cards()

        run_cards = set()
        for card in cards:
            if card-1 >=3 and (card-1 in self.potential_deck or card-1 == game.get_current_card()):
                run_cards.add(card-1)
            if card+1 <= 35 and (card+1 in self.potential_deck  or card+1 == game.get_current_card()):
                run_cards.add(card+1)

        return run_cards

    def card_utility(self, player, card, game):
        u = card

def DanBotFactory():
    extort_ratio = round(random.gauss(.25, .15), 2)
    take_ratio = round(random.gauss(.4, .2), 2)

    class DanBotVariant(DanBot):
        NAME = f"DanBotVariant (take: {take_ratio} | extort {extort_ratio}) "
        TAKE_RATIO = take_ratio
        EXTORT_RATIO = extort_ratio

    return DanBotVariant
