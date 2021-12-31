from player import *


class DanBot(PlayerBase):
    NAME = "DanBot"
    GET_CARD_PROB_MODIFIER = .8
    CARD_CHIP_VALUE_RATIO = .3
    CHIP_UTILITY_MODIFIER = 1
    MAX_LOW_CHIP_PENALTY = 20
    EXTORT_UTILITY_BUFFER = 7 # Maybe lower in games with competent opponents?

    def __init__(self, *args, **kwargs):
        # Must call super if you define your own constructor
        super().__init__(*args, **kwargs)

        self.potential_deck = set(range(3, 36))

    def decide_impl(self, game):
        if self.get_chips() == 0:
            return TAKE

        # if self.mueller_investigation(game):
        #     return TAKE

        take_utility = self.take_card_utility(
            self,
            game.get_current_card(),
            game.get_chips_on_card(),
            self.get_cards(),
            self.get_chips(),
            game.get_deck_length(),
            game.get_current_card(),
            game.get_players()
        )
        if take_utility > 0:
            return DECLINE

        players = game.get_players()
        self_index = players.index(self)
        opponents = (players[self_index:] + players[:self_index])[1:]

        opponent_utilities = [self.take_card_utility(
            p,
            game.get_current_card(),
            game.get_chips_on_card()+i+1,
            p.get_cards(),
            p.get_chips(),
            game.get_deck_length(),
            game.get_current_card(),
            game.get_players()
        ) for i,p in enumerate(opponents) if p is not self]

        if any([u - self.EXTORT_UTILITY_BUFFER < 0 for u in opponent_utilities]):
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

    def take_card_utility(self, player, card, chips_on_card, cards, chips, deck_length, current_card, players):
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

        # Utility is bad!
        return utility_after - utility_before

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

    def mueller_investigation(self, game):
        colluders = [p for p in game.get_players() if (p is not self and self.NAME in p.get_name())]
        non_colluders = [p for p in game.get_players() if (self.NAME not in p.get_name())]
        lowest_colluder_score = min([p.get_score() for p in colluders])

        should_collude = not any([p.get_score() <= lowest_colluder_score for p in non_colluders])

        return should_collude



def DanBotFactory():
    get_card_prob_modifier = DanBot.GET_CARD_PROB_MODIFIER
    card_chip_value_ratio = DanBot.CARD_CHIP_VALUE_RATIO
    chip_utility_modifier = DanBot.CHIP_UTILITY_MODIFIER
    max_low_chip_penalty = DanBot.MAX_LOW_CHIP_PENALTY

    which = random.randint(1,4)
    if which == 1:
        get_card_prob_modifier = round(random.gauss(.8, .8/2), 3)
        name = f"DanBotVariant (get_card_prob_mod: {get_card_prob_modifier}) "
    elif which == 2:
        card_chip_value_ratio = round(random.gauss(.3, .3/2), 3)
        name = f"DanBotVariant (card_chip_value_ratio: {card_chip_value_ratio}) "
    elif which == 3:
        chip_utility_modifier = round(random.gauss(1, 1/2), 3)
        name = f"DanBotVariant (chip_utility_modifier: {chip_utility_modifier}) "
    elif which == 4:
        max_low_chip_penalty = round(random.gauss(15, 15/2), 3)
        name = f"DanBotVariant (max_low_chip_penalty: {max_low_chip_penalty}) "

    class DanBotVariant(DanBot):
        NAME = name
        GET_CARD_PROB_MODIFIER = get_card_prob_modifier
        CARD_CHIP_VALUE_RATIO = card_chip_value_ratio
        CHIP_UTILITY_MODIFIER = chip_utility_modifier
        MAX_LOW_CHIP_PENALTY = max_low_chip_penalty

    return DanBotVariant
