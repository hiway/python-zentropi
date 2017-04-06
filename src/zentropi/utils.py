# coding=utf-8


import gettext
import json
import locale as lib_locale
import logging
import os
import sys
import warnings
from typing import Any
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def log_to_stream(stream: Optional[Any] = None, *,
                  level: Optional[Any] = None) -> Any:
    """
    Send zentropi logs to stream, at logging.[DEBUG] level.
    Default: zentropi.defaults.LOG_LEVEL => logging.DEBUG

    Returns: handler instance.

    Example:
        >>> from zentropi.utils import log_to_stream
        >>> _ = log_to_stream()  # logs to sys.stdout

    Or

        >>> from zentropi.utils import log_to_stream
        >>> _ = log_to_stream(level=logging.WARNING)  # Only warning and higher
    """
    from zentropi.defaults import LOG_LEVEL
    global logger
    if not stream:
        stream = sys.stdout  # pragma: no cover
    handler = logging.StreamHandler(stream)
    handler.setLevel(level or LOG_LEVEL)
    formatter = logging.Formatter(
        '%(asctime)s %(threadName)-10s %(filename)10s:%(lineno)03d '
        '%(funcName)-10s %(levelname)-6s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler


def i18n_wrapper(locale: Optional[str] = None) -> Any:
    """
    Internationalize using gettext.

    Returns gettext for provided locale
    or default (zentropi.defaults.LOCALE).

    Example:
        >>> from zentropi.utils import i18n_wrapper
        >>> _ = i18n_wrapper()
        >>> print(_('Hello, world.'))
        Hello, world.
    """
    from . import BASE_PATH
    from .defaults import LOCALE
    locale = locale or lib_locale.getlocale()[0] or LOCALE
    locale_dir = os.path.join(BASE_PATH, 'locale')
    locale_file = os.path.join(locale_dir, '{}.mo'.format(locale))
    try:
        translation = gettext.GNUTranslations(open(locale_file, 'rb'))
    except IOError:
        warnings.warn('Translation file for {} not found at: {}. Using default.'
                      ''.format(locale, locale_file))
        translation = gettext.NullTranslations()  # type: ignore
    translation.install()
    return translation.gettext


def deflate_dict(frame_as_dict):
    return {k: v for k, v in frame_as_dict.items() if v}


def validate_handler(handler):
    from .handlers import Handler
    if handler is None:
        return None
    if isinstance(handler, Handler):
        return handler
    raise ValueError('Expected handler to an instance of Handler. '
                     'Got: {!r}'.format(handler))


def validate_name(name):
    if name is None:
        return None
    if not name or not isinstance(name, str) or len(name.strip()) == 0:
        raise ValueError('Expected name to be a non-empty string. '
                         'Got: {!r}'.format(name))
    if len(name) > 128:
        raise ValueError('Expected name to be <= 128 unicode characters long. '
                         'Got: {} characters'.format(len(name)))
    return name


def validate_kind(kind):
    from .symbols import Kind
    if kind is None:
        return Kind.unset
    if isinstance(kind, int):
        return Kind(kind)
    if kind not in Kind:
        raise ValueError('Expected kind to be one of zentropi.symbols.Kinds: {!r}. '
                         'Got: {!r}'.format(', '.join([str(k) for k in Kind]), kind))
    return kind


def validate_data(data):
    from .frames import FrameData
    if data is None:
        return FrameData()  # type: ignore
    assert isinstance(data, (dict, FrameData)), data
    if isinstance(data, FrameData):
        data = data.data
    assert len(json.dumps(data)) < 1024 * 10
    return FrameData(data)  # type: ignore


def validate_meta(meta: dict = None) -> dict:
    if meta is None:
        return {}
    assert isinstance(meta, dict)
    assert len(json.dumps(meta)) < 512
    return meta


def validate_id(id: str = None) -> Optional[str]:
    if id is None:
        return None
    assert isinstance(id, str)
    return id
