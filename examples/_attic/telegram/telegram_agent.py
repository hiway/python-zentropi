# coding=utf-8
import signal

import time

from datetime import timedelta, datetime

try:
    from aiotg import Bot
except ImportError:
    raise ImportError('Run `pip install aiotg`')

import traceback

from zentropi import Agent, on_event, on_message, on_timer, Config, Option
from zentropi.defaults import FRAME_NAME_MAX_LENGTH


class TelegramConfig(Config):
    _can_extend = True
    _can_modify = True

    TELEGRAM_BOT_NAME = Option(str, env=True)
    TELEGRAM_BOT_OWNER = Option(str, env=True)
    TELEGRAM_BOT_PUBLIC = Option(bool, default=False, env=True)
    TELEGRAM_BOT_API_TOKEN = Option(str, env=True)
    TELEGRAM_BOT_API_TIMEOUT = Option(int, default=30, env=True)
    TELEGRAM_BOT_USE_MESSAGES = Option(bool, default=True, env=True)
    TELEGRAM_BOT_USE_EVENTS = Option(bool, default=True, env=True)


class TelegramAgent(Agent):
    def __init__(self, name=None, config=None):
        super().__init__(name=name)
        self.config = config or TelegramConfig()
        self._bot = Bot(api_token=self.config.TELEGRAM_BOT_API_TOKEN,
                        name=self.config.TELEGRAM_BOT_NAME,
                        api_timeout=self.config.TELEGRAM_BOT_API_TIMEOUT)
        self._bot.default(self.on_incoming_telegram_message)
        self.sent_telegram_messages = {}
        self.states.use_messages = self.config.TELEGRAM_BOT_USE_MESSAGES
        self.last_message_at = datetime.now()

    @on_timer(60)
    async def restart_bot(self):
        if self.last_message_at < (datetime.now() - timedelta(seconds=60)):
            return
        self._bot.stop()
        await self.sleep(1)
        self.spawn(self._bot.loop())

    def on_incoming_telegram_message(self, chat, message):
        self.last_message_at = datetime.now()
        try:
            username = message['from']['username']
            if not self.config.TELEGRAM_BOT_PUBLIC and username != self.config.TELEGRAM_BOT_OWNER:
                return
            text = message['text']
            name = text
            if len(name) > FRAME_NAME_MAX_LENGTH:
                name = name[:FRAME_NAME_MAX_LENGTH - 1] + '…'
            full_name = '{} {}'.format(message['from']['first_name'], message['from']['last_name'])
            data = {
                'text': text,
                'message_id': message['message_id'],
                'chat_id': message['chat']['id'],
                'user_id': message['from']['id'],
                'username': username,
                'full_name': full_name,
                'session': message['chat']['id'],
            }
            if self.config.TELEGRAM_BOT_USE_MESSAGES:
                sent_msg = self.message(name, data=data)
                self.sent_telegram_messages.update({sent_msg.id: message['chat']['id']})
            if self.config.TELEGRAM_BOT_USE_EVENTS:
                sent_event = self.emit('telegram-message', data=data)
                self.sent_telegram_messages.update({sent_event.id: message['chat']['id']})

        except Exception as e:
            traceback.print_exc()
            signal.alarm(1)

    @on_message('*', _use_messages=True)
    async def telegram_message_reply(self, message):
        if message.reply_to not in self.sent_telegram_messages:
            return
        text = message.data.text or message.name
        chat_id = self.sent_telegram_messages[message.reply_to]
        # del self.sent_telegram_messages[message.reply_to]
        await self._bot.send_message(chat_id=chat_id, text=text)
        self.emit('telegram_reply_sent', data={'text': text, 'chat_id': chat_id})

    @on_event('send_telegram_message')
    async def send_message(self, event):
        text = event.data.text
        chat_id = event.data.session or event.data.chat_id
        if not chat_id:
            self.emit('telegram_message_error', data={'text': 'session or chat_id expected.'})
            return
        ret_val = await self._bot.send_message(chat_id=chat_id, text=text)
        self.emit('telegram_message_sent', data={'text': text, 'chat_id': chat_id, 'return': ret_val})

    @on_event('*** started')
    def on_started(self, event):
        self.emit('telegram_connecting')
        self.spawn(self._bot.loop())

    @on_event('*** stopping')
    def on_stopping(self, event):
        self._bot.stop()
