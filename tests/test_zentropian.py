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
