# coding=utf-8
import pytest

from zentropi.connections import Connection


def test_connection():
    conn = Connection()
    assert conn.connected is False
    assert conn.endpoint is None


@pytest.mark.xfail(raises=NotImplementedError, strict=True)
def test_connection_connect():
    conn = Connection()
    conn.connect('dummy')


@pytest.mark.xfail(raises=NotImplementedError, strict=True)
def test_connection_bind():
    conn = Connection()
    conn.bind('dummy')


@pytest.mark.xfail(raises=NotImplementedError, strict=True)
def test_connection_close():
    conn = Connection()
    conn.close()


@pytest.mark.xfail(raises=NotImplementedError, strict=True)
def test_connection_broadcast():
    conn = Connection()
    conn.broadcast(None)


@pytest.mark.xfail(raises=NotImplementedError, strict=True)
def test_connection_join():
    conn = Connection()
    conn.join('test')


@pytest.mark.xfail(raises=NotImplementedError, strict=True)
def test_connection_leave():
    conn = Connection()
    conn.leave('test')


@pytest.mark.xfail(raises=NotImplementedError, strict=True)
def test_connection_spaces():
    conn = Connection()
    conn.spaces()


@pytest.mark.xfail(raises=NotImplementedError, strict=True)
def test_connection_agents():
    conn = Connection()
    conn.agents('test')


@pytest.mark.xfail(raises=NotImplementedError, strict=True)
def test_connection_describe():
    conn = Connection()
    conn.describe(space='test')
