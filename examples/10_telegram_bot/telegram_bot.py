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
            sent_msg = self.emit('telegram-message', data={
                'text': text,
                'message_id': message['message_id'],
                'chat_id': message['chat']['id'],
                'user_id': message['from']['id'],
            })
            self.sent_telegram_messages.update({sent_msg.id: message['chat']['id']})
        except Exception:
            self.emit('telegram-error', data={'traceback': traceback.format_exc()})

    @on_event('telegram-reply')
    async def on_telegram_reply(self, event):
        if event.reply_to not in self.sent_telegram_messages:
            return
        try:
            chat_id = self.sent_telegram_messages[event.reply_to]
            await self._bot.send_message(chat_id=chat_id, text=event.data.text)
            del self.sent_telegram_messages[event.reply_to]
        except Exception:
            self.emit('telegram-error', data={'traceback': traceback.format_exc()})

    @on_event('*** started')
    def on_started(self, event):
        self.emit('*** connecting')
        self.spawn(self._bot.loop())

    @on_event('*** stopped')
    def on_stopped(self, event):
        self.emit('*** stopping')
        self._bot.stop()


class MyBot(Agent):
    @on_event('telegram-message')
    def on_telegram_message(self, event):
        reply = 'Echo: {!r}'.format(event.data.text)
        print(reply)
        self.emit('telegram-reply', data={'text': reply}, reply_to=event.id)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    server = Agent()
    server.bind('inmemory://telegram-bot')
    server.join('telegram')
    server.start(loop)

    telegram = TelegramAgent()
    telegram.connect('inmemory://telegram-bot')
    telegram.join('telegram')
    telegram.start(loop)

    my_bot = MyBot()
    my_bot.connect('inmemory://telegram-bot')
    my_bot.join('telegram')
    my_bot.start(loop)

    loop.run_forever()
