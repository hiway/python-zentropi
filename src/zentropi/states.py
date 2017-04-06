# coding=utf-8

from collections import UserDict

from .fields import Field
from .frames import State
from .handlers import HandlerRegistry


class States(UserDict):
    def __init__(self, callback=None):
        super().__init__()
        if callback and not callable(callback):
            raise ValueError('Expected a callable for callback, got: {}'
                             ''.format(callback))
        self._trigger_frame_handler = callback
        self._handlers = HandlerRegistry()

    def _add_state(self, name, value_or_state):
        if isinstance(value_or_state, Field):
            state = value_or_state
        else:
            state = Field(value_or_state)
        state.name = '{}.{}'.format(self.__class__.__name__, name)
        self.data[name] = state

    def _get_state(self, name):
        state = self.data[name]
        if not isinstance(state, Field):
            raise ValueError('Expected instance of Field, got: {}'
                             ''.format(state))
        return state.value

    def _update_state(self, name, value):
        should_update = True
        state = self.data[name]
        if not isinstance(state, Field):
            raise ValueError('Expected instance of Field, got: {}'
                             ''.format(state))
        if self._trigger_frame_handler:
            frame = State(name, data={'value': value, 'last': state.value})
            frame, handlers = self._handlers.match(frame)
            for handler in handlers:  # todo: should_update tied to last handler's return value, use all()/any()? Why?
                should_update = self._trigger_frame_handler(
                    frame=frame, handler=handler, internal=True)
            if not isinstance(should_update, bool):
                raise ValueError('Expected bool as return value '
                                 'from state callback, got: {}'
                                 ''.format(should_update))
        if should_update:  # Default is True if not callback set.
            state.value = value
            self.data[name] = state

    def _remove_state(self, name):
        del self.data[name]

    def __getattribute__(self, item):
        if item in ['data', 'callback'] or item.startswith('_'):
            return object.__getattribute__(self, item)
        try:
            attr = object.__getattribute__(self, item)
            if attr and callable(attr):
                return attr
        except AttributeError:
            return self._get_state(item)

    def __setattr__(self, key, value):
        if (key in ['data', 'callback'] or key.startswith('_') or
                (value and callable(value))):
            object.__setattr__(self, key, value)
            return
        if key in self.data:
            self._update_state(key, value)
            return
        self._add_state(key, value)

    def __getitem__(self, item):
        return self._get_state(item)

    def __setitem__(self, key, value):
        if key in self.data:
            self._update_state(key, value)
            return
        self._add_state(key, value)

    def __delitem__(self, key):
        self._remove_state(key)

    def __delattr__(self, item):
        self._remove_state(item)

    @property
    def callback(self):
        return self._trigger_frame_handler

    @callback.setter
    def callback(self, callback):
        if callback is not None and not callable(callback):
            raise ValueError('Expected a callable for callback, got: {}'
                             ''.format(callback))
        self._trigger_frame_handler = callback

    def describe(self):
        fields = [{'name': name, 'field': field.describe()}
                  for name, field in self.data.items()]
        expects = {}  # todo: gather handler names (and help?)
        return {'states': {'fields': fields, 'expects': expects}}

    def add_handler(self, name, handler):
        self._handlers.add_handler(name, handler)

    def remove_handler(self, name, handler):
        self._handlers.remove_handler(name, handler)
