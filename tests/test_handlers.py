# coding=utf-8
import pytest

from zentropi.frames import Event
from zentropi.handlers import Handler
from zentropi.handlers import HandlerRegistry
from zentropi.handlers import validate_handler
from zentropi.handlers import validate_kind
from zentropi.handlers import validate_name
from zentropi.symbols import KINDS


def dummy():
    assert True
    return True


async def dummy_async():  # pragma: no cover
    pass


def test_validate_handler():
    dummy_handler = Handler(kind=KINDS.UNSET,
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
    handler = Handler(KINDS.UNSET, handler='obviously not a callable', name='test')


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_handler_fails_on_invalid_meta():
    handler = Handler(KINDS.UNSET, handler=dummy, name='test', meta='nonsense')


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_handler_fails_on_both_parse_and_fuzzy():
    handler = Handler(KINDS.UNSET, handler=dummy, name='test',
                      fuzzy=True, parse=True)


def test_handler_set_parse():
    handler = Handler(KINDS.UNSET, handler=dummy, name='test', parse=True)


def test_handler_set_fuzzy():
    handler = Handler(KINDS.UNSET, handler=dummy, name='test', fuzzy=True)


def test_async_handler():
    handler = Handler(KINDS.UNSET, handler=dummy_async, name='test_async')
    assert handler.run_async is True


def test_handler():
    handler = Handler(KINDS.UNSET, handler=dummy, name='test', meta={'a': 'b'})
    assert handler() is True
    assert handler.name == 'test'
    assert handler.kind == KINDS.UNSET
    assert handler.meta == {'a': 'b'}
    assert handler.match_exact is True
    assert handler.match_parse is False
    assert handler.match_fuzzy is False
    assert handler.run_async is False


def test_handler_registry():
    handler = Handler(KINDS.EVENT, 'dummy', handler=dummy)
    registry = HandlerRegistry()
    registry.add_handler('test-event', handler)
    frame_, handlers_ = registry.match(frame=Event('test-event'))
    assert handlers_ == {handler}  # set
    frame_1, handlers_1 = registry.match(frame=Event('something else'))
    assert handlers_1 == set()


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_add_handler_fails_on_bad_match_values():
    handler = Handler(KINDS.EVENT, 'dummy', handler=dummy, exact=False)
    registry = HandlerRegistry()
    registry.add_handler('test-event', handler)


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_add_handler_fails_if_match_already_assigned():
    handler = Handler(KINDS.EVENT, 'dummy', handler=dummy)
    registry = HandlerRegistry()
    registry.add_handler('test-event', handler)
    registry.add_handler('test-event', handler)


def test_handler_registry_parse():
    handler = Handler(KINDS.EVENT, 'dummy', handler=dummy, parse=True)
    registry = HandlerRegistry()
    registry.add_handler('{what}-event', handler)
    registry.add_handler('not this event', handler)
    frame_, handlers_ = registry.match(frame=Event('test-event'))
    assert handlers_ == {handler}  # set
    frame_1, handlers_1 = registry.match(frame=Event('something else'))
    assert handlers_1 == set()
    frame_2, handlers_2 = registry.match(frame=Event('not this event'))
    assert handlers_2 == {handler}


def test_handler_registry_fuzzy():
    handler = Handler(KINDS.EVENT, 'dummy', handler=dummy, fuzzy=True)
    registry = HandlerRegistry()
    registry.add_handler('test-event', handler)
    frame_, handlers_ = registry.match(frame=Event('test event'))
    assert handlers_ == {handler}  # set
    frame_1, handlers_1 = registry.match(frame=Event('something else'))
    assert handlers_1 == set()


def test_registry_remove_handler():
    handler_exact = Handler(KINDS.EVENT, 'dummy', handler=dummy)
    handler_parse = Handler(KINDS.EVENT, 'dummy', handler=dummy, parse=True)
    handler_fuzzy = Handler(KINDS.EVENT, 'dummy', handler=dummy, fuzzy=True)
    registry = HandlerRegistry()
    # Exact
    registry.add_handler('test-event', handler_exact)
    assert handler_exact in registry._handlers['test-event']
    registry.remove_handler('test-event', handler_exact)
    assert handler_exact not in registry._handlers['test-event']
    # Parse
    registry.add_handler('test-event', handler_parse)
    assert handler_parse in registry._handlers['test-event']
    registry.remove_handler('test-event', handler_parse)
    assert handler_parse not in registry._handlers['test-event']
    # Fuzzy
    registry.add_handler('test-event', handler_fuzzy)
    assert handler_fuzzy in registry._handlers['test-event']
    registry.remove_handler('test-event', handler_fuzzy)
    assert handler_fuzzy not in registry._handlers['test-event']
