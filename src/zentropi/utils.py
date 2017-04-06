# coding=utf-8


import gettext
import locale as lib_locale
import logging
import os
import sys
import warnings
from typing import Any
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
warnings.simplefilter('always')


def log_to_stream(stream: Optional[Any] = None, *,
                  level: Optional[Any] = None) -> Any:
    """
    Send zentropi logs to stream, at logging.[DEBUG] level.
    Default: zentropi.defaults.LOG_LEVEL => logging.DEBUG

    Returns: handler instance.

    Example:
        >>> from zentropi.utils import log_to_stream
        >>> log_to_stream()  # logs to sys.stdout

    Or

        >>> from zentropi.utils import log_to_stream
        >>> log_to_stream(level=logging.WARNING)  # Only warning and higher
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
        translation = gettext.NullTranslations()
    translation.install()
    return translation.gettext
