# coding=utf-8
import traceback

import os
from aiotg import Bot  # pip install aiotg
from zentropi import Agent  # pip install zentropi
from zentropi import on_event
from zentropi import on_message

TELEGRAM_BOT_NAME = os.getenv('TELEGRAM_BOT_NAME', 'ExampleBot')
TELEGRAM_BOT_API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN', None)
assert TELEGRAM_BOT_API_TOKEN


class SimpleTelegramAgent(Agent):
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
            sent_msg = self.message(text, data={
                'text': text,
                'message_id': message['message_id'],
                'chat_id': message['chat']['id'],
                'user_id': message['from']['id'],
                'username': message['from']['username'],
                'name': name,
            })
            print('>>>', text)
            self.sent_telegram_messages.update({sent_msg.id: message['chat']['id']})
        except Exception:
            print(traceback.format_exc())
            print(message.name, message.data)

    @on_message('*')
    async def telegram_message_reply(self, message):
        if message.reply_to not in self.sent_telegram_messages:
            return
        try:
            chat_id = self.sent_telegram_messages[message.reply_to]
            del self.sent_telegram_messages[message.reply_to]
            await self._bot.send_message(chat_id=chat_id, text=message.name)
            print('<<<', message.name)
        except Exception:
            print(traceback.format_exc())
            print(message.name, message.data)

    @on_event('*** started')
    def on_started(self, event):
        self.spawn(self._bot.loop())

    @on_event('*** stopped')
    def on_stopped(self, event):
        self._bot.stop()


if __name__ == '__main__':
    endpoint = 'redis://localhost:6379'
    agent = SimpleTelegramAgent('telegram')
    agent.connect(endpoint)
    agent.join('telegram')
    agent.run()
