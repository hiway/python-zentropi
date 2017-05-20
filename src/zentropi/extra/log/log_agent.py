# coding=utf-8
import os
import traceback

from zentropi import Agent, on_event, on_message


class LogAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.event_log_file = open('zentropi_events.log', 'a')
        self.message_log_file = open('zentropi_messages.log', 'a')

    @on_event('*** stopping')
    def on_stopping(self, event):
        self.event_log_file.close()
        self.message_log_file.close()

    @on_event('*')
    def on_any_event(self, event):
        if event.source == self.name:
            return  # skip own events
        self.event_log_file.write(event.as_json() + '\n')
        self.event_log_file.flush()

    @on_message('*')
    def on_any_message(self, message):
        if message.source == self.name:
            return  # skip own messages
        self.message_log_file.write(message.as_json() + '\n')
        self.message_log_file.flush()
