# coding=utf-8

from zentropi.symbols import KINDS


def test_kind():
    assert KINDS.TIMER.value == -1
    assert KINDS.UNSET.value == 0
    assert KINDS.COMMAND.value == 1
    assert KINDS.EVENT.value == 2
    assert KINDS.MESSAGE.value == 3
    assert KINDS.REQUEST.value == 4
    assert KINDS.RESPONSE.value == 5
    assert KINDS.STATE.value == 6
