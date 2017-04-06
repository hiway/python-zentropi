# coding=utf-8
from typing import Any
from typing import Optional


class Field(object):
    """
    A Field allows us to store data with extra information associated with it.

    Example:
        >>> from zentropi import Field
        >>> test_field = Field(42, name='the_answer')
        >>> test_field.default
        42
        >>> test_field.value
        42
        >>> test_field.name
        'the_answer'
        >>> test_field.kind
        'Field'
        >>> test_field.describe()
        {'kind': 'Field', 'name': 'the_answer', 'value': 42}
    """
    __slots__ = ['_default', '_value', '_name', '_meta']

    def __init__(self,
                 default: Optional[Any] = None,
                 *,
                 name: Optional[str] = None) -> None:
        self._default = self.clean_and_validate(default)
        self._value = self._default
        self._name = name or str(id(self))
        self._meta = ['kind', 'name', 'value']

    @property
    def default(self):
        return self._default

    @property
    def kind(self) -> str:
        return self.__class__.__name__

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        if not name or not isinstance(name, str):
            raise ValueError('Expected non-empty string for name, '
                             'got: {!r}'.format(name))
        self._name = name

    @property
    def value(self) -> Any:
        if self._value is None:
            return self._default
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value = self.clean_and_validate(value)

    def clean_and_validate(self, value: Any):
        value_ = self.clean(value)
        try:
            if self.validate(value_):
                return value_
            raise ValueError('Field: {} got invalid value: {!r}.'.format(self._name, value))
        except Exception as e:
            raise e

    def clean(self, value: Any) -> Any:
        """Override: Convert types or clean up text; return cleaned value."""
        return value

    def validate(self, value: Any) -> bool:
        """Override: Return True if given value is valid,
        this should only accept cleaned values and return False if the
        value is not valid. Alternatively, raise an exception."""
        return True

    def describe(self) -> dict:
        return {k: getattr(self, k) for k in self._meta}
