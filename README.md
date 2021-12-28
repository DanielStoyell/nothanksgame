# nothanksgame
Implementation of the game "No Thanks!", with the ability for people to add bots that can act as players to compete against each other.

Implementing a new bot is a fairly simple process. There are two example files under the `players` folder.

1. Create a new class that extends `PlayerBase`
2. Give it a name! Add a `NAME` class field.
3. Implement `decide_impl()`. This is the core of your bot. It takes in the current game state, and outputs either `TAKE` or `DECLINE` (constants from `constants.py`). `TAKE` means you take the current card. `DECLINE` means you put one of your chips in rather than taking the card.
4. Implement `turn_update_impl`. This can do nothing, but it may be useful to keep track of internal states as you and other player take actions

You are allowed access to any getter functions within the `Game` and `Player` class, accessible from the `game` variable or the `self` variable (your bot's class instantiation). The one edge case here is that you're only allowed to call the `_get_chips()` function for your own class (yourself, `self._get_chips()`), not for other players (like `game.get_players()[0]._get_chips()`), hence the single underscore marking it as protected.
You're also allowed to store internal state for your bot. For example, you could keep track of the number of turns elapsed so far (or even other player's chip counts...).

Note that you're not allowed to return `DECLINE` if you have no chips. You'll be overridden and the game won't end. However, your bot probably shouldn't do it anyway.

# Tournament Scoring

Tournaments are played over a large number of rounds with 5 random players in each round. The player with the highest win percentage wins!
