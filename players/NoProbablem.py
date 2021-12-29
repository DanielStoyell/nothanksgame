from player import *


class NoProbablemPlayer(PlayerBase):
    NAME = "NoProbablem"

    HYPERPARAMS = {
        "extortion_threshold": 0.25,
        # scale chip value by 1 + chip_utility_base^(chip_utility_scale-curr_chips)
        "chip_utility_base": 2,
        "chip_utility_scale": 3,
        "take_threshold": 0.4,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def decide_impl(self, game):
        if self._get_chips() == 0:
            return TAKE

        card_util = self.get_current_card_utility(game, self)
        chip_util = self.get_current_chip_utility(game, self)
        print(f"Card util: {card_util}")
        print(f"Chip util: {chip_util}")
        print(f"Net: {card_util + chip_util}")

        if card_util + chip_util >= 0:
            # Need to consider how we value current chips?
            if self.get_should_extort(game):
                print("EXTORTING")
                return DECLINE
            return TAKE

        print(f"Ratio: {chip_util / -card_util}")

        if chip_util / -card_util > self.HYPERPARAMS["take_threshold"]:
            return TAKE

        return DECLINE

    def turn_update_impl(self, game, player, decision):
        pass

    # Relative value of current card to me relative to player who wants it next most
    def get_should_extort(self, game):
        players = self.get_players(game)
        values = []
        ratios = []
        for i, player in enumerate(players):
            card_util = self.get_current_card_utility(game, player)
            chip_util = self.get_current_chip_utility(game, player, i)
            values.append(
                card_util +
                chip_util
            )
            if card_util >= 0:
                ratios.append(99999)
            else:
                ratios.append(chip_util / -card_util)

        print("Extortion values", values)
        print("Extortion ratios", ratios)
        if values[0] < 0 or any(v >=0 for v in values[1:]):
            return False

        return all(r < self.HYPERPARAMS['extortion_threshold'] for r in ratios[1:])

    # How much the player values the chips on the current card (or how many chips will be there when it's their turn)
    def get_current_chip_utility(self, game, player, turns_until=0):
        card_chips = game.get_chips_on_card() + turns_until
        player_chips = player._get_chips()
        chip_utility_base = self.HYPERPARAMS["chip_utility_base"]
        chip_utility_scale = self.HYPERPARAMS["chip_utility_scale"]

        # inverse points - positive is GOOD, negative BAD
        return card_chips * (
            1 + chip_utility_base ** (chip_utility_scale - player_chips)
        )

    # How the current card affects the given players score (or potential future score)
    # Ignores chips on card
    def get_current_card_utility(self, game, player):
        cards = player.get_cards()
        curr_card = game.get_current_card()

        curr_score = self.get_player_card_score(cards)
        new_score = self.get_player_card_score(sorted(cards + [curr_card]))

        # inverse points - positive is GOOD, negative BAD
        return curr_score - new_score

    def get_player_card_score(self, cards):
        score = 0
        for i in range(len(cards)):
            if i == 0 or cards[i] != cards[i - 1] + 1:
                score += cards[i]

        return score

    def get_players(self, game):
        players = game.get_players()
        i_me = players.index(self)
        return players[i_me:] + players[:i_me]
