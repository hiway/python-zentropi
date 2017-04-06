# coding=utf-8

from zentropi.symbols import KIND


def test_kind():
    assert KIND.TIMER.value == -1
    assert KIND.UNSET.value == 0
    assert KIND.COMMAND.value == 1
    assert KIND.EVENT.value == 2
    assert KIND.MESSAGE.value == 3
    assert KIND.REQUEST.value == 4
    assert KIND.RESPONSE.value == 5
    assert KIND.STATE.value == 6
