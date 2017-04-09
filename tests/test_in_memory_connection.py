# coding=utf-8
# import pytest
from zentropi import InMemoryConnection
from zentropi import Zentropian
from zentropi import on_event


# def test_in_memory_connection():
class DummyServer(Zentropian):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.connection = InMemoryConnection()
        self.connection.bind('inmemory://test', self.name, self._trigger_frame_handler)
        self.connection.join('test-space')

    @on_event('test-event')
    def on_test(self, event):
        assert event.name == 'test-event'


class DummyClient(Zentropian):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.connection = InMemoryConnection()
        self.connection.connect('inmemory://test', self.name, self._trigger_frame_handler)
        self.connection.join('test-space')

    @on_event('*** started')
    def on_test(self, event):
        emitted_event = self.emit('test-event', space='test-space')
        server.connection.broadcast(emitted_event)

server = DummyServer(name='dummy-server')
server.inspect_handlers()
client1 = DummyClient(name='dummy-client')
client1.inspect_handlers()
client1.emit('*** started')
