"""
Created by Epic at 12/27/20
"""

"""
Created by Epic at 10/13/20
Original script by FireDiscordBot on GitHub
"""

import logging
from copy import copy
from logging import Logger, DEBUG
import sys

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def getcolor(color=None):
    return COLOR_SEQ % (30 + (color or WHITE))


def formatter_message(message):
    for k, v in COLORS.items():
        message = message.replace(k, v)
    return message


LEVELS = {
    "WARNING": YELLOW,
    "INFO": GREEN,
    "DEBUG": BLUE,
    "CRITICAL": YELLOW,
    "ERROR": RED
}

COLORS = {
    "$GREEN": getcolor(GREEN),
    "$BLUE": getcolor(BLUE),
    "$RED": getcolor(RED),
    "$YELLOW": getcolor(YELLOW),
    "$BLACK": getcolor(BLACK),
    "$MAGENTA": getcolor(MAGENTA),
    "$CYAN": getcolor(CYAN),
    "$WHITE": getcolor(WHITE),
    "$RESET": RESET_SEQ,
    "$BOLD": BOLD_SEQ
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg):
        super().__init__(msg)

    def format(self, record):
        record = copy(record)
        levelname = record.levelname
        if levelname in LEVELS:
            levelname_color = COLOR_SEQ % (30 + LEVELS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
            for k, v in COLORS.items():
                record.msg = str(record.msg).replace(k, v)
        return super().format(record)


def basicConfig(logger: Logger):
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setLevel(DEBUG)
    color_format = formatter_message(
        "[$BOLD%(name)s$RESET][%(levelname)s] %(message)s $RESET($BOLD%(filename)s$RESET:%(lineno)d)")
    stdout.setFormatter(ColoredFormatter(color_format))
    logger.addHandler(stdout)
