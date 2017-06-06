# coding=utf-8
import datetime
from pprint import pprint
from string import punctuation

import os
import random
import re
import yaml
from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine
from chronyk import chronyk
from dateparser import parse
from zentropi import Agent, Frame, KINDS, on_event, on_message
from zentropi.handlers import Handler, HandlerRegistry
from zentropi.utils import StopAgent, run_agents_forever

Intent = IntentBuilder

def get_synsets(phrases):
    from nltk.corpus import wordnet

    for phrase in phrases:
        for synset in wordnet.synsets(phrase):
            for lemma in synset.lemmas():
                name = lemma.name()
                if '_' in name:
                    continue
                yield name


class Entity(object):
    def __init__(self, name, *phrases, regex: str = None, expand=0):
        self.name = name
        self.phrases = list(phrases)
        self.regex = regex
        if not phrases and not regex:
            self.phrases = [name]
        if expand:
            synsets = get_synsets(self.phrases[:3])
            self.phrases += synsets
            words = [w for w in self.phrases if ' ' not in w]
            normalized = set()
            for phrase in self.phrases:
                normalized.add(phrase)
            self.phrases = normalized

    def __repr__(self):
        return 'Entity(name={!r}, regex={!r}, phrases={!r})'.format(self.name, self.regex, list(self.phrases)[:3])


def bootstrap_adapt(intents, entities):
    engine = IntentDeterminationEngine()
    for entity in entities:
        for phrase in entity.phrases:
            engine.register_entity(phrase, entity.name)
        if entity.regex:
            engine.register_regex_entity(entity.regex)
    for intent in intents:
        engine.register_intent_parser(intent.build())
    return engine


class AdaptAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self._intent_registry = HandlerRegistry()
        self.engine = None
        self.entities = set()
        self.intents = set()

    @on_event('*** started')
    def startup(self, event):
        for handler in self._intent_registry.handler_objects:
            for entity in handler._handler.entities:
                self.entities.add(entity)
            self.intents.add(handler._handler.intent)
        self.engine = bootstrap_adapt(self.intents, self.entities)

    @on_message('*')
    def process_all_messages(self, message):
        if not self.engine:
            return
        text = message.text
        if not text:
            return
        for intent in self.engine.determine_intent(text):
            if intent.get('confidence') > 0.7:
                frame = Frame(intent.get('intent_type'))
                frame, handlers = self._intent_registry.match_exact(frame)
                handler = list(handlers)[0]
                message.data.update(intent.items())
                return handler(message)

    def on_intent(self, intent, *entities):
        def wrapper(handler):
            name_ = intent.name
            handler.intent = intent
            handler.entities = entities or []
            handler_obj = Handler(name=name_, handler=handler, kind=KINDS.MESSAGE)
            self._intent_registry.add_handler(name_, handler_obj)
            return handler

        return wrapper


RESPONSES = {
    'greet': {
        '*': ['hey', 'hi', 'hello'],
        'morning': ['good morning!'],
        'afternoon': ['good afternoon!'],
        'evening': ['good evening!'],
        # 'night': ['good night'],
        # 'bye': ['see you', 'until later', 'bye'],
    },
    'smalltalk': {
        '*': ['wassup?', 'how is it going?', 'how can I help you?', ':)']
    }
}


class Response(object):
    def __init__(self):
        self._text = ''
        self._greet = False
        self._finalized = False
        self._sentences = 0

    @staticmethod
    def has_context(tag, context):
        return context in RESPONSES[tag]

    @staticmethod
    def one_of(tag, context='*'):
        return str(random.choice(RESPONSES[tag][context]))

    @property
    def text(self):
        # if not self._finalized:
        text_ = self._text.strip()
        if self._greet:
            if text_[-1] == ',':
                text_ = text_[:-1]
        else:
            if text_[-1] == ',':
                text_ = text_[:-1] + '.'
            elif text_[-1] not in punctuation:
                text_ = text_ + '.'
        return text_

    def greet(self, context=None):
        if self._greet:
            raise AssertionError('Already greeted.')
        tag = 'greet'
        if context and self.has_context(tag, context):
            greeting_ = self.one_of(tag, context)
        else:
            greeting_ = self.one_of(tag)
        if self._text:
            self._text = '{}, {}'.format(greeting_.capitalize(), self._text)
        else:
            self._text = '{}'.format(greeting_.capitalize())
        self._greet = True
        return self

    def say(self, text: str, punctuate=True):
        text = text.strip()
        if not text:
            return
        if not self._greet:
            text = text.capitalize()
        text_ = self._text
        if punctuate and text_ and text_[-1] not in punctuation:
            if self._greet and self._sentences == 0:
                if text[0] in [':', ';']:
                    self._text = '{} {}'.format(self._text, text)
                else:
                    self._text = '{}, {}'.format(self._text, text)
            else:
                self._text = '{}. {}'.format(self._text, text)
        else:
            self._text = '{} {}'.format(self._text, text)
        self._sentences += 1
        return self

    def random(self, tag, context):
        context = context or '*'
        return self.say(self.one_of(tag, context))

# ---- main ----

agent = AdaptAgent()


def parse_datetime(datetime_str: str, allow_future=True, allow_past=True):
    date_time = chronyk.Chronyk(datetime_str, allowfuture=allow_future, allowpast=allow_past)
    return date_time


@agent.on_intent(Intent('greeting_intent').require('greeting').optionally('greeting_mod').optionally('greeting_context'))
def greeting(message):
    response = Response()
    context = message.data.greeting_context
    return response.greet(context).text


@agent.on_intent(Intent('greeting_intent_1').optionally('greeting_mod').require('greeting_context'))
def greeting_1(message):
    response = Response()
    context = message.data.greeting_context
    return response.greet(context).text


@agent.on_intent(Intent('sunset').require('question_things').require('sunset') \
                 .optionally('day_modifier').optionally('day'))
def sunset(message):
    pprint(message.data)
    when_str = message.data.day or ''
    if message.data.day_modifier:
        when_str = message.data.day_modifier + ' ' + when_str
    when = parse(when_str)
    if not when:
        return str(agent.city.sun(date=datetime.datetime.now(), local=True)['sunset'])
    return str(agent.city.sun(date=when, local=True)['sunset'])


@agent.on_intent(Intent('weather_intent').require('question_things').require('weather').optionally('day'))
def weather(message):
    wtype = message.data.weather_type
    pprint(message.data)
    return 'Weather is nice...'


@agent.on_intent(Intent('about_intent').require('question_agents').require('subject'))
def generic_about_question(message):
    pprint(message.data)
    return 'About that...'


@agent.on_intent(Intent('reminder_intent').require('reminder_task'))
def set_reminder(message):
    pprint(message.data)
    match = re.search(r'[\d]+[dmhs]', message.text)
    if not match:
        return 'Include a time-delta: (number)(d/h/m/s)'
    time_delta_str = match.group()
    task = str.replace(message.text, time_delta_str, '')
    task = task.replace(message.data.reminder_task, '')
    task = task.strip()
    if not task:
        return 'You did not mention what to remind you about...'
    return 'I will try to remember... {}'.format(task)


def load_entities(file_path: str):
    with open(os.path.abspath(file_path)) as infile:
        entities_ = yaml.safe_load(infile.read())
    return [Entity(name, *words, expand=0) for name, words in entities_.items()]


for entity in load_entities('./entities.yml'):
    agent.entities.add(entity)

run_agents_forever(agent, shell=True)
