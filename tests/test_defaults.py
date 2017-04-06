# coding=utf-8
import logging

from zentropi import defaults


def test_defaults():
    assert defaults.LOCALE == 'en_US'
    assert defaults.LOG_LEVEL == logging.DEBUG
