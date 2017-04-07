# coding=utf-8
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
        self.states = States(callback=self._trigger_frame_handler)
        self.events = Events(callback=self._trigger_frame_handler)
        self._name = validate_name(name) if name else uuid4().hex

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = validate_name(name)

    def _trigger_frame_handler(self, frame: Frame, handler: Handler, internal=False):
        if handler.run_async:
            raise NotImplementedError(
                'Async handlers are not supported '
                'by the base Zentropian class. '
                'Please use Entity or Agent.')
        return_value = handler(frame)
        self.logger.debug('Called handler: {} with frame: {}, it returned: {}'
                          ''.format(handler.name, frame.name, return_value))
        if not internal:
            pass  # todo: broadcast over connections.
        return return_value

    def on_state(self, name, exact=True, parse=False, fuzzy=False):
        def wrapper(handler):
            handler_obj = Handler(kind=KINDS.STATE, name=name, handler=handler,
                                  exact=exact, parse=parse, fuzzy=fuzzy)
            self.states.add_handler(name, handler_obj)
            return handler

        return wrapper

    def on_event(self, name, exact=True, parse=False, fuzzy=False):
        def wrapper(handler):
            handler_obj = Handler(kind=KINDS.EVENT, name=name, handler=handler,
                                  exact=exact, parse=parse, fuzzy=fuzzy)
            self.events.add_handler(name, handler_obj)
            return handler

        return wrapper

    def emit(self, name, data=None, space=None, internal=False):
        self.events.emit(name=name, data=data, space=space, internal=internal)
