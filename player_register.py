from players.basic import BasicPlayer
from players.dumbo import DumboPlayer
from players.danbot import DanBot, DanBotFactory
from players.dumboSally import DumboSally

PLAYER_REGISTER = [
    BasicPlayer,
    DumboPlayer,
    DanBot,
    DumboSally,
    DanBotFactory(True)
]
