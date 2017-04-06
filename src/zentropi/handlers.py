# coding=utf-8
from inspect import iscoroutinefunction

from .symbols import Kinds


def validate_handler(handler):
    if handler is None:
        return None
    if isinstance(handler, Handler):
        return handler
    raise ValueError('Expected handler to an instance of Handler. '
                     'Got: {!r}'.format(handler))


def validate_name(name):
    if not name or not isinstance(name, str) or len(name.strip()) == 0:
        raise ValueError('Expected name to be a non-empty string. '
                         'Got: {!r}'.format(name))
    if len(name) > 128:
        raise ValueError('Expected name to be <= 128 unicode characters long. '
                         'Got: {} characters'.format(len(name)))
    return name


def validate_kind(kind):
    if kind not in Kinds:
        raise ValueError('Expected kind (int) to be one of zentropi.symbols.Kinds: {!r}. '
                         'Got: {!r}'.format(', '.join([str(k) for k in Kinds]), kind))
    return kind


class Handler(object):
    __slots__ = [
        '_kind', '_name', '_handler',
        '_meta', '_async',
        '_match_exact', '_match_parse', '_match_fuzzy',
        '_length',
    ]

    def __init__(self, kind, name, handler, meta=None,
                 exact=True, parse=False, fuzzy=False):
        if callable(handler) and not iscoroutinefunction(handler):
            self._async = False
        elif iscoroutinefunction(handler):
            self._async = True
        else:
            raise ValueError('Expected handler to be a callable '
                             '(function, method) or a coroutine function. '
                             'Got: {!r}'.format(handler))
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
    def match_exact(self):
        return self._match_exact

    @property
    def match_parse(self):
        return self._match_parse

    @property
    def match_fuzzy(self):
        return self._match_fuzzy
