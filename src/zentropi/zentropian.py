# coding=utf-8
import inspect
from typing import Optional
from typing import Union
from uuid import uuid4

from .events import Event
from .events import Events
from .frames import Frame
from .handlers import Handler
from .states import State
from .states import States
from .symbols import KINDS
from .utils import validate_name


class Zentropian(object):
    def __init__(self, name=None):
        from .connections.registry import ConnectionRegistry
        self._name = validate_name(name) if name else uuid4().hex
        callback = self._trigger_frame_handler
        self.states = States(callback=callback)
        self.events = Events(callback=callback)
        self._connections = ConnectionRegistry(self)
        self.inspect_handlers()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = validate_name(name)

    def inspect_handlers(self):
        for attribute_name in self.__dir__():
            attr = getattr(self, attribute_name)
            if not callable(attr):
                continue
            if hasattr(attr, 'meta'):
                for handler in attr.meta:
                    if handler.kind == KINDS.EVENT:
                        self.events.add_handler(handler.name, handler)
                    elif handler.kind == KINDS.STATE:
                        self.states.add_handler(handler.name, handler)
                    else:  # pragma: no cover
                        raise ValueError('Unknown handler kind: {}'.format(handler.kind))

    def handle_frame(self, frame):
        if isinstance(frame, Event):
            frame, handlers = self.events.match(frame)
        elif isinstance(frame, State):
            frame, handlers = self.states.match(frame)
        else:
            raise ValueError('Unknown frame {!r} with kind {!r}'
                             ''.format(frame.name, KINDS(frame.kind)))  # todo: KINDS might throw an exception?
        for handler in handlers:
            self._trigger_frame_handler(frame=frame, handler=handler, internal=True)

    def _trigger_frame_handler(self, frame: Frame, handler: Handler, internal=False):
        if handler.run_async:
            raise NotImplementedError(
                'Async handlers are not supported '
                'by the base Zentropian class. '
                'Please use Entity or Agent.')
        if 'self' in inspect.getfullargspec(handler._handler).args:
            return_value = handler(self, frame)
        else:
            return_value = handler(frame)
        return return_value

    def on_state(self, name, *, exact=True, parse=False, fuzzy=False):
        def wrapper(handler):
            handler_obj = Handler(kind=KINDS.STATE, name=name, handler=handler,
                                  exact=exact, parse=parse, fuzzy=fuzzy)
            self.states.add_handler(name, handler_obj)
            return handler

        return wrapper

    def on_event(self, name, *, exact=True, parse=False, fuzzy=False):
        def wrapper(handler):
            handler_obj = Handler(kind=KINDS.EVENT, name=name, handler=handler,
                                  exact=exact, parse=parse, fuzzy=fuzzy)
            self.events.add_handler(name, handler_obj)
            return handler

        return wrapper

    def emit(self, name, data=None, space=None, internal=False):
        event = self.events.emit(name=name, data=data, space=space, internal=internal, source=self.name)
        if not internal and self._connections.connected:
            self._connections.broadcast(frame=event)
        return event

    def connect(self, endpoint, *, tag='default'):
        self._connections.connect(endpoint, tag=tag)

    def bind(self, endpoint, *, tag='default'):
        self._connections.bind(endpoint, tag=tag)

    def join(self, space, *, tags: Optional[Union[list, str]] = None):
        self._connections.join(space, tags=tags)


def on_event(name, *, exact=True, parse=False, fuzzy=False):
    def wrapper(handler):
        handler_obj = Handler(kind=KINDS.EVENT, name=name, handler=handler,
                              exact=exact, parse=parse, fuzzy=fuzzy)
        if hasattr(handler, 'meta'):
            handler.meta.append(handler_obj)
        else:
            handler.meta = [handler_obj, ]
        return handler

    return wrapper


def on_state(name, *, exact=True, parse=False, fuzzy=False):
    def wrapper(handler):
        handler_obj = Handler(kind=KINDS.STATE, name=name, handler=handler,
                              exact=exact, parse=parse, fuzzy=fuzzy)
        if hasattr(handler, 'meta'):
            handler.meta.append(handler_obj)
        else:
            handler.meta = [handler_obj, ]
        return handler

    return wrapper
