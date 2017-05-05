# coding=utf-8
import sys
import os

from prompt_toolkit import CommandLineInterface
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import create_prompt_application
from prompt_toolkit.shortcuts import create_asyncio_eventloop
from pygments.token import Token
from zentropi.defaults import FRAME_NAME_MAX_LENGTH

from .agent import (
    Agent,
    on_event,
    on_message
)
from .frames import (
    KINDS,
    Message
)

BASE_DIR = os.path.dirname(os.path.abspath(__name__))
PROMPT = '〉'
PROMPT_MORE = '  '
history = FileHistory(os.path.expanduser('~/.zentropi_history'))

FRAME_PREFIX = {
    KINDS.EVENT: '⚡ ︎',
    KINDS.MESSAGE: '✉ ',
    KINDS.STATE: '⇥ ',
    KINDS.COMMAND: '⎈ ',
    KINDS.REQUEST: '🔺 ',
    KINDS.RESPONSE: '🔻 ',
}


class ZentropiShell(Agent):
    def __init__(self, name=None):
        ptk_loop = create_asyncio_eventloop()
        self.loop = ptk_loop.loop
        self.cli = self._get_cli(ptk_loop)
        sys.stdout = self.cli.stdout_proxy(raw=True)
        super().__init__(name=name)
        self._prompt = PROMPT
        self._prompt_more = PROMPT_MORE
        self._multi_line = False
        self._exit_on_next_kb_interrupt = False

    def _get_cli(self, loop):
        global history
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
                self.emit('shell-ready', internal=True)
                user_input = await self.cli.run_async()
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
    def on_any_message(self, frame):
        if frame.source == self.name and frame.internal is True and not frame.name.startswith('***'):
            if 'text' in frame.data:
                text = frame.data.text.strip()
            else:
                text = frame.name
            self.message(text)
            return
        prefix = FRAME_PREFIX[frame.kind]
        if frame.data and frame.data.text != frame.name:
            print('{} @{}: {!r} {!r}'.format(prefix, frame.source, frame.name, frame.data))
        else:
            print('{} @{}: {}'.format(prefix, frame.source, frame.name))

    @on_event('join {space}', parse=True)
    def join_space(self, message):
        if message.source != self.name:
            return
        space = message.data.space.strip()
        self.join(space)

    @on_event('leave {space}', parse=True)
    def leave_space(self, message):
        if message.source != self.name:
            return
        space = message.data.space.strip()
        self.leave(space)
