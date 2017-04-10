# coding=utf-8
from collections import defaultdict
from typing import Optional
from typing import Union

from ..zentropian import Zentropian
from .connection import Connection
from .in_memory import InMemoryConnection


def build_connection_instance(endpoint: str, connection_class: Connection, agent: Zentropian):
    if connection_class is None:
        return InMemoryConnection(agent=agent)
    elif not isinstance(connection_class, Connection):
        raise ValueError('Expected connection_class to subclass zentropi.Connection. '
                         'Got: {!r}'.format(connection_class))
    if endpoint.startswith('inmemory://'):
        return InMemoryConnection(agent=agent)
    else:
        raise ValueError('Expected endpoint to be in {!r}. Got: {!r}.'
                         ''.format(['inmemory://'], endpoint))  # todo: generic list


class ConnectionRegistry(object):
    def __init__(self, agent: Zentropian) -> None:
        self._agent = agent
        self._tags = defaultdict(set)  # type: dict
        self._connections = set()  # type: set

    @property
    def connected(self):
        return len(self._connections) > 0

    def connect(self, endpoint, *, tag='default', connection_class=None):
        connection = build_connection_instance(endpoint, connection_class, self._agent)
        connection.connect(endpoint)
        self._connections.add(connection)
        self._tags[tag].add(connection)

    def bind(self, endpoint, *, tag='default', connection_class=None):
        connection = build_connection_instance(endpoint, connection_class, self._agent)
        connection.bind(endpoint)
        self._connections.add(connection)
        self._tags[tag].add(connection)

    def broadcast(self, frame, *, tags: Optional[Union[list, str]] = None):
        for connection in self.connections_by_tags(tags):
            connection.broadcast(frame)

    def join(self, space: str, *, tags: Optional[Union[list, str]] = None):
        for connection in self.connections_by_tags(tags):
            connection.join(space)

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
