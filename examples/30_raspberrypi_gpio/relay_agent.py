# coding=utf-8
from zentropi import (
    Agent,
    on_event,
    on_message,
    on_state
)


class Relay(Agent):
    @on_event('*** started')
    def setup(self, event):
        # Define custom states.
        self.states.power = False

    @on_message('switch {power}', parse=True)
    def switch(self, message):
        power = message.data.power.lower().strip()  # Clean input
        if power in ['on', 'up']:
            self.states.power = True  # Will trigger @on_state('power')
        elif power in ['off', 'down']:
            self.states.power = False  # Will trigger @on_state('power')
        else:
            return 'I did not understand {!r}; try "switch [on|off]".'.format(power)
        return 'Switching power {}'.format(power)  # Send reply.

    @on_state('power')
    def on_test_state(self, state):
        print('Change GPIO value to', state.data.value)
        return True  # Accept state change


if __name__ == '__main__':
    agent = Relay('Relay')
    agent.connect('redis://localhost:6379')
    agent.join('telegram')
    agent.run()
