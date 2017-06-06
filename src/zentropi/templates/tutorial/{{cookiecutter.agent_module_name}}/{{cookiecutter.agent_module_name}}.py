# coding=utf-8
from zentropi import (
    Agent,
    on_event,
    on_message,
    on_state,
    on_timer,
    run_agents
)


class {{ cookiecutter.agent_class_name }}(Agent):
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

    @on_message('debug')
    def get_debug(self, message):
        response = 'debug is {}'.format('on' if self.states.debug else 'off')
        return response

    @on_state('debug')
    def debug_changed(self, state):
        print('!! DEBUG is {}'.format(state.data.value))
        return True

    @on_message('hello')
    def greet(self, message):
        return 'hello, world'

    @on_timer(3, state_debug=True)
    def heart_beat(self):
        print('❤️')


if __name__ == '__main__':
    {{cookiecutter.agent_module_name}} = {{cookiecutter.agent_class_name}}(name='{{cookiecutter.agent_name}}')
    run_agents({{cookiecutter.agent_module_name}}, shell=True)
