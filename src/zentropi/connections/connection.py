# coding=utf-8

from typing import List, Optional


class Connection(object):
    def __init__(self):
        self._connected = False
        self._endpoint = None

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def endpoint(self) -> Optional[str]:
        return self._endpoint

    def connect(self, endpoint: str, auth: Optional[str] = None) -> None:
        raise NotImplementedError()

    def bind(self, endpoint: str) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()

    def broadcast(self, frame) -> None:
        raise NotImplementedError()

    def join(self, space: str) -> None:
        raise NotImplementedError()

    def leave(self, space: str) -> None:
        raise NotImplementedError()

    def spaces(self) -> List[str]:
        raise NotImplementedError()

    def agents(self, space: str) -> List[str]:
        raise NotImplementedError()

    def describe(self, *, space: str, agent: Optional[str] = None) -> dict:
        raise NotImplementedError()
