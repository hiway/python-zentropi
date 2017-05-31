# coding=utf-8
import pytest

from zentropi import Field
from zentropi.handlers import Handler
from zentropi.states import States
from zentropi.symbols import KINDS


def test_states():
    states = States()
    states.hello = Field('Hello, world.')
    assert states.hello == 'Hello, world.'
    states.hello = 'Hi'
    assert states.hello == 'Hi'
    states.a_number = 21
    assert states.a_number == 21


def test_states_with_callback():
    def _trigger_frame_handler(frame, handler, internal):
        assert frame
        assert handler
        assert internal
        return handler(frame)

    def test_handler(state):
        assert state.name == 'the_answer'
        assert state.data.value in [42, 0]
        return True

    states = States()
    a_handler = Handler(KINDS.STATE, 'the_answer', test_handler)
    states.add_handler('the_answer', handler=a_handler)
    states.remove_handler('the_answer', handler=a_handler)
    states.add_handler('the_answer', handler=a_handler)
    states.the_answer = Field()
    states.callback = _trigger_frame_handler
    assert states.callback == _trigger_frame_handler
    states.the_answer = 42
    assert states['the_answer'] == 42
    states['the_answer'] = 0
    assert states['the_answer'] == 0
    states['not_the_answer'] = 'lol cats'
    assert states['not_the_answer'] == 'lol cats'
    del states['not_the_answer']
    assert 'not_the_answer' not in states
    del states.the_answer
    assert 'the_answer' not in states


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_state_fails_with_invalid_callback():
    states = States()
    states.callback = "none shall pass"


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_state_fails_with_invalid_callback_on_init():
    states = States(callback="none shall pass")


def test_states_describe():
    def _trigger_frame_handler(frame, handler, internal):
        assert frame
        assert handler
        assert internal
        return handler(frame)

    def test_handler(state):
        assert state.name == 'the_answer'
        assert state.data.value in [42, 0]
        return True

    states = States()

    a_handler = Handler(KINDS.STATE, 'the_answer', test_handler)
    states.add_handler('the_answer', handler=a_handler)
    states.the_answer = Field()
    states.callback = _trigger_frame_handler
    assert states.callback == _trigger_frame_handler
    states.the_answer = 42
    assert states.the_answer is 42

    assert states.describe() == {
            'expects': [{
                # 'help': None,
                'kind': KINDS.STATE.name,
                'match': 'exact',
                'name': 'the_answer',
            }],
            'fields': [{
                'kind': 'Field',
                'name': 'the_answer',
                'value': 42
            }]
    }


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_states_fails_on_unexpected_field():
    states = States()
    states.data['whoa'] = 'oh noes!'  # Should not be directly set
    assert states.whoa == 'oh noes!'  # Fails


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_states_fails_for_directly_set_field():
    states = States()
    states.data['whoa'] = 'oh noes!'  # Should not be directly set
    states.whoa = 'oh noes!'  # Fails


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_states_with_callback_fails():
    def _trigger_frame_handler(frame, handler, internal):
        assert frame
        assert handler
        assert internal
        return handler(frame)

    def test_handler(state):
        assert state.name == 'the_answer'
        assert state.data.value in [42, 0]

    states = States()
    a_handler = Handler(KINDS.STATE, 'the_answer', test_handler)
    states.add_handler('the_answer', handler=a_handler)
    states.the_answer = Field()
    states.callback = _trigger_frame_handler
    assert states.callback == _trigger_frame_handler
    states.the_answer = 42


def test_states_with_callback_no_update():
    def _trigger_frame_handler(frame, handler, internal):
        assert frame
        assert handler
        assert internal
        return handler(frame)

    def test_handler(state):
        assert state.name == 'the_answer'
        assert state.data.value in [42, 0]
        return False

    states = States()
    a_handler = Handler(KINDS.STATE, 'the_answer', test_handler)
    states.add_handler('the_answer', handler=a_handler)
    states.the_answer = Field()
    states.callback = _trigger_frame_handler
    assert states.callback == _trigger_frame_handler
    states.the_answer = 42
    assert states.the_answer is None
