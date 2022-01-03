from player import *


class DanBot(PlayerBase):
    NAME = "DanBot"
    HYPERPARAMS = {
        # How much to additionally weight each "getting screwed" in adjusting the extort utility buffer
        "screwed_buffer_weight": .5,
        # Additional utility caution in estimations of card utility for other players while extorting
        "extort_utility_buffer": 3.2,
        # With exponential decay, the maximum utility penalty for low chips
        "max_low_chip_penalty": 15,
        # The fuzz factor on the utility of chips (this + proportion of deck left + low chip penalty)
        "chip_utility_modifier": 1,
        # The expected value a card will yield in chips when picked up
        "card_chip_value_ratio": .32,
        # The fuzz factor on the raw card probability computation
        "get_card_prob_modifier": .75,
    }

    MAX_DECK_SIZE = 24

    def __init__(self, *args, **kwargs):
        if "hyperparams" in kwargs:
            self.hyperparams = kwargs["hyperparams"]
            del kwargs["hyperparams"]
        else:
            self.hyperparams = self.HYPERPARAMS

        super().__init__(*args, **kwargs)

        self.potential_deck = set(range(3, 36))
        self.times_screwed = 0
        self.currently_extorting = False

    def decide_impl(self, game):
        # If no chips, have to take
        if self.get_chips() == 0:
            return TAKE

        # If can collude to let friendly bot win, take infinitely
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
        # If taking the card would hurt me, decline
        if take_utility > 0:
            return DECLINE

        should_extort = self.get_should_extort(game.get_players(), game)

        # If taking the card would help me but hurt others, extort
        if should_extort:
            self.currently_extorting = True
            return DECLINE

        # If taking the card would help me and can't extort, take
        return TAKE



    def turn_update_impl(self, game, player, decision):
        if game.get_current_card() in self.potential_deck:
            self.potential_deck.remove(game.get_current_card())

        if decision == TAKE:
            if self.currently_extorting and player is not self:
                self.times_screwed += 1

            self.currently_extorting = False


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
        utility_decline = self.compute_player_utility(
            player,
            cards,
            chips-1,
            deck_length,
            current_card,
            players
        )
        utility_take = self.compute_player_utility(
            player,
            cards + [card],
            chips + chips_on_card,
            deck_length - 1,
            -1,
            players
        )

        # Utility is bad!
        return utility_take - utility_decline

    def compute_player_utility(self, player, cards, chips, deck_length, current_card, players):
        card_set_utility = self.get_card_set_utility(player, cards, current_card, deck_length, players)
        chip_utility = self.get_chip_utility(chips, deck_length)

        return card_set_utility + chip_utility

    def get_chip_utility(self, chips, deck_length):
        if chips < 0:
            return 1000000
        # low chip penalty should scale with end of game
        return (-chips) * (self.hyperparams["chip_utility_modifier"] + (deck_length / self.MAX_DECK_SIZE)) + (self.hyperparams["max_low_chip_penalty"]/(chips+1))

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
        chip_value = card * self.hyperparams["card_chip_value_ratio"]

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

        return prob_card_in_deck * steal_modifier * self.hyperparams["get_card_prob_modifier"]

    def get_score_for_cards(self, cards):
        cards = sorted(cards)
        score = 0

        for i in range(len(cards)):
            if i == 0 or cards[i] != cards[i-1] + 1:
                score += cards[i]

        return score

    def get_should_extort(self, players, game):
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

        return not any([u - self.get_extort_utility_buffer() < 0 for u in opponent_utilities])


    def mueller_investigation(self, game):
        colluders = [p for p in game.get_players() if (p is not self and self.NAME in p.get_name())]
        if len(colluders) == 0:
            return False
        non_colluders = [p for p in game.get_players() if (self.NAME not in p.get_name())]
        lowest_colluder_score = min([p.get_score() for p in colluders])

        should_collude = not any([p.get_score() <= lowest_colluder_score for p in non_colluders])

        return should_collude

    def get_extort_utility_buffer(self):
        return self.hyperparams["extort_utility_buffer"] * (1 + self.hyperparams["screwed_buffer_weight"] * self.times_screwed)


def DanBotFactory():
    hyperparams = DanBot.HYPERPARAMS.copy()
    param, value = random.choice(list(hyperparams.items()))

    hyperparams[param] = round(random.gauss(value, value/3), 2)
    name = f"DanBotVariant ({param}: {hyperparams[param]}) "

    class DanBotVariant(DanBot):
        NAME = name
        HYPERPARAMS = hyperparams

    return DanBotVariant
