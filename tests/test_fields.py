# coding=utf-8
import pytest
from typing import Any
from zentropi import Field


def test_field():
    field = Field(42, name='the_answer')
    assert field.default == 42
    assert field.value == 42
    assert field.name == 'the_answer'
    assert field.kind == 'Field'
    assert field.describe() == {'kind': 'Field', 'name': 'the_answer', 'value': 42}


def test_no_value_no_default():
    field = Field()
    assert field.default is None
    assert field.value is None
    assert field.name
    field.name = 'the_answer'
    field.value = 42
    assert field.default is None
    assert field.value is 42
    assert field.kind == 'Field'
    assert field.describe() == {'kind': 'Field', 'name': 'the_answer', 'value': 42}


@pytest.mark.xfail(raises=ValueError)
def test_invalid_name_empty():
    field = Field()
    field.name = '    '


@pytest.mark.xfail(raises=ValueError)
def test_invalid_name_int():
    field = Field()
    field.name = 42


@pytest.mark.xfail(raises=ValueError)
def test_invalid_value():
    class MyField(Field):
        def validate(self, value: Any):
            return isinstance(value, int)

    field = MyField(42)
    field.value = 'lol no'
