# coding=utf-8
import inspect
from uuid import uuid4

from .events import Events
from .frames import Frame
from .handlers import Handler
from .states import States
from .symbols import KINDS
from .utils import log_to_stream
from .utils import logger
from .utils import validate_name


class Zentropian(object):
    logger = logger
    log_to_stream()

    def __init__(self, name=None):
        # self.logger = logger
        callback = self._trigger_frame_handler
        self.states = States(callback=callback)
        self.events = Events(callback=callback)
        self._name = validate_name(name) if name else uuid4().hex

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
                    # self.logger.debug('Inspect handler: {}:{}'.format(KINDS_NAMES[kind], name))
                    if handler.kind == KINDS.EVENT:
                        self.events.add_handler(handler.name, handler)
                    elif handler.kind == KINDS.STATE:
                        self.states.add_handler(handler.name, handler)
                    else:  # pragma: no cover
                        raise ValueError('Unknown handler kind: {}'.format(handler.kind))

    def _trigger_frame_handler(self, frame: Frame, handler: Handler, internal=False):
        if handler.run_async:
            raise NotImplementedError(
                'Async handlers are not supported '
                'by the base Zentropian class. '
                'Please use Entity or Agent.')
        print(inspect.getfullargspec(handler._handler))
        if 'self' in inspect.getfullargspec(handler._handler).args:
            return_value = handler(self, frame)
        else:
            return_value = handler(frame)
        self.logger.debug('Called handler: {} with frame: {}, it returned: {}'
                          ''.format(handler.name, frame.name, return_value))
        if not internal:
            pass  # todo: broadcast over connections.
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
        self.events.emit(name=name, data=data, space=space, internal=internal)


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
