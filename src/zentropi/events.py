# coding=utf-8

from .frames import Event
from .handlers import HandlerRegistry


class Events(object):
    """
    class Zentropian:
        self.events = Events(callback=self._trigger_frame_handler)


    zen.emit('event-name', data={}, internal=False)

    @zen.on_event('event-name', parse=True)
    def handle_event_name(event):
        pass
    """

    # todo: describe

    def __init__(self, callback=None):
        self._handlers = HandlerRegistry()
        if callback and not callable(callback):
            raise ValueError('Expected a callable for callback, got: {}'
                             ''.format(callback))
        self._trigger_frame_handler = callback

    def add_handler(self, name, handler):
        self._handlers.add_handler(name, handler)

    def remove_handler(self, name, handler):
        self._handlers.remove_handler(name, handler)

    @property
    def callback(self):
        return self._trigger_frame_handler

    @callback.setter
    def callback(self, callback):
        if callback and not callable(callback):
            raise ValueError('Expected a callable for callback, got: {}'
                             ''.format(callback))
        self._trigger_frame_handler = callback

    def emit(self, name, data=None, space=None, internal=False):
        frame_ = Event(name=name, data=data, space=space)
        frame, handlers = self._handlers.match(frame=frame_)
        for handler in handlers:
            ret_val = self._trigger_frame_handler(
                frame=frame, handler=handler, internal=internal)
            if ret_val is not None:
                raise ValueError('Returning values from event handler has no effect.')
