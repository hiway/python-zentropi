# coding=utf-8
import shlex
import sys

import os
from prompt_toolkit import CommandLineInterface
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import (
    create_asyncio_eventloop,
    create_prompt_application
)
from pygments.token import Token
from zentropi import Agent, Kind, on_event, on_message, on_request, on_state

BASE_DIR = os.path.dirname(os.path.abspath(__name__))
PROMPT = '〉'
PROMPT_MORE = '  '
history = InMemoryHistory()

FRAME_PREFIX = {
    Kind.EVENT: '⚡ ︎',
    Kind.MESSAGE: '✉ ',
    Kind.STATE: '⇥ ',
    Kind.COMMAND: '⎈ ',
    Kind.REQUEST: '🔺 ',
    Kind.RESPONSE: '🔻 ',
}


class ZentropiShell(Agent):
    def __init__(self, name=None, **kwargs):
        ptk_loop = create_asyncio_eventloop()
        self.loop = ptk_loop.loop
        self.cli = self._get_cli(ptk_loop)
        sys.stdout = self.cli.stdout_proxy(raw=True)
        super().__init__(name=name, **kwargs)
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
        while True:
            try:
                user_input = await self.cli.run_async()
                command = user_input.text
                self._exit_on_next_kb_interrupt = False  # We have new input; relax.
                if command in ['exit', 'q']:
                    break
                if command:
                    await self.process_command(command)
            except EOFError:
                break
            except KeyboardInterrupt:  # User pressed Ctrl+C
                if self._exit_on_next_kb_interrupt:
                    # Second, immediate interrupt (can be reset by input on prompt).
                    break
                # First interrupt
                self._exit_on_next_kb_interrupt = True
                print('!')
                continue
        print('Stopping...', flush=True)
        self.stop()

    async def start(self, loop=None, **kwargs):
        await super().start(loop=loop, **kwargs)
        self._loop.create_task(self.interact())

    def parse_command(self, command):
        if ' ' not in command:
            return command, {}
        split_command = command.split(' ')
        name = split_command[0]
        data = {k: v
                for k, v in [x.split('=')
                             for x in shlex.split(' '.join(split_command[1:]))
                             if '=' in x]}
        return name, data

    async def process_command(self, command):
        if command.startswith('/'):
            event_name, data = self.parse_command(command[1:])
            await self.emit(event_name, **data)
        elif command.startswith('?'):
            try:
                command_name, data = self.parse_command(command[1:])
                print(await self.request(command_name, timeout=20, **data))
            except Exception as e:
                print('Error: ', e.args)
        elif command.startswith(':'):
            state_name, data = self.parse_command(command[1:])
            print(await self.state(state_name, **data))
        else:
            await self.message(command)

    @on_event('*', rate_limit=0)
    async def incoming_event(self, frame):
        await self.incoming_frame(frame)

    @on_message('*', rate_limit=0)
    async def incoming_message(self, frame):
        await self.incoming_frame(frame)

    @on_request('*', rate_limit=0)
    async def incoming_request(self, frame):
        await self.incoming_frame(frame)

    @on_state('*', if_show_states=True, rate_limit=0)
    async def incoming_state(self, frame):
        await self.incoming_frame(frame)

    async def incoming_frame(self, frame):
        text = frame.name
        if frame.data:
            print('{} {}\n\t{}'.format(FRAME_PREFIX[frame.kind], text, frame.data), flush=True)
        else:
            print('{} {}'.format(FRAME_PREFIX[frame.kind], text), flush=True)

