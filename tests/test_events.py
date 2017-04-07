# coding=utf-8

import pytest

from zentropi import Events
from zentropi.handlers import Handler
from zentropi.symbols import KINDS


def test_events():
    def trigger_frame_handler(frame, handler, internal):
        assert frame
        assert handler
        assert internal is False
        return handler(frame)

    def test_handler(event):
        assert event.name == 'ping'

    events = Events(callback=trigger_frame_handler)
    handler = Handler(KINDS.STATE, 'the_answer', test_handler)
    events.add_handler('ping', handler=handler)
    events.emit('ping')
    assert handler in events._handlers._handlers['ping']
    events.remove_handler('ping', handler=handler)
    assert handler not in events._handlers._handlers['ping']


def test_events_set_callback_later():
    def trigger_frame_handler(frame, handler, internal):
        return handler(frame)

    def test_handler(event):
        assert event.name == 'ping'

    events = Events()
    events.callback = trigger_frame_handler
    assert events.callback == trigger_frame_handler
    handler = Handler(KINDS.STATE, 'the_answer', test_handler)
    events.add_handler('ping', handler=handler)
    events.emit('ping')


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_events_return_value_from_event_fails():
    def trigger_frame_handler(frame, handler, internal):
        return handler(frame)

    def test_handler(event):
        assert event.name == 'ping'
        return True

    events = Events(callback=trigger_frame_handler)
    handler = Handler(KINDS.STATE, 'the_answer', test_handler)
    events.add_handler('ping', handler=handler)
    events.emit('ping')


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_events_invalid_callback():
    _ = Events(callback="fail")


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_events_invalid_callback_setter():
    events = Events()
    events.callback = "fail"
