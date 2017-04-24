# coding=utf-8
import sys
import os

from prompt_toolkit import CommandLineInterface
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import create_prompt_application
from prompt_toolkit.shortcuts import create_asyncio_eventloop
from pygments.token import Token
from zentropi import Agent
from zentropi import on_event
from zentropi import on_message

BASE_DIR = os.path.dirname(os.path.abspath(__name__))
PROMPT = '〉'
PROMPT_MORE = '  '
history = FileHistory(os.path.expanduser('~/.maya_history'))


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
                    self.message(command, internal=True)
            except EOFError:
                break
            except KeyboardInterrupt:
                if self._exit_on_next_kb_interrupt:
                    break
                self._exit_on_next_kb_interrupt = True
                print('!')
                continue
        self.emit('shell-exiting', internal=True)
        print('Stopping...', flush=True)
        self.close()
        self.stop()

    @on_event('*** started')
    async def on_started(self, event):
        self.spawn(self.interact())

    @on_message('*')
    def on_any_message(self, message):
        if message.source == self.name:
            return
        if message.data:
            print('@{}: {!r} {!r}'.format(message.source, message.name, message.data))
        else:
            print('@{}: {!r}'.format(message.source, message.name))

    @on_message('join {space}', parse=True)
    def join_space(self, message):
        space = message.data.space.strip()
        self.join(space)

    @on_message('leave {space}', parse=True)
    def leave_space(self, message):
        space = message.data.space.strip()
        self.leave(space)

    @on_message('.{text}', parse=True)
    def broadcast_message(self, message):
        text = message.data.text.strip()
        self.message(text)
