# coding=utf-8
from typing import Optional, Union
from uuid import uuid4

from zentropi.defaults import \
    FRAME_NAME_MAX_LENGTH
from zentropi.events import Event, Events
from zentropi.frames import Frame
from zentropi.handlers import Handler
from zentropi.messages import Message, Messages
from zentropi.states import State, States
from zentropi.symbols import KINDS
from zentropi.utils import validate_name


class Zentropian(object):
    def __init__(self, name=None):
        from .connections.registry import ConnectionRegistry
        self._name = validate_name(name) if name else uuid4().hex
        callback = self._trigger_frame_handler
        self.states = States(callback=callback)
        self.events = Events(callback=callback)
        self.messages = Messages(callback=callback)
        self._connections = ConnectionRegistry(self)
        self.inspect_handlers()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = validate_name(name)

    def add_handler(self, handler):
        if handler.kind == KINDS.EVENT:
            self.events.add_handler(handler.name, handler)
        elif handler.kind == KINDS.STATE:
            self.states.add_handler(handler.name, handler)
        elif handler.kind == KINDS.MESSAGE:
            self.messages.add_handler(handler.name, handler)
        else:  # pragma: no cover
            raise ValueError('Unknown handler kind: {}'.format(handler.kind))

    def inspect_handlers(self):
        for attribute_name in dir(self):
            attr = getattr(self, attribute_name)
            if not callable(attr) or not hasattr(attr, 'meta'):
                continue
            for handler in attr.meta:
                self.add_handler(handler)

    def handle_frame(self, frame):
        if isinstance(frame, Event):
            frame, handlers = self.events.match(frame)
        elif isinstance(frame, State):
            frame, handlers = self.states.match(frame)
        elif isinstance(frame, Message):
            frame, handlers = self.messages.match(frame)
        else:
            raise ValueError('Unknown frame {!r} with kind {!r}'
                             ''.format(frame.name, KINDS(frame.kind)))  # todo: KINDS might throw an exception?
        for handler in handlers:
            self._trigger_frame_handler(frame=frame, handler=handler, internal=True)

    def handle_return(self, frame, return_value):
        """Original frame and returned value from handler."""
        if isinstance(frame, Event):
            return return_value
        elif isinstance(frame, State):
            return return_value
        elif isinstance(frame, Message):
            if len(return_value) > FRAME_NAME_MAX_LENGTH:
                name = return_value[:FRAME_NAME_MAX_LENGTH - 5] + '...'
            else:
                name = return_value
            self.message(name=name,
                         data={'text': return_value},
                         reply_to=frame.id)
        else:
            raise NotImplementedError()

    def _trigger_frame_handler(self, frame: Frame, handler: Handler, internal=False):
        if isinstance(frame, Message) and frame.source == self.name:
            return
        if isinstance(frame, Event) and frame.source != self.name and frame.name.startswith('***'):
            return
        if handler.run_async:
            raise NotImplementedError(
                'Async handlers are not supported '
                'by the base Zentropian class. '
                'Please use Agent.')
        payload = []  # type: list
        if handler.pass_self:
            payload.append(self)
        if handler.kind != KINDS.TIMER:
            payload.append(frame)
        return_value = handler(*payload)
        return self.handle_return(frame, return_value)

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

    def on_message(self, name, *, exact=True, parse=False, fuzzy=False):
        def wrapper(handler):
            handler_obj = Handler(kind=KINDS.MESSAGE, name=name, handler=handler,
                                  exact=exact, parse=parse, fuzzy=fuzzy)
            self.messages.add_handler(name, handler_obj)
            return handler

        return wrapper

    def emit(self, name, data=None, space=None, internal=False, reply_to=None):
        event = self.events.emit(name=name, data=data, space=space, internal=internal,
                                 source=self.name, reply_to=reply_to)
        if not internal and self._connections.connected:
            self._connections.broadcast(frame=event)
        return event

    def message(self, name, data=None, space=None, internal=False, reply_to=None):
        message = self.messages.message(name=name, data=data, space=space, internal=internal,
                                        source=self.name, reply_to=reply_to)
        if not internal and self._connections.connected:
            self._connections.broadcast(frame=message)
            # print('broadcasting')
        return message

    def connect(self, endpoint, *, tag='default'):
        self._connections.connect(endpoint, tag=tag)

    def bind(self, endpoint, *, tag='default'):
        self._connections.bind(endpoint, tag=tag)

    def join(self, space, *, tags: Optional[Union[list, str]] = None):
        self._connections.join(space, tags=tags)

    def leave(self, space, *, tags: Optional[Union[list, str]] = None):
        self._connections.leave(space, tags=tags)

    def close(self, *, endpoint: Optional[str] = None, tags: Optional[Union[list, str]] = None):
        """Closes all connections if no endpoint or tags given."""
        if endpoint and tags:
            raise ValueError('Expected either endpoint: {!r} or tags: {!r}.'
                             ''.format(endpoint, tags))
        elif endpoint:
            connections = self._connections.connections_by_endpoint(endpoint)
        elif tags:
            connections = self._connections.connections_by_tags(tags)
        else:
            connections = self._connections.connections
        for connection in connections:
            connection.close()


def on_event(name, *, exact=True, parse=False, fuzzy=False):
    def wrapper(handler):
        handler_obj = Handler(kind=KINDS.EVENT, name=name, handler=handler,
                              exact=exact, parse=parse, fuzzy=fuzzy)
        if hasattr(handler, 'meta'):
            handler.meta.append(handler_obj)
        else:
            handler.meta = [handler_obj]
        return handler

    return wrapper


def on_state(name, *, exact=True, parse=False, fuzzy=False):
    def wrapper(handler):
        handler_obj = Handler(kind=KINDS.STATE, name=name, handler=handler,
                              exact=exact, parse=parse, fuzzy=fuzzy)
        if hasattr(handler, 'meta'):
            handler.meta.append(handler_obj)
        else:
            handler.meta = [handler_obj]
        return handler

    return wrapper


def on_message(name, *, exact=True, parse=False, fuzzy=False):
    def wrapper(handler):
        handler_obj = Handler(kind=KINDS.MESSAGE, name=name, handler=handler,
                              exact=exact, parse=parse, fuzzy=fuzzy)
        if hasattr(handler, 'meta'):
            handler.meta.append(handler_obj)
        else:
            handler.meta = [handler_obj]
        return handler

    return wrapper
