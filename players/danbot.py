from player import *


class DanBot(PlayerBase):
    NAME = "DanBot"
    IS_PROBABILISTIC = False
    TAKE_RATIO = .4
    EXTORT_RATIO = .25
    GET_CARD_PROB_MODIFIER = .8
    CARD_CHIP_VALUE_RATIO = .3
    CHIP_UTILITY_MODIFIER = 1
    MAX_LOW_CHIP_PENALTY = 15

    def __init__(self, *args, **kwargs):
        # Must call super if you define your own constructor
        super().__init__(*args, **kwargs)

        self.potential_deck = set(range(3, 36))

    def decide_impl(self, game):
        if self.get_chips() == 0:
            return TAKE

        if self.IS_PROBABILISTIC:
            should_take = self.should_take_card(
                self,
                game.get_current_card(),
                game.get_chips_on_card(),
                self.get_cards(),
                self.get_chips(),
                game.get_deck_length(),
                game.get_current_card(),
                game.get_players()
            )
            if should_take:
                return TAKE
            else:
                return DECLINE


        ratio = self.get_ratio(game)
        if ratio >= self.TAKE_RATIO:
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

    def should_take_card(self, player, card, chips_on_card, cards, chips, deck_length, current_card, players):
        utility_before = self.compute_player_utility(
            player,
            cards,
            chips,
            deck_length,
            current_card,
            players
        )
        utility_after = self.compute_player_utility(
            player,
            cards + [card],
            chips + chips_on_card,
            deck_length - 1,
            -1,
            players
        )
        # print(f"Considering {card} with {chips_on_card} chips on it...")
        # print(f"Utility before: {utility_before} | Utility after: {utility_after}")

        # Utility is bad!
        return utility_after < utility_before

    def compute_player_utility(self, player, cards, chips, deck_length, current_card, players):
        card_set_utility = self.get_card_set_utility(player, cards, current_card, deck_length, players)
        chip_utility = self.get_chip_utility(chips, deck_length)

        return card_set_utility + chip_utility

    def get_chip_utility(self, chips, deck_length):
        # low chip penalty should scale with end of game
        return (-chips) * (self.CHIP_UTILITY_MODIFIER + (deck_length / 24)) + (self.MAX_LOW_CHIP_PENALTY/(chips+1))

    def get_card_set_utility(self, player, cards, current_card, deck_length, players):
        wanted_cards = self.get_run_cards_for_player(cards, current_card)
        score = self.get_score_for_cards(cards)

        expected_utilities = 0
        for card in wanted_cards:
            utility = self.get_card_utility(card, cards)
            prob = self.probability_get_wanted_card(player, card, deck_length, current_card, players)
            expected_utilities += utility * prob

        return score + expected_utilities

    def get_card_utility(self, card, current_cards):
        new_cards = current_cards + [card]
        score_diff = self.get_score_for_cards(new_cards) - self.get_score_for_cards(current_cards)
        chip_value = card * self.CARD_CHIP_VALUE_RATIO

        return score_diff - chip_value

    def probability_get_wanted_card(self, player, card, deck_length, current_card, players):
        if card not in self.potential_deck:
            return 0

        prob_card_in_deck = deck_length / (deck_length + 9)
        others_wanted = [None if p is player else card in self.get_run_cards_for_player(p.get_cards(), current_card) for p in players]
        player_pos = others_wanted.index(None)
        i = (player_pos - 1) % 5
        while i != player_pos:
            if others_wanted[i]:
                break
            i = (i-1) % 5

        dist = (player_pos - i) % 5
        if dist != 0:
            steal_modifier = dist / 5
        else:
            steal_modifier = 1

        return prob_card_in_deck * steal_modifier * self.GET_CARD_PROB_MODIFIER

    def get_score_for_cards(self, cards):
        cards = cards.copy()
        cards.sort()
        score = 0

        for i in range(len(cards)):
            if i == 0 or cards[i] != cards[i-1] + 1:
                score += cards[i]

        return score




def DanBotFactory(is_prob=False):
    extort_ratio = round(random.gauss(.25, .15), 2)
    take_ratio = round(random.gauss(.4, .2), 2)

    class DanBotVariant(DanBot):
        # NAME = f"DanBotVariant (take: {take_ratio} | extort {extort_ratio})"
        NAME = "DanBotProbability"
        TAKE_RATIO = take_ratio
        EXTORT_RATIO = extort_ratio
        IS_PROBABILISTIC = is_prob

    return DanBotVariant
