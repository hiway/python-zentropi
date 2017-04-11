# coding=utf-8
import traceback

import asyncio
import os
from aiotg import Bot  # pip install aiotg
from zentropi import Agent  # pip install zentropi
from zentropi import on_event

TELEGRAM_BOT_NAME = os.getenv('TELEGRAM_BOT_NAME', 'ExampleBot')
TELEGRAM_BOT_API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN', None)
assert TELEGRAM_BOT_API_TOKEN


class TelegramAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self._bot = Bot(api_token=TELEGRAM_BOT_API_TOKEN,
                        name=TELEGRAM_BOT_NAME,
                        api_timeout=10)
        self._bot.default(self.on_incoming_telegram_message)
        self.sent_telegram_messages = {}

    def on_incoming_telegram_message(self, chat, message):
        try:
            text = message['text']
            if len(text) > 128:
                text = text[:127] + '…'
            name = '{} {}'.format(message['from']['first_name'], message['from']['last_name'])
            sent_msg = self.emit('telegram-message', data={
                'text': text,
                'message_id': message['message_id'],
                'chat_id': message['chat']['id'],
                'user_id': message['from']['id'],
                'username': message['from']['username'],
                'name': name,
            })
            self.sent_telegram_messages.update({sent_msg.id: message['chat']['id']})
        except Exception:
            print(message)
            print(traceback.format_exc())
            self.emit('telegram-error', data={'traceback': traceback.format_exc()})

    @on_event('telegram-reply')
    async def on_telegram_reply(self, event):
        if event.reply_to not in self.sent_telegram_messages:
            return
        try:
            chat_id = self.sent_telegram_messages[event.reply_to]
            del self.sent_telegram_messages[event.reply_to]
            await self._bot.send_message(chat_id=chat_id, text=event.data.text)
        except Exception:
            self.emit('telegram-error', data={'traceback': traceback.format_exc()})

    @on_event('*** started')
    def on_started(self, event):
        self.emit('*** connecting')
        print('*** starting telegram bot')
        self.spawn(self._bot.loop())

    @on_event('*** stopped')
    def on_stopped(self, event):
        self.emit('*** stopping')
        self._bot.stop()


class MyBot(Agent):
    @on_event('telegram-message')
    def on_telegram_message(self, event):
        text = event.data.text
        user = event.data.username
        reply = 'Echo: @{} said {!r}'.format(user, text)
        print('@{}: {!r} => {!r}'.format(user, text, reply))
        self.emit('telegram-reply', data={'text': reply}, reply_to=event.id)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    endpoint = 'redis://localhost:6379'
    telegram = TelegramAgent('telegram')
    my_bot = MyBot('my_bot')

    telegram.connect(endpoint)
    my_bot.connect(endpoint)

    telegram.join('telegram')
    my_bot.join('telegram')

    telegram.start(loop)
    my_bot.start(loop)
    loop.run_forever()
