# coding=utf-8
from zentropi import (
    Agent,
    on_event,
    on_message,
    on_state,
    on_timer,
)


class Zenbrowser(Agent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.states.debug = True

    @on_event('*** start')
    def startup(self, event):
        print('!! {} is ready.'.format(self.name))

    @on_message('debug {debug_state:w}', parse=True)
    def set_debug(self, message):
        debug = message.data.debug_state.lower().strip()
        if debug in ['true', 'on', 'yes']:
            self.states.debug = True
        elif debug in ['false', 'off', 'no']:
            self.states.debug = False
        else:
            return 'Try "debug on" or "debug off", or just "debug" to check state.'
        return 'debug is {}'.format('on' if self.states.debug else 'off')

    @on_message('debug')
    def get_debug(self, message):
        return 'debug is {}'.format('on' if self.states.debug else 'off')

    @on_state('debug')
    def debug_changed(self, state):
        print('!! DEBUG is {}'.format(state.data.value))
        return True

    @on_message('zopen {url}', parse=True)
    def greet(self, message):
        url = message.data.url
        import os
        with open(os.path.expanduser('~/.qutefifo'), 'w') as fifo:
            fifo.write('open -t {}\n'.format(url))
        return 'sent to browser'
