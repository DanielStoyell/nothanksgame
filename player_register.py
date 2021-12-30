from players.basic import BasicPlayer
from players.dumbo import DumboPlayer
from players.danbot import DanBot
from players.NoProbablem import NoProbablemPlayer
from players.danbot import DanBot, DanBotFactory
from players.dumboSally import DumboSally

PLAYER_REGISTER = [
    DanBot,
    DanBot,
    DanBot,
    DumboSally,
    DanBotFactory(True)
]
