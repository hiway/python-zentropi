# coding=utf-8

from enum import Enum
from enum import unique


@unique
class KINDS(Enum):
    TIMER = -1
    UNSET = 0
    COMMAND = 1
    EVENT = 2
    MESSAGE = 3
    REQUEST = 4
    RESPONSE = 5
    STATE = 6


@unique
class SOURCES(Enum):
    DEFAULT = 0
    CONFIG = 1
    ENV = 2
    RUNTIME = 3
