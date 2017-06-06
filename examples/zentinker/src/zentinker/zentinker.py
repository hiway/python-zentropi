# coding=utf-8
import asyncio
from tkinter import (
    Entry,
    Tk,
    Button, TclError)
from zentropi import (
    Agent,
    on_event,
    on_message,
    on_state,
    on_timer,
)


class ZenTinKer(Agent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.states.debug = True
        self._root = Tk()
        self._entry = Entry(self._root)
        self._entry.grid()
        self._button = Button(self._root, text='Ohai!', command=self.button_pressed).grid()

    async def run_tk(self, root, interval=0.05):
        """Run a tkinter app in an asyncio event loop."""
        try:
            print('*** starting tk loop')
            while True:
                root.update()
                await self.sleep(interval)
        except TclError as e:
            if "application has been destroyed" not in e.args[0]:
                raise e

    def button_pressed(self, *args, **kwargs):
        print('button pressed')

    @on_event('*** start')
    def startup(self, event):
        self.spawn(self.run_tk(self._root))
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
