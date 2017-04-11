# coding=utf-8
# import pytest
from zentropi import InMemoryConnection
from zentropi import Zentropian
from zentropi import on_event


# Test Connection() without ConnectionHandler()
def test_inmemory():
    class DummyServer(Zentropian):
        def __init__(self, name=None):
            super().__init__(name=name)
            self.connection = InMemoryConnection(self)
            self.connection.bind('inmemory://test')
            self.connection.join('test-space')

        @on_event('test-event')
        def on_test(self, event):
            assert event.name == 'test-event'

    class DummyClient(Zentropian):
        def __init__(self, name=None):
            super().__init__(name=name)
            self.connection = InMemoryConnection(self)
            self.connection.connect('inmemory://test')
            self.connection.join('test-space')

        @on_event('*** started')
        def on_test(self, event):
            emitted_event = self.emit('test-event', space='test-space')
            server.connection.send(emitted_event, internal=True)
            # self.connection.broadcast(emitted_event)

    server = DummyServer(name='dummy-server')
    client1 = DummyClient(name='dummy-client')
    client1.emit('*** started')
