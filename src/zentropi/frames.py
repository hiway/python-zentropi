# coding=utf-8
import json
import time
from collections import UserDict
from typing import Optional
from typing import Union
from uuid import uuid4

from zentropi.utils import deflate_dict

from .symbols import Kind
from .utils import validate_data
from .utils import validate_id
from .utils import validate_kind
from .utils import validate_meta
from .utils import validate_name


class FrameData(UserDict):
    def __init__(self, *args, **kwargs):
        super(FrameData, self).__init__(*args, **kwargs)

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        return None

    def __setattr__(self, key, value):
        if key == 'data':
            self.__dict__[key] = value
        else:
            self.__dict__['data'][key] = value


class Frame(object):
    __slots__ = ['_id', '_name', '_data', '_meta', '_kind']

    def __init__(self,
                 name: str = None, *,
                 data: dict = None,
                 meta: dict = None,
                 kind=None,
                 id: str = None,
                 source: str = None,
                 target: str = None,
                 space: str = None,
                 reply_to: str = None,
                 timestamp: int = None) -> None:
        self._name = validate_name(name)
        self._data = validate_data(data)
        self._meta = validate_meta(meta)
        self._id = validate_id(id) or uuid4().hex
        self._kind = validate_kind(kind) or Kind.unset
        if source:
            self._meta.update({'source': validate_name(source)})
        if target:
            self._meta.update({'target': validate_name(target)})
        if space:
            self._meta.update({'space': validate_name(space)})
        if reply_to:
            self._meta.update({'reply_to': validate_name(reply_to)})
        if timestamp:
            self._meta.update({'timestamp': int(timestamp)})
        elif 'timestamp' not in self._meta:
            self._meta.update({'timestamp': int(time.time())})

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = validate_name(name)

    @property
    def data(self) -> Optional[dict]:
        return self._data or {}

    @data.setter
    def data(self, data: dict) -> None:
        self._data = validate_data(data)

    @property
    def meta(self) -> Optional[dict]:
        return self._meta

    @property
    def kind(self) -> Optional[int]:
        return self._kind

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def source(self) -> Optional[str]:
        return self._meta.get('source', None)

    @property
    def space(self) -> Optional[str]:
        return self._meta.get('space', None)

    @space.setter
    def space(self, space: str) -> None:
        self._meta['space'] = space

    @property
    def target(self) -> Optional[str]:
        return self._meta.get('target', None)

    @target.setter
    def target(self, agent: str) -> None:
        self._meta['target'] = agent

    @property
    def reply_to(self) -> Optional[str]:
        return self._meta.get('reply_to', None)

    @reply_to.setter
    def reply_to(self, agent: str) -> None:
        self._meta['reply_to'] = agent

    @property
    def timestamp(self) -> Optional[str]:
        return self._meta.get('timestamp', None)

    @staticmethod
    def build(name: str, *,
              data: dict = None,
              meta: dict = None,
              kind=None,
              id: str = None) -> Union['Frame', 'Command', 'Event']:
        if kind == Kind.command or kind == Kind.command.value:
            return Command(name, data=data, meta=meta, kind=kind, id=id)
        elif kind == Kind.event or kind == Kind.event.value:
            return Event(name, data=data, meta=meta, kind=kind, id=id)
        elif kind == Kind.message or kind == Kind.message.value:
            return Message(name, data=data, meta=meta, kind=kind, id=id)
        elif kind == Kind.request or kind == Kind.request.value:
            return Request(name, data=data, meta=meta, kind=kind, id=id)
        elif kind == Kind.response or kind == Kind.response.value:
            return Response(name, data=data, meta=meta, kind=kind, id=id)
        elif kind == Kind.state or kind == Kind.state.value:
            return State(name, data=data, meta=meta, kind=kind, id=id)
        else:
            return Frame(name, data=data, meta=meta, kind=kind, id=id)

    @staticmethod
    def from_dict(frame_as_dict):
        return Frame.build(**frame_as_dict)

    @staticmethod
    def from_json(frame_as_json):
        return Frame.build(**json.loads(frame_as_json))

    def as_dict(self) -> dict:
        return deflate_dict({
            'id': self.id,
            'name': self._name,
            'data': self._data.data,
            'meta': self._meta,
            'kind': self._kind.value,
        })

    def as_json(self) -> str:
        return json.dumps(self.as_dict())


