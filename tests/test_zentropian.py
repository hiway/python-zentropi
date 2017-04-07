# coding=utf-8
import pytest

from zentropi import Zentropian


def test_zentropian():
    zen = Zentropian()
    zen.name = 'test'
    assert zen.name == 'test'
    zen.states.hello = 0

    @zen.on_state('hello')
    def on_hello(state):
        print('got: name: {} last: {} value: {}'
              ''.format(state.name, state.data.last, state.data.value))
        zen.emit('what is this')
        return True

    @zen.on_event('what is that', fuzzy=True)  # todo: '*'
    def on_test(event):
        print('Event: TEST!')

    zen.states['काय'] = '😉🙃👍'
    zen.states.hello = 2
    zen.states.hello = 'hello'
    zen.states.hello = 0x22


@pytest.mark.xfail(raises=NotImplementedError, strict=True)
def test_zentropian_fails_on_async():
    zen = Zentropian()

    @zen.on_event('failing')
    async def on_test(event):  # pragma: no cover
        pass

    zen.emit('failing')


def test_zentropian_sub_class():
    from zentropi import Zentropian
    from zentropi import on_event

    class Test(Zentropian):
        @on_event('test-event')
        def on_test(self, event):
            assert event.name == 'test-event'

    zen = Test()
    zen.inspect_handlers()
    zen.emit('test-event')


if __name__ == '__main__':
    test_zentropian_sub_class()
