# coding=utf-8
import os
import textwrap

from zentropi import (
    Agent,
    on_message,
    on_timer,
    run_agents
)
from zentropi.extra.telegram import TelegramAgent
from zentropi.extra.twitter import TwitterAgent

SECONDS = 1
MINUTES = SECONDS * 60
HOURS = MINUTES * 60
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', None)
assert TELEGRAM_CHAT_ID, 'Please export TELEGRAM_CHAT_ID="YOUR-CHAT-ID"'

HELP = """\
Usage: 
1. Schedule a tweet: bird add {tweet}
2. See scheduled tweets: bird list
3. Send next scheduled tweet immediately: bird next
4. Send a tweet immediately: bird send {tweet}
5. Remove a scheduled tweet: bird remove {index}
5.1 Remove upcoming tweet: bird remove next   
"""


def default_file_path():
    return os.path.join(os.path.dirname(__file__), 'tweets.txt')


class TweetinBird(Agent):
    def __init__(self, name=None, file_path=None):
        super().__init__(name=name)
        self.file_path = file_path or default_file_path()

    def get_tweets(self):
        try:
            with open(self.file_path, 'r') as in_file:
                tweets = in_file.readlines()
            return [t.strip() for t in tweets if t.strip()]
        except FileNotFoundError:
            raise AssertionError('File not found: {!r}'.format(self.file_path))

    def save_tweets(self, tweets):
        try:
            with open(self.file_path, 'w') as out_file:
                out_file.writelines([t.strip() + '\n' for t in tweets if t.strip()])
        except Exception as e:
            print('ERROR: ', e.args)
            raise AssertionError('Can not write to file: {!r}'.format(self.file_path))

    def remove_next_tweet_from_file(self):
        tweets = self.get_tweets()
        self.save_tweets(tweets[1:])

    def send_next_tweet(self):
        try:
            tweets = self.get_tweets()
        except AssertionError as e:
            return '; '.join(e.args)
        if not tweets:
            return 'No tweets to send!'
        next_tweet = tweets[0]
        self.emit('twitter-send-update', data={'text': next_tweet})
        self.remove_next_tweet_from_file()
        return 'Sending: {}'.format(next_tweet)

    def telegram_message(self, text):
        data = {text: text, 'session': TELEGRAM_CHAT_ID, }
        self.emit('send_telegram_message', data=data)

    @on_message('bird help', parse=True)
    def help(self, message):
        return textwrap.dedent(HELP).strip()

    @on_message('bird add {tweet}', parse=True)
    def add_tweet(self, message):
        tweet = message.data.tweet
        with open(self.file_path, 'a') as out_file:
            out_file.write(tweet)
        return 'Saved {!r}'.format(tweet)

    @on_message('bird list', parse=True)
    def list_tweets(self, message):
        try:
            tweets = self.get_tweets()
        except AssertionError as e:
            return '; '.join(e.args)
        if len(tweets) > 10:
            tweets = tweets[:10]
        return 'Scheduled next:\n' + '\n'.join(['{}: {}'.format(i + 1, t) for i, t in enumerate(tweets)])

    @on_message('bird next')
    def send_next_tweet_now(self, message):
        return self.send_next_tweet()

    @on_message('bird send {tweet}')
    def send_a_tweet_now(self, message):
        tweet = message.data.tweet
        self.emit('twitter-send-update', data={'text': tweet})
        return 'Sent: {}'.format(tweet)

    @on_message('bird remove {index}', parse=True)
    def remove_tweet_with_index(self, message):
        index = message.data.index
        if index.lower() == 'next':
            index = 1
        try:
            index = int(index) - 1
        except ValueError:
            return 'Error: Expected "next" or a number.'
        tweets = self.get_tweets()
        if not tweets:
            return 'No tweets are scheduled.'
        try:
            tweet = tweets[index]
            print('*** index', index)
            print('*** before', tweets)
            del tweets[index]
            print('*** after', tweets)
            self.save_tweets(tweets)
            return 'Removed {}: {!r}'.format(index, tweet)
        except IndexError:
            return 'Error: Expected 1 <= index <= {}'.format(len(tweets) + 1)
        except AssertionError as e:
            return '; '.join(e.args)

    @on_timer(3 * HOURS)
    def check_schedule(self):
        text = self.send_next_tweet()
        self.telegram_message(text)


if __name__ == '__main__':
    telegram = TelegramAgent('telegram')
    twitter = TwitterAgent('twitter')
    tweetin_bird = TweetinBird('tweetin_bird')
    run_agents(telegram, twitter, tweetin_bird, shell=True)