class Command(Frame):
    __slots__ = ['_id', '_name', '_data', '_meta', '_kind']

    def __init__(self,
                 name: str = None, *,
                 data: dict = None,
                 meta: dict = None,
                 kind=None,
                 id: str = None,
                 source: str = None,
                 target: str = None,
                 space: str = None,
                 reply_to: str = None,
                 timestamp: int = None) -> None:
        super().__init__(name, data=data, meta=meta, kind=Kind.command, id=id,
                         source=source, target=target, space=space,
                         reply_to=reply_to, timestamp=timestamp)
        self._kind = Kind.command


class Event(Frame):
    __slots__ = ['_id', '_name', '_data', '_meta', '_kind']

    def __init__(self,
                 name: str = None, *,
                 data: dict = None,
                 meta: dict = None,
                 kind=None,
                 id: str = None,
                 source: str = None,
                 target: str = None,
                 space: str = None,
                 reply_to: str = None,
                 timestamp: int = None) -> None:
        super().__init__(name, data=data, meta=meta, kind=Kind.event, id=id,
                         source=source, target=target, space=space,
                         reply_to=reply_to, timestamp=timestamp)
        self._kind = Kind.event


class Message(Frame):
    __slots__ = ['_id', '_name', '_data', '_meta', '_kind']

    def __init__(self,
                 name: str = None, *,
                 data: dict = None,
                 meta: dict = None,
                 kind=None,
                 id: str = None,
                 source: str = None,
                 target: str = None,
                 space: str = None,
                 reply_to: str = None,
                 timestamp: int = None) -> None:
        super().__init__(name, data=data, meta=meta, kind=Kind.message, id=id,
                         source=source, target=target, space=space,
                         reply_to=reply_to, timestamp=timestamp)
        self._kind = Kind.message


class Request(Frame):
    __slots__ = ['_id', '_name', '_data', '_meta', '_kind']

    def __init__(self,
                 name: str = None, *,
                 data: dict = None,
                 meta: dict = None,
                 kind=None,
                 id: str = None,
                 source: str = None,
                 target: str = None,
                 space: str = None,
                 reply_to: str = None,
                 timestamp: int = None) -> None:
        super().__init__(name, data=data, meta=meta, kind=Kind.request, id=id,
                         source=source, target=target, space=space,
                         reply_to=reply_to, timestamp=timestamp)
        self._kind = Kind.request


class Response(Frame):
    __slots__ = ['_id', '_name', '_data', '_meta', '_kind']

    def __init__(self,
                 name: str = None, *,
                 data: dict = None,
                 meta: dict = None,
                 kind=None,
                 id: str = None,
                 source: str = None,
                 target: str = None,
                 space: str = None,
                 reply_to: str = None,
                 timestamp: int = None) -> None:
        super().__init__(name, data=data, meta=meta, kind=Kind.response, id=id,
                         source=source, target=target, space=space,
                         reply_to=reply_to, timestamp=timestamp)
        self._kind = Kind.response


class State(Frame):
    __slots__ = ['_id', '_name', '_data', '_meta', '_kind']

    def __init__(self,
                 name: str = None, *,
                 data: dict = None,
                 meta: dict = None,
                 kind=None,
                 id: str = None,
                 source: str = None,
                 target: str = None,
                 space: str = None,
                 reply_to: str = None,
                 timestamp: int = None) -> None:
        super().__init__(name, data=data, meta=meta, kind=Kind.state, id=id,
                         source=source, target=target, space=space,
                         reply_to=reply_to, timestamp=timestamp)
        self._kind = Kind.state
