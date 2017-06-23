# coding=utf-8
import textwrap
import pprint
import sys

import os
from prompt_toolkit import CommandLineInterface
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.shortcuts import (
    create_asyncio_eventloop,
    create_prompt_application
)
from pygments.token import Token
from zentropi import Config
from zentropi.defaults import \
    FRAME_NAME_MAX_LENGTH

from .agent import Agent, on_event, on_message
from .frames import KINDS
from .fields import PersistentStore
from .utils import logger

BASE_DIR = os.path.dirname(os.path.abspath(__name__))
PROMPT = '〉'
PROMPT_MORE = '  '

FRAME_PREFIX = {
    KINDS.EVENT: '⚡ ︎',
    KINDS.MESSAGE: '✉ ',
    KINDS.STATE: '⇥ ',
    KINDS.COMMAND: '⎈ ',
    KINDS.REQUEST: '🔺 ',
    KINDS.RESPONSE: '🔻 ',
}


class ZentropiShellConfig(Config):
    _can_extend = True
    _can_modify = True
    _config_file = '~/.zentropi/shell.conf'

    HISTORY_FILE = '~/.zentropi/shell.history'
    ENABLE_HISTORY = False


class ZentropiShell(Agent):
    def __init__(self, name=None, config=None, **kwargs):
        self.config = config or ZentropiShellConfig()
        ptk_loop = create_asyncio_eventloop()
        self.loop = ptk_loop.loop
        self.cli = self._get_cli(ptk_loop)
        self.std_out = self.cli.stdout_proxy(raw=True)
        sys.stdout = self.std_out
        super().__init__(name=name, **kwargs)
        self._prompt = PROMPT
        self._prompt_more = PROMPT_MORE
        self._multi_line = False
        self._exit_on_next_kb_interrupt = False
        # self.store = PersistentStore('~/.zentropi/shell.db')
        self.states.events = True  # self.store.field(True)

    def _get_cli(self, loop):
        if self.config.ENABLE_HISTORY:
            history = FileHistory(os.path.expanduser(self.config.HISTORY_FILE))
        else:
            history = InMemoryHistory()
        return CommandLineInterface(
            application=create_prompt_application(
                multiline=Condition(lambda: self._multi_line),
                get_prompt_tokens=self._get_prompt,
                history=history,
                wrap_lines=True,
            ),
            eventloop=loop,
        )

    def _get_prompt(self, _):
        if self._multi_line:
            prompt = self._prompt_more
        else:
            prompt = self._prompt
        return [
            (Token.Prompt, prompt)
        ]

    @on_event('shell-prompt')
    def _on_prompt(self, event):
        self._prompt = event.data.get('prompt', self._prompt)
        self.cli.request_redraw()

    async def interact(self):
        self.emit('shell-starting', internal=True)
        while True:
            try:
                # self.emit('shell-ready', internal=True)
                user_input = await self.cli.run_async()
                if not hasattr(user_input, 'text'):
                    continue
                command = user_input.text
                self._exit_on_next_kb_interrupt = False  # We have new input; relax.
                if command in ['exit', 'q']:
                    break
                if command:
                    self.emit(command[:FRAME_NAME_MAX_LENGTH], data={'text': command}, internal=True)
            except EOFError:
                break
            except KeyboardInterrupt:
                if self._exit_on_next_kb_interrupt:
                    break
                self._exit_on_next_kb_interrupt = True
                print('!')
                continue
        self.emit('shell-stopping', internal=True)
        print('Stopping...', flush=True)
        self.stop()

    async def _run_forever(self):
        self.spawn(self.interact())
        await super()._run_forever()

    @on_message('*')
    @on_event('*')
    async def on_any_message(self, frame):
        if not self.states.events and frame.kind is KINDS.EVENT:
            return
        if frame.source == self.name and frame.internal is True and not frame.name.startswith('***'):
            if 'text' in frame.data:
                text = frame.data.text.strip()
            else:
                text = frame.name
            if text.startswith('/'):
                name = text[1:].strip()
                args = []
                kwargs = {}
                # logger.debug('prepare to emit event {}'.format(name))
                if ' ' in name:
                    # logger.debug('space in name')
                    name, *params = name.split(' ')
                    # logger.debug('name {}'.format(name))
                    # logger.debug('parameters {}'.format(params))
                    for token in params:
                        # logger.debug('token {}'.format(token))
                        if '=' in token:
                            # logger.debug('SPLIT')
                            k, v = token.split('=')
                            kwargs.update({k: v})
                        else:
                            args.append(token)
                    kwargs.update({'args': args})
                self.emit(name, data=kwargs)
            else:
                self.message(text)
            return
        elif frame.source == self.name and frame.internal is False:
            return
        prefix = FRAME_PREFIX[frame.kind]
        print('{} @{}: {}'.format(prefix, frame.source, frame.name))
        if frame.data and frame.data.text != frame.name:
            str_data = str(frame.data)
            if len(str_data) < 500:
                pprint.pprint(frame.data)
            else:
                print(textwrap.shorten(str_data, 80))

    @on_event('join {space}', parse=True)
    async def join_space(self, message):
        if message.source != self.name:
            return
        space = message.data.space.strip()
        self.join(space)

    @on_event('leave {space}', parse=True)
    async def leave_space(self, message):
        if message.source != self.name:
            return
        space = message.data.space.strip()
        self.leave(space)

    @on_event('shell events {events_state:w}', parse=True)
    def set_events(self, message):
        events_ = message.data.events_state.lower().strip()
        if events_ in ['true', 'on', 'yes']:
            self.states.events = True
        elif events_ in ['false', 'off', 'no']:
            self.states.events = False
        else:
            print('Try "events on" or "events off", or just "events" to check state.')

    @on_event('shell events')
    def get_events(self, message):
        response = 'Display events is {}'.format('on' if self.states.events else 'off')
        print(response)
