# coding=utf-8
import asyncio
import sys
import os
import re
import uvloop

from prompt_toolkit import CommandLineInterface
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import create_prompt_application
from prompt_toolkit.shortcuts import create_asyncio_eventloop
from pygments.token import Token
from pytz import all_timezones_set
from zentropi import Agent
from zentropi import on_event

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

BASE_DIR = os.path.dirname(os.path.abspath(__name__))
PROMPT = '〉'
PROMPT_MORE = '  '
history = FileHistory(os.path.expanduser('~/.maya_history'))

ALL_TIMEZONES = all_timezones_set


def extract_urls(text):
    return re.findall(r'(https?://\S+)', text)


class Shell(Agent):
    def __init__(self):
        super().__init__()
        ptk_loop = create_asyncio_eventloop()
        self.loop = ptk_loop.loop
        self.cli = self._get_cli(ptk_loop)
        self._prompt = PROMPT
        self._prompt_more = PROMPT_MORE
        self._multi_line = False
        self._exit_on_next_kb_interrupt = False
        sys.stdout = self.cli.stdout_proxy(raw=True)

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
                self.emit(command, internal=True)
            except EOFError:
                break
            except KeyboardInterrupt:
                if self._exit_on_next_kb_interrupt:
                    break
                self._exit_on_next_kb_interrupt = True
                print('!')
                continue
        self.emit('shell-exiting', internal=True)
        print('')
        sys.exit(0)

    @on_event('*** started')
    async def on_started(self, event):
        print('started!')
        self.spawn(self.interact())

    @on_event('about')
    def on_about(self, event):
        print('An interactive-shell example.')

    @on_event('telegram-message')
    def on_about(self, event):
        print(event.data)

    @on_event('help {topic}', parse=True)
    def on_help(self, event):
        topic = event.data.topic
        print('Help for:', topic)


if __name__ == '__main__':
    endpoint = 'redis://localhost:6379'

    # server = Agent()
    shell = Shell()

    # server.bind('inmemory://shell-agent')
    # server.join('shell')
    # server.start(shell.loop)

    shell.connect(endpoint)
    shell.join('telegram')
    shell.run()
