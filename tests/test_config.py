# coding=utf-8
import os
from zentropi import Config
from zentropi.config import ConfigField
from zentropi.symbols import SOURCES


def test_config_import():
    from zentropi import Config as Config1
    from zentropi.config import Config as Config2
    assert Config1 is Config2


def test_config_subclass_plain_values():
    class TestConfig(Config):
        _can_modify = True

        test_1 = True
        test_2 = 0
        test_3 = 'ok'

    config = TestConfig()
    assert config.test_1 is True
    assert config.test_2 == 0
    assert config.test_3 == 'ok'
    config.test_3 = 'okhai'
    assert config.data['test_3'].value == 'okhai'


def test_config_subclass_config_fields():
    class TestConfig2(Config):
        TEST_CONFIG_INT = ConfigField(int, default=0, env=True, coerce=True)
        TEST_CONFIG_INT_2 = ConfigField(int, default=0, env=True)

    os.environ['TEST_CONFIG_INT'] = "1"
    os.environ['TEST_CONFIG_INT_2'] = "3"
    config = TestConfig2()
    assert config.TEST_CONFIG_INT == 1
    assert config.TEST_CONFIG_INT_2 == 3
    assert config.data['TEST_CONFIG_INT'].source == SOURCES.ENV


def test_config_file_save():
    class TestConfig3(Config):
        _config_file = 'test_config.conf'
        _can_modify = True

        TEST_CONFIG_INT = ConfigField(int, default=0)

    config = TestConfig3()
    assert config.TEST_CONFIG_INT == 0
    config.TEST_CONFIG_INT = 1
    config.save()

    config = TestConfig3()
    assert config.TEST_CONFIG_INT == 1
    os.remove(os.path.abspath(config._config_file))
