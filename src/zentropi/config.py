# coding=utf-8
import json

import os
import yaml
from collections import UserDict
from cryptography.fernet import Fernet


class sources:
    DEFAULT = 0
    CONFIG = 1
    ENV = 2
    RUNTIME = 3

    ALL = [DEFAULT, CONFIG, ENV, RUNTIME]
    LABELS = ['DEFAULT', 'CONFIG', 'ENV', 'RUNTIME']

    @staticmethod
    def validate(source):
        if source not in sources.ALL:
            raise ValueError('Invalid value for source: {}. '
                             'Expected int in range: {}'
                             ''.format(source, sources.ALL))
        return source


class Option(object):
    def __init__(self, validator, *, default=None, optional=False, coerce=False,
                 config=True, env=False, secret=False,
                 source=None, name=None):
        self._name = name
        self._coerce = coerce
        self._validator = self.validate_validator(validator)
        self._default = self.validate(default) if default is not None else None
        self._value = self._default
        self._source = self.validate_source(source)
        self._optional = bool(optional)
        self._config = bool(config)
        self._env = bool(env)
        self._secret = bool(secret)

    def validate(self, value):
        try:
            if not self._coerce and not isinstance(value, self._validator):
                raise ValueError()
            return self._validator(value)
        except (ValueError, TypeError) as e:
            e.args += ('{} got invalid value: {}'
                       ''.format(self._name, repr(value)),)
            raise e

    @staticmethod
    def validate_validator(validator):
        if validator and callable(validator):
            return validator
        else:
            raise ValueError('validator must be callable, got: {}'
                             ''.format(repr(validator)))

    @staticmethod
    def validate_source(source):
        if not source:
            return sources.DEFAULT
        return sources.validate(source)

    @property
    def default(self):
        return self._default

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = self.validate(value)

    def set_value(self, value, source):
        self._value = self.validate(value)
        self._source = sources.validate(source)

    @property
    def source(self):
        return sources.LABELS[self._source]

    @property
    def optional(self):
        return self._optional

    @property
    def config(self):
        return self._config

    @property
    def env(self):
        return self._env

    @property
    def secret(self):
        return self._secret


