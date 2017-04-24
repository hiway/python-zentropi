# coding=utf-8
from enum import Enum, unique


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
