# coding=utf-8
# coding=utf-8
import json
import traceback

import jmespath
import os
import tweepy as tweepy
from zentropi import (
    Agent,
    on_event,
)

auth = tweepy.OAuthHandler(os.getenv('ZENTROPI_TWITTER_API_KEY'),
                           os.getenv('ZENTROPI_TWITTER_API_SECRET'))
auth.set_access_token(os.getenv('ZENTROPI_TWITTER_OAUTH_TOKEN'),
                      os.getenv('ZENTROPI_TWITTER_OAUTH_SECRET'))

# Construct the API instance
api = tweepy.API(auth)
agent = Agent()


class ZentropiStreamListener(tweepy.StreamListener):
    def __init__(self):
        super().__init__()

    def on_error(self, status_code):
        if status_code == 420:
            return False

    def on_data(self, data):
        try:
            frame = json.loads(data)
            screen_name = frame.get('user', {}).get('screen_name', None)
            text = frame.get('text', None)
            if screen_name and text:
                output = jmespath.search(
                    '{name:user.name, '
                    'text:text, '
                    'followers_count:user.followers_count, '
                    'statuses_count:user.statuses_count, '
                    'geo_enabled:user.geo_enabled, '
                    'contributors_enabled:user.contributors_enabled, '
                    'following:user.following, '
                    'friends_count:user.friends_count, '
                    'verified:user.verified, '
                    'statuses_count:user.statuses_count, '
                    'lang:user.lang, '
                    'location:user.location, '
                    'url:user.url, '
                    'protected:user.protected, '
                    'length:length(text), '
                    'description:user.description, '
                    'time_zone:user.time_zone, '
                    'utc_offset:user.utc_offset, '
                    'created_at:created_at, '
                    'source:source, '
                    'truncated:truncated, '
                    'in_reply_to_user_id:in_reply_to_user_id, '
                    'in_reply_to_status_id:in_reply_to_status_id, '
                    'id_str:id_str, '
                    'geo:geo, '
                    'coordinates:coordinates, '
                    'place:place, '
                    'username:user.screen_name}', frame)
                agent.emit('twitter-update', data=output)
        except:
            traceback.print_exc()
            print('... continuing')
        finally:
            return True


class TwitterAgent(Agent):
    @on_event('twitter-send-update')
    def send_update(self, event):
        status = event.data.text
        if status.strip():
            print('Sending Tweet: {}'.format(status))
            try:
                api.update_status(status)
            except ValueError:
                print('!!! ERROR: Have you set environment variables '
                      'for Twitter API keys?')

    @on_event('twitter-send-reply')
    def send_reply(self, event):
        status = event.data.get('text')
        print('Sending Reply: {}'.format(status))
        in_reply_to = event.data.get('in_reply_to', None)
        if status.strip():
            api.update_status(status, in_reply_to_status_id=in_reply_to)

    @on_event('*** started')
    def on_startup(self, event):
        self.stream = tweepy.Stream(auth=api.auth, listener=ZentropiStreamListener())
        self.stream.userstream(async=True, replies='all')

    @on_event('*** stopping')
    def on_shutdown(self, event):
        self.stream.disconnect()
