# coding=utf-8
from zentropi import InMemoryConnection
from zentropi import Zentropian
from zentropi import on_event


def test_default_zentropian():
    class DummyServer(Zentropian):
        def __init__(self, name=None):
            super().__init__(name=name)

        @on_event('test-event')
        def on_test(self, event):
            assert event.name == 'test-event'
            print('server')

    class DummyClient(Zentropian):
        def __init__(self, name=None):
            super().__init__(name=name)

        @on_event('*** started')
        def on_test(self, event):
            self.emit('test-event')
            self.emit('test-event', space='test-space')
            print('client')

    server = DummyServer(name='dummy-server')
    server.bind('inmemory://test_1')
    server.join('test-space')

    client1 = DummyClient(name='dummy-client')
    client1.connect('inmemory://test_1')
    client1.join('test-space')

    client1.emit('*** started', internal=True)
    client1.close()
