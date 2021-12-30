from player import *
from functools import reduce


class NoProbablemPlayer(PlayerBase):
    NAME = "NoProbablem"
    RUN_CONSIDERATION_SIZE = 3

    HYPERPARAMS = {
        "extortion_threshold": 0.45121,
        # scale chip value by 1 + chip_utility_factor * e^(-chip_utility_scale*curr_chips)
        "chip_utility_factor": 7.64079,
        "chip_utility_scale": 0.8985,
        "take_threshold_high": 0.9,
        "take_threshold_low": 0.35,
    }

    def __init__(self, *args, **kwargs):
        if "hyperparams" in kwargs:
            self.hyperparams = kwargs["hyperparams"]
            del kwargs["hyperparams"]
        else:
            self.hyperparams = self.HYPERPARAMS
        super().__init__(*args, **kwargs)

    def decide_impl(self, game):
        if self.get_chips() == 0:
            return TAKE

        card_util = self.get_current_card_utility_ev(game, self)
        chip_util = self.get_current_chip_utility(game, self)
        # print(f"Card util: {card_util}")
        # print(f"Chip util: {chip_util}")
        # print(f"Net: {card_util + chip_util}")

        if card_util + chip_util >= 0:
            # Need to consider how we value current chips?
            if self.get_should_extort(game):
                # print("EXTORTING")
                return DECLINE
            return TAKE

        # print(f"Ratio: {chip_util / -card_util}")

        if chip_util / -card_util > self.get_take_threshold(game):
            return TAKE

        return DECLINE

    def turn_update_impl(self, game, player, decision):
        pass

    def get_take_threshold(self, game):
        diff = self.hyperparams["take_threshold_high"] - self.hyperparams["take_threshold_low"]
        return self.hyperparams["take_threshold_high"] - (diff/(33-9) * game.get_deck_length())

    # Relative value of current card to me relative to player who wants it next most
    def get_should_extort(self, game):
        if self.get_current_card_utility_ev(game, self) < 0:
            return False
        players = self.get_players(game)
        values = []
        ratios = []
        for i, player in enumerate(players):
            card_util = self.get_current_card_utility(game, player)
            chip_util = self.get_current_chip_utility(game, player, i) if i != 0 else 0
            values.append(card_util + chip_util)
            if card_util >= 0:
                ratios.append(99999)
            else:
                ratios.append(chip_util / -card_util)

        # print("Extortion values", values)
        # print("Extortion ratios", ratios)
        if values[0] < 0 or any(v >= 0 for v in values[1:]):
            return False

        return all(r < self.hyperparams["extortion_threshold"] for r in ratios[1:])

    # How much the player values the chips on the current card (or how many chips will be there when it's their turn)
    def get_current_chip_utility(self, game, player, turns_until=0):
        card_chips = game.get_chips_on_card() + turns_until
        player_chips = player.get_chips()
        chip_utility_factor = self.hyperparams["chip_utility_factor"]
        chip_utility_scale = self.hyperparams["chip_utility_scale"]

        # inverse points - positive is GOOD, negative BAD
        return card_chips * (
            1 + chip_utility_factor * 2.71828 ** (-chip_utility_scale * player_chips)
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

    # How the current card affects the given players score (or potential future score)
    # Ignores chips on card
    def get_current_card_utility_ev(self, game, player):
        cards = player.get_cards()
        curr_card = game.get_current_card()
        revealed_cards = self.get_all_revealed_cards(game)
        curr_score = self.get_player_card_score(cards)

        run_consideration_range = range(
            curr_card - self.RUN_CONSIDERATION_SIZE,
            curr_card + self.RUN_CONSIDERATION_SIZE + 1,
        )
        subrun_scores = {}
        subrun_probs = {}
        for low in range(curr_card - self.RUN_CONSIDERATION_SIZE, curr_card + 1):
            for high in range(curr_card, curr_card + self.RUN_CONSIDERATION_SIZE + 1):
                run_prob = reduce(lambda x,y: x*y, (self.get_card_prob(c, game, player) for c in range(low, high + 1)))
                no_extra_low_prob, no_extra_high_prob = 1,1
                if low != curr_card - self.RUN_CONSIDERATION_SIZE:
                    no_extra_low_prob = (1-self.get_card_prob(low-1, game, player))
                if high != curr_card + self.RUN_CONSIDERATION_SIZE:
                    no_extra_high_prob = (1-self.get_card_prob(high+1, game, player))
                subrun_scores[(low, high)] = self.get_player_card_score(
                    sorted(set(cards + list(range(low, high + 1))))
                )
                subrun_probs[(low, high)] = run_prob * no_extra_low_prob * no_extra_high_prob

        ev = 0
        for i, j in subrun_probs.keys():
            component = subrun_probs[(i, j)] * (curr_score - subrun_scores[(i, j)])
            # print((i, j), round(subrun_probs[(i, j)],2), subrun_scores[(i, j)])
            ev += component
        # print(sum(subrun_probs.values()))

        # connector_exists_probs = []
        # connector_exists_values = []
        # for run_direction in [-1, +1]:
        #     if curr_card + run_direction in revealed_cards:
        #         continue
        #     if curr_card + run_direction * 2 not in cards:
        #         continue
        #     curr_score = self.get_player_card_score(cards)
        #     new_score = self.get_player_card_score(
        #         sorted(cards + [curr_card, curr_card + run_direction])
        #     )
        #     connector_exists_prob = game.get_deck_length() / (
        #         game.get_deck_length() + 9
        #     )
        #     connector_exists_probs.append(connector_exists_prob)
        #     connector_exists_values.append(curr_score - new_score)

        # curr_score = self.get_player_card_score(cards)
        # new_score = self.get_player_card_score(sorted(cards + [curr_card]))

        # single_connector_val = (curr_score - new_score) * (1 - sum(connector_exists_probs)) + sum(
        #     prob * v for prob, v in zip(connector_exists_probs, connector_exists_values)
        # )

        # print("OLDEST SYSTEM", curr_score - new_score)
        # print("OLD SYSTEM", single_connector_val)
        # print("NEW SYSTEM", ev)

        return ev

    def get_card_prob(self, card, game, player):
        player_cards = player.get_cards()
        curr_card = game.get_current_card()
        revealed_cards = self.get_all_revealed_cards(game)
        if card == curr_card or card in player_cards:
            return 1
        elif card in revealed_cards:
            return 0

        return game.get_deck_length() / (game.get_deck_length() + 9)

    def get_all_revealed_cards(self, game):
        cards = []
        for player in self.get_players(game):
            cards.extend(player.get_cards())
        return cards

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

    def sub_lists(l):
        lists = [[]]
        for i in range(len(l) + 1):
            for j in range(i):
                lists.append(l[j:i])
        return lists
