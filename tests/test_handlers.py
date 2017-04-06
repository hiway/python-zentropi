# coding=utf-8
import pytest

from zentropi.handlers import Handler
from zentropi.handlers import validate_handler
from zentropi.handlers import validate_name
from zentropi.handlers import validate_kind
from zentropi.symbols import Kinds


def dummy():
    assert True
    return True


async def dummy_async():  # pragma: no cover
    pass


def test_validate_handler():
    dummy_handler = Handler(kind=Kinds.unset,
                            name='test',
                            handler=dummy)

    validated_handler = validate_handler(dummy_handler)
    assert validated_handler == dummy_handler


def test_validate_empty_handler():
    assert validate_handler(None) is None


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_validate_handler_fails():
    validate_handler("fail!")


def test_validate_name():
    assert validate_name('a name') == 'a name'


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_validate_name_fails_on_int():
    validate_name(0)


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_validate_name_fails_too_long():
    validate_name('lol' * 100)


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_validate_kind_fails():
    validate_kind('this will not work')


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_handler_fails_on_invalid_handler():
    handler = Handler(Kinds.unset, handler='obviously not a callable', name='test')


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_handler_fails_on_invalid_meta():
    handler = Handler(Kinds.unset, handler=dummy, name='test', meta='nonsense')


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_handler_fails_on_both_parse_and_fuzzy():
    handler = Handler(Kinds.unset, handler=dummy, name='test',
                      fuzzy=True, parse=True)


def test_handler_set_parse():
    handler = Handler(Kinds.unset, handler=dummy, name='test', parse=True)


def test_handler_set_fuzzy():
    handler = Handler(Kinds.unset, handler=dummy, name='test', fuzzy=True)


def test_async_handler():
    handler = Handler(Kinds.unset, handler=dummy_async, name='test_async')
    assert handler.run_async is True


def test_handler():
    handler = Handler(Kinds.unset, handler=dummy, name='test', meta={'a': 'b'})
    assert handler() is True
    assert handler.name == 'test'
    assert handler.kind == Kinds.unset
    assert handler.meta == {'a': 'b'}
    assert handler.match_exact is True
    assert handler.match_parse is False
    assert handler.match_fuzzy is False
    assert handler.run_async is False
