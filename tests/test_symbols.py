# coding=utf-8

from zentropi.symbols import Kind


def test_kind():
    assert Kind.timer.value == -1
    assert Kind.unset.value == 0
    assert Kind.command.value == 1
    assert Kind.event.value == 2
    assert Kind.message.value == 3
    assert Kind.request.value == 4
    assert Kind.response.value == 5
    assert Kind.state.value == 6
