# coding=utf-8
from collections import defaultdict
from inspect import (
    getfullargspec,
    iscoroutinefunction
)

from fuzzywuzzy import fuzz, process
from parse import parse as string_parse
from sortedcontainers import SortedListWithKey

from zentropi.defaults import \
    MATCH_FUZZY_THRESHOLD
from zentropi.utils import (
    validate_handler,
    validate_kind,
    validate_name
)


class Handler(object):
    __slots__ = [
        '_kind', '_name', '_handler',
        '_meta', '_async', '_pass_self',
        '_match_exact', '_match_parse', '_match_fuzzy',
        '_ignore_case', '_length', '_filters'
    ]

    def __init__(self, kind, name, handler, meta=None,
                 exact=True, parse=False, fuzzy=False, ignore_case=False, **kwargs):
        if callable(handler) and not iscoroutinefunction(handler):
            self._async = False
        elif iscoroutinefunction(handler):
            self._async = True
        else:
            raise ValueError('Expected handler to be a callable '
                             '(function, method) or a coroutine function. '
                             'Got: {!r}'.format(handler))
        if 'self' in getfullargspec(handler).args:
            self._pass_self = True
        else:
            self._pass_self = False
        if meta is not None and not isinstance(meta, dict):
            raise ValueError('Expected meta to be of type dict. '
                             'Got: {!r}'.format(meta))
        if parse and fuzzy:
            raise ValueError('Expected only one of parse: {} or fuzzy: {} '
                             'to be True.'.format(parse, fuzzy))
        if parse or fuzzy:
            exact = False
        self._kind = validate_kind(kind)
        self._name = validate_name(name)
        self._handler = handler
        self._meta = meta
        self._match_exact = bool(exact)
        self._match_parse = bool(parse)
        self._match_fuzzy = bool(fuzzy)
        self._length = len(name)
        self._ignore_case = bool(ignore_case)
        self._filters = {k[1:]: a for k, a in kwargs.items() if k.startswith('_')}
        unexpected_kwargs = [k for k in kwargs if not k.startswith('_')]
        if unexpected_kwargs:
            raise AssertionError('Unexpected keyword arguments: {}\n'
                                 'Filters should be named as: {}'.format(', '.join(unexpected_kwargs),
                                                                         ', '.join(['_{}'.format(k)
                                                                                    for k in unexpected_kwargs])))

    def __call__(self, *args, **kwargs):
        return self._handler(*args, **kwargs)

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

    @property
    def meta(self):
        return self._meta

    @property
    def run_async(self):
        return self._async

    @property
    def pass_self(self):
        return self._pass_self

    @property
    def match_exact(self):
        return self._match_exact

    @property
    def match_parse(self):
        return self._match_parse

    @property
    def match_fuzzy(self):
        return self._match_fuzzy

    @property
    def ignore_case(self):
        return self._ignore_case

    @property
    def filters(self):
        return self._filters


class HandlerRegistry(object):
    def __init__(self):
        self._handlers = defaultdict(set)
        self._index_exact = SortedListWithKey(key=len)
        self._index_parse = SortedListWithKey(key=len)
        self._index_fuzzy = SortedListWithKey(key=len)
        self.match_functions = {self.match_exact: self._index_exact,
                                self.match_parse: self._index_parse,
                                self.match_fuzzy: self._index_fuzzy}
        self._catch_all_handlers = set()

    @property
    def handlers(self):
        return self._handlers.keys()

    def add_handler(self, name, handler):
        validate_handler(handler)
        if not any([handler.match_exact,
                    handler.match_parse,
                    handler.match_fuzzy]):
            raise ValueError('Expected one of exact, parse, fuzzy'
                             'to be True.')
        if handler.ignore_case:
            name = name.lower()
        if handler in self._handlers[name]:
            raise ValueError('Handler: {!r} already assigned to: {!r}'
                             ''.format(handler, name))
        self._handlers[name].add(handler)
        if handler.match_exact:
            self._index_exact.add(name)
        elif handler.match_parse:
            self._index_parse.add(name)
        else:  # handler.match_fuzzy:
            self._index_fuzzy.add(name)
        if '*' in self._handlers:
            self._catch_all_handlers = self._handlers['*']

    def remove_handler(self, name, handler):
        self._handlers[name].remove(handler)
        if handler.match_exact:
            self._index_exact.remove(name)
        elif handler.match_parse:
            self._index_parse.remove(name)
        else:  # handler.match_fuzzy:
            self._index_fuzzy.remove(name)

    def match(self, frame):
        for match_function, index in self.match_functions.items():
            if not index:
                continue
            frame_, handlers = match_function(frame)
            if not handlers:
                continue
            return frame_, handlers
        else:
            if self._catch_all_handlers:
                return frame, self._catch_all_handlers
            return frame, set()

    def match_exact(self, frame):
        name = frame.name
        if name in self._index_exact:
            return frame, self._handlers[frame.name]
        if name.lower() in self._index_exact:
            handlers_ = self._handlers[name.lower()]
            return frame, {h for h in handlers_ if h.ignore_case is True}
        return frame, set()

    def match_parse(self, frame):
        for pattern in reversed(self._index_parse):
            if isinstance(frame.data.text, str):
                match_string = frame.data.text
            else:
                match_string = frame.name
            res = string_parse(
                format=pattern, string=match_string)
            if not res:
                continue
            handlers = self._handlers[pattern]
            data = frame.data
            data.update(**res.named)
            data.update({'args': res.fixed})
            frame.data = data
            return frame, handlers
        else:
            return frame, set()

    def match_fuzzy(self, frame):
        if not self._index_fuzzy:
            return frame, set()
        pattern = process.extractOne(
            frame.name, self._index_fuzzy,
            scorer=fuzz.token_sort_ratio)
        if not pattern or pattern[1] < MATCH_FUZZY_THRESHOLD:
            return frame, set()
        return frame, self._handlers[pattern[0]]


class Registry(object):
    def __init__(self, callback=None):
        self._registry = HandlerRegistry()
        if callback and not callable(callback):
            raise ValueError('Expected a callable for callback, got: {}'
                             ''.format(callback))
        self._trigger_frame_handler = callback

    @property
    def handlers(self):
        return self._registry.handlers

    def add_handler(self, name, handler):
        self._registry.add_handler(name, handler)

    def remove_handler(self, name, handler):
        self._registry.remove_handler(name, handler)

    def match(self, frame):
        """Returns (frame, {handlers})"""
        return self._registry.match(frame)

    @property
    def callback(self):
        return self._trigger_frame_handler

    @callback.setter
    def callback(self, callback):
        if callback and not callable(callback):
            raise ValueError('Expected a callable for callback, got: {}'
                             ''.format(callback))
        self._trigger_frame_handler = callback
