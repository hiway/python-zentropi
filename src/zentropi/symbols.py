# coding=utf-8

from enum import Enum, unique


@unique
class Kind(Enum):
    timer = -1
    unset = 0
    command = 1
    event = 2
    message = 3
    request = 4
    response = 5
    state = 6