class Config(UserDict):
    _strict = True
    _frozen = False
    _can_modify = False
    _can_extend = False
    _config_file = None
    _config_name = None
    # _key = Fernet.generate_key()

    # _auto_save = False

    def __init__(self, *, required=True):
        super().__init__()
        if self._config_name is None:
            self._config_name = type(self).__name__
        self._check_class_attributes()
        if self._config_file:
            self.load(self._config_file)
        self.load_env()
        if required:
            self._check_required_options_are_set()
        self._frozen = True

    def _check_class_attributes(self):
        for attr_name in self.__dir__():
            attr = getattr(self, attr_name)
            if attr_name.startswith('_') or callable(attr):
                continue
            setattr(self, attr_name, attr)

    def _check_required_options_are_set(self):
        for name, option in self.data.items():
            if option.optional:
                continue
            if option.value is None:
                hints = ''
                if option.env:
                    hints = '\nSince env=True, you can export environment variable in your shell.\n' \
                            'export {}="VALUE-GOES-HERE"'.format(name)
                raise ValueError('{}.{} is required (optional=False), got: {}.'
                                 '{}'.format(type(self).__name__, name, option.value, hints))

    # def _check_secrets(self):
    #     for name, option in self.data.items():
    #         if not option.secret:
    #             continue
    #         if option.value is not None:
    #             raise ValueError('{}.{} is secret (secret=True), do not pass a default value.'
    #                              ''.format(type(self).__name__, name))
    #         option.value = input('Config {}:'.format(name))

    def _get_option_name(self, key):
        return '{}.{}'.format(type(self).__name__, key)

    def _set_option_value(self, key, value, source):
        if key == 'data' or key.startswith('_'):
            # 'data' and _private attributes are stored as-given on self
            object.__setattr__(self, key, value)
            return
        elif key in self.data:
            if self._frozen and self._can_modify is False:
                raise PermissionError('Can not modify config with \'{}\': {} ({}._can_modify: {})'
                                      ''.format(key, repr(value), type(self).__name__, self._can_modify))
            option = self.data[key]
            option.set_value(value, source=source)
        elif isinstance(value, Option):
            value._name = self._get_option_name(key)
            option = value
        else:
            validator = type(value)
            option = Option(validator, default=value, source=source,
                            name=self._get_option_name(key))
        if self._frozen and self._can_extend is False:
            raise PermissionError('Can not extend config with option \'{}\': {} ({}._can_extend: {})'
                                  ''.format(key, repr(value), type(self).__name__, self._can_extend))
        # if option.secret:
        #     if isinstance(option.value, str) and option.value.startswith('secret:'):
        #         pass
        #         option.value = option.value[7:]
        self.data[key] = option

    def __getattribute__(self, item):
        if item == 'data' or item.startswith('_') or self._frozen is False:
            # 1. 'data' and _private attributes are stored as-given on self.
            # 2. self._frozen is False when init is not complete,
            #    return everything as-is during that short period.
            return object.__getattribute__(self, item)
        try:
            method_ = object.__getattribute__(self, item)
            if method_ and callable(method_):
                return method_
        except AttributeError:
            pass
        option = self.__dict__['data'].get(item, None)
        if self._frozen and not option and self._strict:
            raise AttributeError('No such option: {}'.format(item))
        if self._frozen and not option:
            # Not strict, return None for unknown options.
            return None
        return option.value

    def __setattr__(self, key, value):
        self._set_option_value(key, value, sources.RUNTIME)

    # def plain_value(self, option):
    #     if option.secret and option.value:
    #         cipher_suite = Fernet(self._key)
    #         # try:
    #         if isinstance(option.value, str) and option.value.startswith('secret:'):
    #             return cipher_suite.decrypt(str(option.value)[7:].encode('utf-8')).decode('utf-8')
    #             # except cryptography.fernet.InvalidToken:
    #             #     return option.value
    #     return option.value
    #
    # def encrypted_value(self, option):
    #     if option.secret and option.value:
    #         cipher_suite = Fernet(self._key)
    #         encrypted = 'secret:' + cipher_suite.encrypt(self.plain_value(option).encode('utf-8')).decode('utf-8')
    #         # print('original:', option.value)
    #         # print('encrypting:', self.plain_value(option))
    #         print('encrypted:', encrypted)
    #         return encrypted
    #     return option.value

    def filter_export(self, config=False, env=False):
        for name, option in self.data.items():
            # if option.X and X both are True for any X, we have a match
            if ((option.config and config) or
                    (option.env and env)):
                yield name, option.value

    def filter_import(self, data, config=False, env=False):
        for name, option in self.data.items():
            # if option.X and X both are True for any X, we have a match
            if ((option.config and config) or
                    (option.env and env)):
                value = data.get(name, None)
                if value is not None:
                    yield name, value

    def load(self, file=None, *, create=False, config_name=None):
        file = file or self._config_file
        if not file:
            raise AssertionError('Please set _config_file, or pass file as an argument.')
        config_name = config_name or self._config_name or 'config'
        data = None
        if isinstance(file, str):
            path = os.path.abspath(os.path.expanduser(file))
            if not os.path.exists(path):
                self.save(path, create=create, config_name=config_name)
            with open(path, 'r') as infile:
                try:
                    config = yaml.safe_load(infile)
                    data = config.get(config_name, {})
                except yaml.YAMLError as e:
                    print('Unable to load, expecting {!r} '
                          'to be a valid YAML file.'.format(path))
                    raise e
        else:
            config = yaml.safe_load(file)
            data = config.get(config_name, {})
        if not data:
            return
        for k, v in self.filter_import(data, config=True):
            self._set_option_value(k, v, sources.CONFIG)

    def save(self, file=None, *, create=False, config_name=None):
        file = file or self._config_file
        config_name = config_name or self._config_name or 'config'
        data = {config_name: {k: v for k, v in self.filter_export(config=True)}}
        if isinstance(file, str):
            path = os.path.abspath(os.path.expanduser(file))
            if create is True:
                dir_name = os.path.dirname(path)
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
            with open(path, 'w') as outfile:
                yaml.safe_dump(data, outfile)
            return
        yaml.safe_dump(data, file,
                       default_flow_style=False,
                       allow_unicode=True)

    def load_env(self):
        env_vars = [k for k, _ in self.filter_export(env=True)]
        for envar in env_vars:
            value = os.getenv(envar, None)
            if not value:
                continue
            if value.startswith('json:'):
                value = json.loads(value[5:])
            self._set_option_value(envar, value, sources.ENV)

    def export_env(self):
        for k, v in self.filter_export(env=True):
            if v is None or isinstance(v, (int, str, float, bool)):
                value = str(v) if v is not None else ''
            else:
                value = 'json:' + json.dumps(v).replace('"', '\\"')
            yield '{}="{}"'.format(k, value)
