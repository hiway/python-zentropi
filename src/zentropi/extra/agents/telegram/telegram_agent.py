# coding=utf-8
try:
    from aiotg import Bot
except ImportError:
    raise ImportError('Run `pip install aiotg`')

import os
import traceback

from zentropi import Agent, on_event, on_message
from zentropi.defaults import \
    FRAME_NAME_MAX_LENGTH

TELEGRAM_BOT_NAME = os.getenv('TELEGRAM_BOT_NAME', None)
TELEGRAM_BOT_API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN', None)
assert TELEGRAM_BOT_NAME, 'Missing ENV variable: export TELEGRAM_BOT_NAME="[your-bot-name]" '
assert TELEGRAM_BOT_API_TOKEN, 'Missing ENV variable: export TELEGRAM_BOT_API_TOKEN="[your-bot-api-token]" '


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
            name = text
            if len(name) > FRAME_NAME_MAX_LENGTH:
                name = name[:FRAME_NAME_MAX_LENGTH-1] + '…'
            full_name = '{} {}'.format(message['from']['first_name'], message['from']['last_name'])
            sent_msg = self.message(name, data={
                'text': text,
                'message_id': message['message_id'],
                'chat_id': message['chat']['id'],
                'user_id': message['from']['id'],
                'username': message['from']['username'],
                'full_name': full_name,
            })
            self.sent_telegram_messages.update({sent_msg.id: message['chat']['id']})
        except Exception:
            print(traceback.format_exc())
            print(message.name, message.data)

    @on_message('*')
    async def telegram_message_reply(self, message):
        if message.reply_to not in self.sent_telegram_messages:
            return
        text = message.data.text or message.name
        try:
            chat_id = self.sent_telegram_messages[message.reply_to]
            del self.sent_telegram_messages[message.reply_to]
            await self._bot.send_message(chat_id=chat_id, text=text)
            self.emit('telegram-reply-sent', data={'text': text, 'chat_id': chat_id})
        except Exception:
            print(traceback.format_exc())
            print(message.name, message.data)

    @on_event('*** started')
    def on_started(self, event):
        self.spawn(self._bot.loop())

    @on_event('*** stopping')
    def on_stopping(self, event):
        self._bot.stop()
