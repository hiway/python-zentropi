# coding=utf-8
from typing import List
from typing import Optional

from ..zentropian import Zentropian


class Connection(Zentropian):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.states.connected = False
        self.states.endpoint = None

    @property
    def connected(self) -> bool:
        return self.states.connected

    @property
    def endpoint(self) -> Optional[str]:
        return self.states.endpoint

    def connect(self, endpoint: str, agent, frame_handler) -> None:
        raise NotImplementedError()

    def bind(self, endpoint: str, frame_handler, **kwargs) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()

    def broadcast(self, frame, space=None) -> bool:
        raise NotImplementedError()

    def join(self, space: str) -> bool:
        raise NotImplementedError()

    def leave(self, space: str) -> bool:
        raise NotImplementedError()

    def spaces(self) -> List[str]:
        raise NotImplementedError()

    def agents(self, space: str) -> List[str]:
        raise NotImplementedError()

    def describe(self, *, space: str, agent: Optional[str] = None) -> dict:
        raise NotImplementedError()
