# coding=utf-8
import atexit
import json
import traceback
from asyncio import Queue, QueueFull
from pprint import pprint

import jmespath
import tweepy
from zentropi import (
    Agent,
    Config,
    KINDS,
    Option,
    log_to_stream,
    on_event,
    on_message,
    on_timer)
from zentropi.handlers import Handler

logger = log_to_stream(enable=True)

UPDATE_FORMAT = ('{name:user.name, '
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
                 'username:user.screen_name}')


class ZenTweepyStreamListener(tweepy.StreamListener):
    def __init__(self, *args, update_queue=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(update_queue, Queue):
            raise ValueError('Expected asyncio.Queue() in `status_queue`, '
                             'got: {!r}'.format(update_queue))
        self.update_queue = update_queue

    def on_error(self, status_code):
        logger.debug('Twitter stream error code: {}'.format(status_code))
        if status_code == 420:
            return False

    def on_data(self, raw_data):
        try:
            update = json.loads(raw_data)
        except:
            logger.debug('Unable to load data {}'.format(raw_data))
            return False
        try:
            self.update_queue.put_nowait(update)
        except QueueFull:
            print('*** Agent not processing incoming updates fast enough.')
            print('*** Dropping: {}: {}'.format(update['id'], update.get('text') or update.get('event')))
        except Exception as e:
            traceback.print_exc()
            logger.debug('Continuing.')
        finally:
            return True


class ZenTweepyConfig(Config):
    _can_extend = True
    _can_modify = True
    _config_file = '~/.zentropi/zentweepy.conf'
    _config_name = 'Zentweepy'

    TWITTER_API_KEY = Option(str, config=True, env=True)
    TWITTER_API_SECRET = Option(str, config=True, env=True)
    TWITTER_OAUTH_TOKEN = Option(str, config=True, env=True, optional=True)
    TWITTER_OAUTH_SECRET = Option(str, config=True, env=True, optional=True)
    TWITTER_TIMEOUT = Option(int, default=60 * 10, config=True, env=True, optional=True)


class ZenTweepy(Agent):
    def __init__(self, name=None, config=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.config = config or ZenTweepyConfig()
        self.states.debug = True
        self.auth = auth = tweepy.OAuthHandler(self.config.TWITTER_API_KEY,
                                               self.config.TWITTER_API_SECRET)
        if self.config.TWITTER_OAUTH_TOKEN and self.config.TWITTER_OAUTH_SECRET:
            self.auth.set_access_token(self.config.TWITTER_OAUTH_TOKEN,
                                       self.config.TWITTER_OAUTH_SECRET)
            self.states.oauth_done = True
        else:
            self.states.oauth_done = False

        self.states.wait_for_verifier = False
        self.api = tweepy.API(self.auth)
        self.stream = None
        self.update_queue = Queue()
        self._watchdog_counter = 0
        self._watchdog_last_value = 0
        self._listener_task = None
        self.add_handler(Handler(KINDS.TIMER, str(self.config.TWITTER_TIMEOUT), self.watchdog))

    def feed_watchdog(self):
        self._watchdog_counter += 1

    def watchdog(self):
        if self.states.should_stop:
            return
        if not self.states.oauth_done:
            return
        if not self._watchdog_counter > self._watchdog_last_value:
            self.restart_tweepy_stream()
        self._watchdog_last_value = self._watchdog_counter

    async def update_queue_listener(self):
        await self.sleep(1)
        await self.send_whoami()
        while self.states.should_stop is False:
            update = await self.update_queue.get()
            self.feed_watchdog()
            screen_name = update.get('user', {}).get('screen_name', None)
            text = update.get('text', None)
            if not (screen_name or text):
                if 'event' in update:
                    event_name = update['event']
                    update_ = {k: v for k, v in update.items()}
                    del update_['event']
                    if 'target_object' in update_:
                        update_['target_object'] = update_ = jmespath.search(UPDATE_FORMAT, update_['target_object'])
                    self.emit('twitter_{}'.format(event_name), data=update_)
                else:
                    # self.emit('twitter_stream_raw', data=update)
                    pass
                continue
            if self.states.debug:
                print('@{}: {}'.format(screen_name, text))
            update_ = jmespath.search(UPDATE_FORMAT, update)
            self.emit('twitter_update', data=update_)

    def start_tweepy_stream(self):
        self.stream = tweepy.Stream(
            auth=self.auth,
            listener=ZenTweepyStreamListener(update_queue=self.update_queue))
        self.stream.userstream(async=True, replies='all')
        atexit.register(self.stream.disconnect)

    def restart_tweepy_stream(self):
        logger.debug('Restarting tweepy stream')
        self.stream.disconnect()
        atexit.unregister(self.stream.disconnect)
        self.start_tweepy_stream()

    def have_oauth_tokens(self, frame):
        if self.states.oauth_done is True:
            return True
        if frame.kind == KINDS.MESSAGE:
            self.message('I do not have oAuth tokens. Try "zentweepy auth".', reply_to=frame.id)
        else:
            data = {
                'text': 'oAuth tokens unavailable. '
                        'Please set in config or send "zentweepy auth" from shell.'
            }
            self.emit('{}_error'.format(frame.name), data=data, reply_to=frame.id)
        return False

    @on_event('*** start')
    async def startup(self, frame):
        if not self.have_oauth_tokens(frame):
            logger.debug('Skipping tweepy stream. Try "zentweepy auth" ')
            return
        logger.debug('Starting tweepy stream')
        self.start_tweepy_stream()
        self._listener_task = self.spawn(self.update_queue_listener())
        logger.debug('startup done')

    async def send_whoami(self):
        await self.sleep(1)
        whoami = self.api.me()
        # print('whomi', whoami._json)
        self.emit('twitter_whoami', data={'screen_name': whoami._json['screen_name'], 'id_str': whoami._json['id_str']})

    @on_event('*** stop')
    def shutdown(self, frame):
        logger.debug('shutdown now')
        if not self.have_oauth_tokens(frame):
            return
        self.stream.disconnect()
        self._listener_task.cancel()
        logger.debug('shutdown done')

    @on_message('debug {debug_state:w}', parse=True)
    def set_debug(self, message):
        debug = message.data.debug_state.lower().strip()
        if debug in ['true', 'on', 'yes']:
            self.states.debug = True
        elif debug in ['false', 'off', 'no']:
            self.states.debug = False
        else:
            return 'Try "debug on" or "debug off", or just "debug" to check state.'

    @on_message('debug')
    def get_debug(self, message):
        response = 'debug is {}'.format('on' if self.states.debug else 'off')
        return response

    @on_message('zentweepy auth')
    def do_oauth(self, frame):
        self.message('Let us set up authorization. Please visit this URL:', reply_to=frame.id)
        try:
            redirect_url = self.auth.get_authorization_url()
            self.states.wait_for_verifier = True
            print(redirect_url)
            self.message(redirect_url, reply_to=frame.id)
            return 'Copy-paste the verifier code below and hit enter.'
        except tweepy.TweepError:
            return 'Error! Failed to get request token.'

    @on_message('{verifier:w}', state_wait_for_verifier=True, parse=True)
    def verify_oauth(self, message):
        verifier = message.data.verifier
        try:
            self.auth.get_access_token(verifier)
            self.config.TWITTER_OAUTH_TOKEN = self.auth.access_token
            self.config.TWITTER_OAUTH_SECRET = self.auth.access_token_secret
            self.config.save()
            return 'Your configuration was updated. Please restart the agent.'
        except tweepy.TweepError:
            return 'Error! Failed to get access token.'

    @on_event(['zentweepy_send_update', 'zentweepy_send_reply'])
    @on_message('zentweepy send {text}', parse=True)
    def send_update(self, frame):
        if not self.have_oauth_tokens(frame):
            return
        update = frame.data.text.strip()
        in_reply_to = frame.data.in_reply_to.strip() if frame.data.in_reply_to else ''
        if not update:
            logger.debug('Skipping {}'.format(update))
            return
        try:
            if frame.name == 'zentweepy_send_reply' and not in_reply_to:
                self.emit('zentweepy_send_reply_error',
                          data={'text': 'Expected data.in_reply_to => Twitter status id.'})
                return
            elif frame.name == 'zentweepy_send_reply' and in_reply_to:
                request = self.api.update_status(update, in_reply_to_status_id=in_reply_to)
                logger.debug('reply sent')
            else:
                request = self.api.update_status(update)
                logger.debug('update sent')
            self.emit('{}_done'.format(frame.name))
            if frame.kind == KINDS.MESSAGE:
                return 'Sent: {}'.format(update)
        except Exception as e:
            data = {'text': '; '.join(e.args)} if self.states.debug else None
            self.emit('{}_error'.format(frame.name), data=data)

    @on_event('zentweepy_follow_user')
    @on_message('zentweepy follow {user:w}', parse=True)
    def follow_user(self, frame):
        if not self.have_oauth_tokens(frame):
            return
        user = frame.data.user.strip()
        if not user:
            # Since parser handles it, we won't see this issue with messages
            self.emit('zentweepy_follow_user_error',
                      data={'text': 'Expected data.user => Twitter screen_name or user.id'})
            return
        try:
            user_id = int(user)
        except ValueError:
            user_id = None
        try:
            if user_id:
                self.api.create_friendship(user_id=user_id, follow=True)
            else:
                self.api.create_friendship(screen_name=user, follow=True)
        except Exception as e:
            data = {'text': '; '.join(e.args)} if self.states.debug else None
            self.emit('zentweepy_follow_user_error', data=data)

    @on_event('zentweepy_unfollow_user')
    @on_message('zentweepy unfollow {user:w}', parse=True)
    def unfollow_user(self, frame):
        if not self.have_oauth_tokens(frame):
            return
        user = frame.data.user.strip()
        if not user:
            self.emit('zentweepy_unfollow_user_error',
                      data={'text': 'Expected data.user => Twitter screen_name or user.id'})
            return
        try:
            user_id = int(user)
        except ValueError:
            user_id = None
        try:
            if user_id:
                self.api.destroy_favorite(user_id=user_id, follow=True)
            else:
                self.api.destroy_favorite(screen_name=user, follow=True)
        except Exception as e:
            data = {'text': '; '.join(e.args)} if self.states.debug else None
            self.emit('zentweepy_unfollow_user_error', data=data)

    @on_event('zentweepy_like')
    def like(self, frame):
        if not self.have_oauth_tokens(frame):
            return
        id_ = frame.data.id
        if not id_:
            self.emit('zentweepy_like_error',
                      data={'text': 'Expected data.id => Twitter status.id'})
            return
        try:
            self.api.create_favorite(id=id_)
        except Exception as e:
            data = {'text': '; '.join(e.args)} if self.states.debug else None
            self.emit('zentweepy_like_error', data=data)

    @on_event('zentweepy_like_remove')
    def like_remove(self, frame):
        if not self.have_oauth_tokens(frame):
            return
        id_ = frame.data.id
        if not id_:
            self.emit('zentweepy_like_remove_error',
                      data={'text': 'Expected data.id => Twitter status.id'})
            return
        try:
            self.api.destroy_favorite(id=id_)
        except Exception as e:
            data = {'text': '; '.join(e.args)} if self.states.debug else None
            self.emit('zentweepy_like_remove_error', data=data)

    @on_event('zentweepy_retweet')
    def retweet(self, frame):
        if not self.have_oauth_tokens(frame):
            return
        id_ = frame.data.id
        if not id_:
            self.emit('zentweepy_retweet_error',
                      data={'text': 'Expected data.id => Twitter status.id'})
            return
        try:
            self.api.retweet(id=id_)
        except Exception as e:
            data = {'text': '; '.join(e.args)} if self.states.debug else None
            self.emit('zentweepy_retweet_error', data=data)

    @on_event('zentweepy_delete_update')
    def delete_update(self, frame):
        if not self.have_oauth_tokens(frame):
            return
        id_ = frame.data.id
        if not id_:
            self.emit('zentweepy_delete_update_error',
                      data={'text': 'Expected data.id => Twitter status.id'})
            return
        try:
            self.api.destroy_status(id=id_)
        except Exception as e:
            data = {'text': '; '.join(e.args)} if self.states.debug else None
            self.emit('zentweepy_delete_update_error', data=data)

    @on_event('zentweepy_block_user')
    def block_user(self, frame):
        if not self.have_oauth_tokens(frame):
            return
        user = frame.data.user.strip()
        if not user:
            self.emit('zentweepy_block_user_error',
                      data={'text': 'Expected data.user => Twitter screen_name or user.id'})
            return
        try:
            user_id = int(user)
        except ValueError:
            user_id = None
        try:
            if user_id:
                self.api.create_block(user_id=user_id, follow=True)
            else:
                self.api.create_block(screen_name=user, follow=True)
        except Exception as e:
            data = {'text': '; '.join(e.args)} if self.states.debug else None
            self.emit('zentweepy_block_user_error', data=data)

    @on_event('zentweepy_unblock_user')
    def unblock_user(self, frame):
        if not self.have_oauth_tokens(frame):
            return
        user = frame.data.user.strip()
        if not user:
            self.emit('zentweepy_unblock_user_error',
                      data={'text': 'Expected data.user => Twitter screen_name or user.id'})
            return
        try:
            user_id = int(user)
        except ValueError:
            user_id = None
        try:
            if user_id:
                self.api.destroy_block(user_id=user_id, follow=True)
            else:
                self.api.destroy_block(screen_name=user, follow=True)
        except Exception as e:
            data = {'text': '; '.join(e.args)} if self.states.debug else None
            self.emit('zentweepy_unblock_user_error', data=data)
