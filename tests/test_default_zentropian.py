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

    class DummyClient(Zentropian):
        def __init__(self, name=None):
            super().__init__(name=name)

        @on_event('*** started')
        def on_test(self, event):
            emitted_event = self.emit('test-event', space='test-space')

    server = DummyServer(name='dummy-server')
    server.inspect_handlers()
    server.bind('inmemory://test_1')
    server.join('test-space')

    client1 = DummyClient(name='dummy-client')
    client1.inspect_handlers()  # todo: move to Zentropian.init
    client1.connect('inmemory://test_1')
    client1.join('test-space')

    client1.emit('*** started', internal=True)
