# coding=utf-8
import pytest

from zentropi.spaces import Space, Spaces


def test_space():
    space = Space('test-space')
    assert space.name == 'test-space'
    assert space.agents == set()
    space.join('test-agent')
    assert space.agents == {'test-agent'}
    space.leave('test-agent')
    assert space.agents == set()


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_space_fails_on_double_join():
    space = Space('test-space')
    space.join('test-agent')
    space.join('test-agent')


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_space_fails_on_double_leave():
    space = Space('test-space')
    space.join('test-agent')
    space.leave('test-agent')
    space.leave('test-agent')


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_space_fails_on_leave_without_join():
    space = Space('test-space')
    space.leave('test-agent')


def test_spaces():
    spaces = Spaces()
    assert spaces.agents() == []
    assert spaces.spaces() == []


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_spaces_agents_fails_on_invalid_space():
    spaces = Spaces()
    _ = spaces.agents('whoa')


def test_spaces_connect():
    agent_name = 'test-agent'
    spaces = Spaces()
    assert spaces.agents() == []
    spaces.agent_connect(agent_name, connection=None)
    assert spaces.agents() == [agent_name]


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_spaces_connect_fails_on_duplicate_name():
    agent_name = 'test-agent'
    spaces = Spaces()
    assert spaces.agents() == []
    spaces.agent_connect(agent_name, connection=None)
    assert spaces.agents() == [agent_name]
    spaces.agent_connect(agent_name, connection=None)


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_spaces_connect_fails_on_invalid_connection():
    agent_name = 'test-agent'
    spaces = Spaces()
    assert spaces.agents() == []
    spaces.agent_connect(agent_name, connection="lol wut")


def test_spaces_join():
    agent_name = 'test-agent'
    space_name = 'test-space'
    spaces = Spaces()
    assert spaces.agents() == []
    assert spaces.spaces() == []
    spaces.agent_connect(agent_name, connection=None)
    cmd = spaces.join(agent_name, space_name)
    assert cmd.name == 'join'
    assert cmd.data == {'space': space_name}
    assert spaces.agents() == [agent_name]
    assert spaces.agents(space_name) == [agent_name]
    assert spaces.spaces() == [space_name]
    cmd2 = spaces.join(agent_name, space_name + '2')
    assert cmd2.data == {'space': space_name + '2'}
    assert sorted(spaces.spaces()) == sorted([space_name, space_name + '2'])
    cmd3 = spaces.join(agent_name + '3', space_name)
    assert agent_name in spaces.agents(space_name)
    assert agent_name + '3' in spaces.agents(space_name)


def test_spaces_join_fails():
    agent_name = 'test-agent'
    space_name = 'test-space'
    spaces = Spaces()
    spaces.agent_connect(agent_name, connection=None)
    cmd = spaces.join(agent_name, space_name)
    assert cmd.name == 'join'
    cmd = spaces.join(agent_name, space_name)
    assert cmd.name == 'join-failed'
