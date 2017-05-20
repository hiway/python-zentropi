# coding=utf-8

from collections import defaultdict
from inspect import iscoroutinefunction
from typing import Optional, Union

from ..agent import Agent
from ..zentropian import Zentropian
from .connection import Connection
from .in_memory import InMemoryConnection


def build_connection_instance(endpoint: str, connection_class: Connection, agent: Zentropian):
    if connection_class and not isinstance(connection_class, Connection):
        raise ValueError('Expected connection_class to subclass zentropi.Connection. '
                         'Got: {!r}'.format(connection_class))
    if isinstance(connection_class, Connection):
        return connection_class(agent=agent)  # type: ignore
    if endpoint.startswith('inmemory://'):
        return InMemoryConnection(agent=agent)
    elif endpoint.startswith('redis://'):
        from .redis_connection import RedisConnection
        return RedisConnection(agent=agent)
    else:
        raise ValueError('Expected endpoint to be in {!r}. Got: {!r}.'
                         ''.format(['inmemory://'], endpoint))  # todo: generic list


class ConnectionRegistry(object):
    def __init__(self, agent: Agent) -> None:
        self._agent = agent
        self._tags = defaultdict(set)  # type: dict
        self._endpoints = defaultdict(set)  # type: dict
        self._connections = set()  # type: set

    @property
    def connected(self):
        return len(self._connections) > 0

    @property
    def connections(self):
        return [c for c in self._connections]

    def connect(self, endpoint, *, auth=None, tag='default', connection_class=None):
        connection = build_connection_instance(endpoint, connection_class, self._agent)
        if iscoroutinefunction(connection.connect):
            self._agent.spawn(connection.connect(endpoint, auth=auth))
        else:
            connection.connect(endpoint, auth=auth)
        self._connections.add(connection)
        self._tags[tag].add(connection)
        self._endpoints[endpoint].add(connection)

    def bind(self, endpoint, *, tag='default', connection_class=None):
        connection = build_connection_instance(endpoint, connection_class, self._agent)
        if iscoroutinefunction(connection.bind):
            self._agent.spawn(connection.bind(endpoint))
        else:
            connection.bind(endpoint)
        self._connections.add(connection)
        self._tags[tag].add(connection)
        self._endpoints[endpoint].add(connection)

    def broadcast(self, frame, *, tags: Optional[Union[list, str]] = None):
        for connection in self.connections_by_tags(tags):
            # print('broadcasting on', connection, frame.name)
            if iscoroutinefunction(connection.broadcast):
                self._agent.spawn(connection.broadcast(frame))
            else:
                connection.broadcast(frame)

    def join(self, space: str, *, tags: Optional[Union[list, str]] = None):
        for connection in self.connections_by_tags(tags):
            if iscoroutinefunction(connection.join):
                self._agent.spawn(connection.join(space))
            else:
                connection.join(space)

    def leave(self, space: str, *, tags: Optional[Union[list, str]] = None):
        for connection in self.connections_by_tags(tags):
            if iscoroutinefunction(connection.leave):
                self._agent.spawn(connection.leave(space))
            else:
                connection.leave(space)

    def connections_by_tags(self, tags: Optional[Union[list, str]] = None):
        if isinstance(tags, str):
            if ',' in tags:
                tags = [t.strip() for t in tags.split(',') if t.strip()]
            else:
                tags = [tags]
        if not tags:
            tags = ['default']
        for tag in tags:
            if tag not in self._tags:
                raise KeyError('Tag {!r} not found in tags: {!r}'.format(tag, [t for t in self._tags]))
        for tag in tags:
            for connection in self._tags[tag]:
                yield connection

    def connections_by_endpoint(self, endpoint):
        if not endpoint:
            return self.connections
        return [c for c in self._endpoints[endpoint]]
