# coding=utf-8

try:
    import aiohttp
except ImportError:
    raise ImportError('Run `pip install aiohttp`')

import json
import os
import pprint

from aiohttp.web_ws import MsgType
from zentropi import (Agent,
                      on_event,
                      on_message)

from .event_types import EVENT_TYPES


class SlackAgent(Agent):
    def __init__(self, name=None):
        self.api_token = os.getenv('SLACK_BOT_API_KEY', None)
        if not self.api_token:
            raise ValueError('Set "SLACK_BOT_API_KEY" in your shell environment (Add to ~/.bash_profile).')
        super().__init__(name=name)
        self.rtm = None
        self.ws = None
        self._sent_messages = {}

    async def api_call(self, method, data=None):
        """
        Slack API call.
        
        https://medium.com/@greut/a-slack-bot-with-pythons-3-5-asyncio-ad766d8b5d8f
        """
        with aiohttp.ClientSession() as session:
            form = aiohttp.FormData(data or {})
            form.add_field('token', self.api_token)
            async with session.post('https://slack.com/api/{0}'.format(method),
                                    data=form) as response:
                if response.status != 200:
                    raise ValueError('{0} with {1} failed.'.format(method, data))
            return await response.json()

    async def slack_event_stream(self):
        rtm = await self.api_call('rtm.start')
        if 'ok' not in rtm:
            raise ConnectionError('Expected "ok" in Real Time Messaging API. Got: {!r}'.format(rtm))
        self.rtm = rtm

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(rtm["url"]) as ws:
                self.ws = ws
                async for msg in ws:
                    if msg.tp != MsgType.text:
                        continue
                    slack_event = json.loads(msg.data)
                    if 'type' not in slack_event:
                        # print('Skipping', slack_event)
                        continue
                    slack_event_type = slack_event['type']
                    if slack_event_type in EVENT_TYPES:
                        # print('Emitting', slack_event)
                        self.emit('slack_{}'.format(slack_event_type), data=slack_event)
                        if slack_event_type.startswith('message'):
                            msg = self.message(name=slack_event['text'], data=slack_event)
                            self._sent_messages.update({msg.id: msg.data})
                    else:
                        # print('Unknown', slack_event)
                        pass

    @on_event('*** started')
    def start_streaming(self, event):
        self.spawn(self.slack_event_stream())

    @on_message('*')
    async def send_valid_replies(self, message):
        if message.reply_to not in self._sent_messages:
            print('*** skipping reply', message.name, message.data)
            return
        data = self._sent_messages[message.reply_to]
        if 'text' in message.data:
            text = message.data['text']
        else:
            text = message.name
        self.ws.send_str(json.dumps(
            {
                'type': 'message',
                'channel': data['channel'],
                'text': text,
            }
        ))
        del self._sent_messages[message.reply_to]
