# coding=utf-8
import json
from typing import Any
from typing import Optional

import os
import yaml
from zentropi.fields import Field
from zentropi.states import States
from zentropi.symbols import SOURCES
from zentropi.utils import validate_source
from zentropi.utils import validate_validator


class ConfigField(Field):
    __slots__ = [
        '_default', '_value', '_name', '_meta', '_validator',
        '_coerce', '_source', '_optional', '_config', '_env',
        '_secret',
    ]

    def __init__(self,
                 validator,
                 *,
                 default: Optional[Any] = None,
                 name: Optional[str] = None,
                 coerce: bool = False,
                 optional: bool = False,
                 config: bool = True,
                 env: bool = False,
                 secret: bool = False,
                 source: int = SOURCES.DEFAULT) -> None:
        self._coerce = coerce
        self._validator = validate_validator(validator)
        self._default = self.clean_and_validate(default) if default is not None else None
        self._value = self._default
        self._source = validate_source(source)
        self._optional = bool(optional)
        self._config = bool(config)
        self._env = bool(env)
        self._secret = bool(secret)
        super().__init__(default=default, name=name)

    def clean(self, value: Any):
        return self._validator(value)

    def validate(self, value):
        try:
            self._validator(value)
            return True
        except:
            return False

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = validate_source(source)

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


class Config(States):
    _frozen = False
    _can_modify = False
    _can_extend = False
    _config_file = None

    def __init__(self, callback=None, required=True):
        super().__init__(callback=callback)
        self._add_class_attributes()
        if self._config_file:
            self.load(self._config_file)
        self.load_env()
        if required:
            self._check_required_options_are_set()
            self._frozen = True

    @property
    def config_file(self):
        return self._config_file

    def _add_class_attributes(self):
        for attr_name in self.__dir__():
            attr = object.__getattribute__(self, attr_name)
            if callable(attr) or attr_name.startswith('_'):
                continue
            if attr_name in ['data', 'config_file', 'callback']:
                continue
            setattr(self, attr_name, attr)

    def _check_required_options_are_set(self):
        for name, option in self.data.items():
            if option.optional:
                continue
            if option.value is None:
                raise ValueError('{}.{} is required (optional: False), got: {}'
                                 ''.format(self.__class__.__name__,
                                           name, option.value))

    def _add_state(self, name, default_or_config):
        if self._frozen and self._can_extend is False:
            raise PermissionError('Config is frozen and _can_extend is False, '
                                  'can not add field: {}'.format(name))
        if isinstance(default_or_config, ConfigField):
            config = default_or_config
        else:
            validator = type(default_or_config)
            config = ConfigField(validator=validator,
                                 default=default_or_config,
                                 name=name)
        super()._add_state(name, config)

    def _update_state(self, name, value):
        if self._frozen and self._can_modify is False:
            raise PermissionError('Config is frozen and _can_modify is False,'
                                  'can not update field: {}'.format(name))
        super()._update_state(name=name, value=value)

    def set_value_with_source(self, name, value, source):
        setattr(self, name, value)
        self.data[name].source = source

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

    def load(self, file=None, *, create=False):
        file = file or self._config_file
        data = None
        if isinstance(file, str):
            path = os.path.abspath(os.path.expanduser(file))
            if not os.path.exists(path):
                self.save(path, create=create)
            with open(path, 'r') as infile:
                try:
                    data = yaml.safe_load(infile)
                except yaml.YAMLError as e:
                    e.args += ('Unable to load, expected "{}" '
                               'to be a valid YAML file.'.format(path),)
                    raise e
        else:
            try:
                data = yaml.safe_load(file)
            except yaml.YAMLError as e:
                e.args += ('Unable to load, expected {!r} '
                           'to be a valid YAML file.'.format(file),)
                raise e
        if not data:
            return
        for k, v in self.filter_import(data, config=True):
            self.set_value_with_source(k, v, SOURCES.CONFIG)

    def save(self, file=None, *, create=False):
        file = file or self._config_file
        data = {k: v for k, v in self.filter_export(config=True)}
        if isinstance(file, str):
            path = os.path.abspath(os.path.expanduser(file))
            if create is True:
                dir_name = os.path.dirname(path)
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
            with open(path, 'w') as outfile:
                yaml.dump(data, outfile)
            return
        yaml.dump(data, file,
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
            self.set_value_with_source(envar, value, SOURCES.ENV)

    def export_env(self):
        for k, v in self.filter_export(env=True):
            if v is None or isinstance(v, (int, str, float, bool)):
                value = str(v) if v is not None else ''
            else:
                value = 'json:' + json.dumps(v).replace('"', '\\"')
            yield '{}="{}"'.format(k, value)
