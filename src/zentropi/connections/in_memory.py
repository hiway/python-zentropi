# coding=utf-8
from typing import List

from ..connections.connection import Connection
from ..frames import Command
from ..spaces import Spaces
from ..utils import validate_endpoint
from ..utils import validate_name
from ..zentropian import on_event


SPACES = {}  # type: dict


class InMemoryConnection(Connection):
    def __init__(self, name=None):
        super().__init__(name=name)
        self._spaces = None

    def _validate_connection(self, endpoint):
        if self._spaces:
            raise ConnectionError('Unable to connect as {} is already connected or bound to endpoint {!r}'
                                  ''.format(self.__class__.__name__, endpoint))

    def connect(self, endpoint: str, agent_name: str, frame_handler):
        global SPACES
        self.states.agent_name = validate_name(agent_name)
        self.states.endpoint = validate_endpoint(endpoint)
        if endpoint not in SPACES:
            raise ConnectionError('Expected another connection to have run {}.bind("{}") .'
                                  'No endpoint available to connect.'
                                  ''.format(self.__class__.__name__, endpoint))
        endpoint = self.states.endpoint
        self._validate_connection(endpoint)
        self._spaces = SPACES[endpoint]
        self._spaces.agent_connect(agent_name, self)
        self.states.connected = True

    def bind(self, endpoint: str, agent_name: str, frame_handler):
        global SPACES
        self.states.agent_name = validate_name(agent_name)
        self.states.endpoint = validate_endpoint(endpoint)
        endpoint = self.states.endpoint
        self._validate_connection(endpoint)
        if endpoint in SPACES:
            raise ConnectionError('Unable to bind to endpoint {!r} '
                                  'as bind() has been called already.'.format(endpoint))
        spaces = Spaces()
        SPACES[endpoint] = spaces
        self._spaces = spaces
        self._spaces.agent_connect(agent_name, self)
        self.states.connected = True

    def close(self):
        if not self._spaces:
            raise ConnectionError('Unable to close; not connected.')
        self._spaces.agent_close(self.states.agent_name)
        self._spaces = None
        self.states.connected = False

    def broadcast(self, frame):
        if not self._spaces:
            raise ConnectionError('Unable to broadcast; not connected.')
        self._spaces.broadcast(frame)
        return True

    def join(self, space: str):
        self._spaces._join(self.states.agent_name, space)
        # cmd = Command(name='join', space=space, source=self.name)
        # self.broadcast(cmd)

    def leave(self, space: str):
        cmd = Command(name='leave', space=space, source=self.states.agent_name)
        self.broadcast(cmd)

    def spaces(self) -> List[str]:
        return self._spaces.spaces()

    def agents(self, space=None) -> List[str]:
        return self._spaces.agents(space)

    def incoming_frame_handler(self, frame):


    @on_event('join')
    def on_join(self, command):
        pass

    @on_event('join-failed')
    def on_join_failed(self, command):  # todo: check event names <+^
        pass
