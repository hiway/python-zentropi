# coding=utf-8
import logging
from io import StringIO

from zentropi.frames import FrameData
from zentropi.utils import (
    i18n_wrapper,
    log_to_stream,
    validate_data
)


def test_log():
    stream = StringIO()
    logger = log_to_stream(stream=stream, level=logging.DEBUG)
    handler = logger.handlers[0]
    logger.warning('test')
    logger.info('test')
    logger.debug('test')
    logs = handler.stream.getvalue()
    handler.stream.close()
    assert 'WARNING' in logs
    assert 'INFO' in logs
    assert 'DEBUG' in logs


def test_i18n():
    _ = i18n_wrapper()
    assert callable(_)


def test_validate_data():
    data = FrameData({'a': 'b'})
    data_1 = validate_data(data)
    assert data == data_1
    data_2 = validate_data({'a': 'b'})
    assert data == data_2
