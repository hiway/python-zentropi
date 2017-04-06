# coding=utf-8

from zentropi.symbols import Kinds


def test_kinds():
    assert Kinds.timer.value == -1
    assert Kinds.unset.value == 0
    assert Kinds.command.value == 1
    assert Kinds.event.value == 2
    assert Kinds.message.value == 3
    assert Kinds.request.value == 4
    assert Kinds.response.value == 5
    assert Kinds.state.value == 6
