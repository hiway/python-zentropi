# coding=utf-8
import aiohttp
import asyncio
import json
import os

from aiohttp.web_ws import MsgType
from zentropi import (Agent,
                      on_event)

# https://medium.com/@greut/a-slack-bot-with-pythons-3-5-asyncio-ad766d8b5d8f


class SlackAgent(Agent):
    def __init__(self, name=None):
        self.api_token = os.getenv('SLACK_BOT_API_KEY', None)
        if not self.api_token:
            raise ValueError('Please set "SLACK_BOT_API_KEY" in your shell environment (Add to ~/.bash_profile).')
        self.rtm = None
        self.ws = None
        super().__init__(name=name)

    async def api_call(self, method, data=None):
        """Slack API call."""
        with aiohttp.ClientSession() as session:
            form = aiohttp.FormData(data or {})
            form.add_field('token', self.api_token)
            async with session.post('https://slack.com/api/{0}'.format(method),
                                    data=form) as response:
                if response.status != 200:
                    raise ValueError('{0} with {1} failed.'.format(method, data))
            return await response.json()

    async def stream(self):
        rtm = await self.api_call("rtm.start")
        assert rtm['ok'], "Error connecting to RTM."
        self.rtm = rtm

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(rtm["url"]) as ws:
                self.ws = ws
                async for msg in ws:
                    if msg.tp != MsgType.text:
                        continue
                    slack_event = json.loads(msg.data)
                    slack_event_type = slack_event['type']
                    if slack_event_type in ['hello',
                                            'goodbye',
                                            'reconnect_url',
                                            'user_typing',
                                            'desktop_notification']:
                        print('Skipping', slack_event)
                        continue
                    elif slack_event_type in ['presence_change',
                                              'message']:
                        print('Emitting', slack_event)
                        self.emit('slack_{}'.format(slack_event_type), data=slack_event)
                        if slack_event_type == 'message':
                            self.message(name=slack_event['text'], data=slack_event)
                    else:
                        print('Unknown', slack_event)

    @on_event('*** started')
    def start_streaming(self, event):
        self.spawn(self.stream())


if __name__ == "__main__":
    agent = SlackAgent('slack')
    agent.connect('redis://localhost:6379')
    agent.join('slack')
    agent.run()
