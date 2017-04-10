# coding=utf-8
from typing import List
from typing import Optional

from ..connections.connection import Connection
from ..spaces import Spaces
from ..utils import validate_endpoint
from ..zentropian import Zentropian


SPACES = {}  # type: dict


class InMemoryConnection(Connection):
    def __init__(self, agent: Zentropian) -> None:
        super().__init__()
        self._agent = agent
        self._endpoint = None  # type: Optional[str]
        self._spaces = None  # type: Optional[Spaces]

    def _validate_connection(self, endpoint):
        if self._spaces:
            raise ConnectionError('Unable to connect as {} is already connected or bound to endpoint {!r}'
                                  ''.format(self.__class__.__name__, endpoint))

    def connect(self, endpoint: str):   # type: ignore
        global SPACES
        agent_name = self._agent.name
        endpoint = validate_endpoint(endpoint)
        if endpoint not in SPACES:
            raise ConnectionError('Expected another connection to have run {}.bind("{}") .'
                                  'No endpoint available to connect.'
                                  ''.format(self.__class__.__name__, endpoint))
        self._validate_connection(endpoint)
        self._spaces = SPACES[endpoint]
        self._spaces.agent_connect(agent_name, self)   # type: ignore
        self._connected = True
        self._endpoint = endpoint
        print('*** connected', endpoint)

    def bind(self, endpoint: str):   # type: ignore
        global SPACES
        agent_name = self._agent.name
        endpoint = validate_endpoint(endpoint)
        self._validate_connection(endpoint)
        if endpoint in SPACES:
            raise ConnectionError('Unable to bind to endpoint {!r} '
                                  'as bind() has been called already.'.format(endpoint))
        spaces = Spaces()
        SPACES[endpoint] = spaces
        self._spaces = spaces
        self._spaces.agent_connect(agent_name, self)
        self._connected = True
        self._endpoint = endpoint
        print('*** bound', endpoint)

    def close(self):
        if not self._spaces:
            raise ConnectionError('Unable to close; not connected.')
        self._spaces.agent_close(self._agent.name)
        self._spaces = None
        self._connected = False
        print('*** closed')

    def broadcast(self, frame):
        self.validate_is_connected()
        self._spaces.broadcast(frame)
        print('*** broadcast', frame.name)
        return True

    def join(self, space: str):  # type: ignore
        self.validate_is_connected()
        self._spaces._join(self._agent.name, space)  # type: ignore
        # cmd = Command(name='join', space=space, source=self.name)
        # self.broadcast(cmd)
        print('*** join', space)

    # def leave(self, space: str):
    #     self._spaces._leave(self._agent.name, space)
    #     # cmd = Command(name='leave', space=space, source=self._agent.name)
    #     # self.broadcast(cmd)
    #     print('*** leave', space)

    def spaces(self) -> List[str]:
        self.validate_is_connected()
        return self._spaces.spaces()  # type: ignore

    def agents(self, space: Optional[str] = None) -> List[str]:
        self.validate_is_connected()
        return self._spaces.agents(space)  # type: ignore

    def send(self, frame, internal=False):
        if internal:
            self._agent.handle_frame(frame)
            print('*** send internal', frame.name)
        else:
            raise NotImplementedError()

    def validate_is_connected(self):
        if not self._spaces:
            raise AssertionError('Not connected or bound. Call connect() or bind() first.')
