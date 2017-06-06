# coding=utf-8
import cachetools
from zentropi import Agent, Config, on_event, run_agents
from zentropi.utils import logger


class CateepultConfig(Config):
    _can_extend = True
    _can_modify = True

    DEBUG = False


class Catweepult(Agent):
    def __init__(self, name=None, config=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.config = config or CateepultConfig()
        # self.store = PersistentStore('~/.zentropi/catweepult.db')
        self._friends = []
        self._whoami = {}
        self._my_id = ''
        self.states.period = 10 * 60
        self._rts_in_last_period = cachetools.TTLCache(maxsize=100, ttl=self.states.period)

    @on_event('twitter_whoami')
    def whoami(self, event):
        self._my_id = event.data['id_str']
        self._whoami = event.data
        logger.debug('Signed in as {}'.format(event.data['screen_name']))

    @on_event('twitter_stream_raw')
    def on_raw(self, event):
        if 'friends' not in event.data:
            return
        self._friends = event.data['friends']

    @on_event('twitter_update')
    def on_twitter_update(self, event):
        username = event.data.username
        text = event.data.text.lower()
        print('@{}: {}'.format(username, text))
        if 'hello' in text:
            self.emit('zentweepy_send_reply', data={'text': '@hiway ohai', 'in_reply_to': event.data.id_str})


if __name__ == '__main__':
    # from zentweepy import ZenTweepy
    # zentweepy = ZenTweepy('zentweepy')

    catweepult = Catweepult(name='Catweepult', auth='f96e4809b01d4e00a0c3f318ee0f9b6e')

    # run_agents(catweepult, zentweepy, shell=True)
    run_agents(catweepult, shell=False, endpoint='wss://local.zentropi.com')
