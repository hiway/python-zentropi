# coding=utf-8
import logging

from io import StringIO

from zentropi.frames import FrameData
from zentropi.utils import i18n_wrapper
from zentropi.utils import log_to_stream
from zentropi.utils import logger
from zentropi.utils import validate_data


def test_log():
    stream = StringIO()
    handler = log_to_stream(stream=stream, level=logging.DEBUG)
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
