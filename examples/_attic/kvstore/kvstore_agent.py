# coding=utf-8
import os

from zentropi import Agent, on_event, on_message

try:
    from tinydb import (
        Query,
        TinyDB,
    )
except ImportError as e:
    raise ImportError('Run `pip install tinydb` (https://tinydb.readthedocs.io/)')


STORE_PATH = os.path.expanduser('~/.zentropi/kvstore.db')


class KVStoreAgent(Agent):
    def __init__(self, name=None, *, path=None):
        super().__init__(name=name)
        self.db = TinyDB(path or STORE_PATH)

    def _set(self, key, value):
        Record = Query()
        records = self.db.search(Record.key == key)
        eids = [r.eid for r in records]
        element_data = {'key': key, 'value': value}
        if len(eids) > 1:
            self.db.remove(eids=eids[:-1])
        if eids:
            return self.db.update(element_data, eids=[eids[-1]])[0]
        return self.db.insert(element_data)

    def _get(self, key):
        Record = Query()
        values = self.db.search(Record.key == key)
        return values[0]['value'] if values else None

    @on_event('kvstore-set')
    def event_kvstore_set(self, event):
        key = event.data.key
        value = event.data.value
        eid = self._set(key, value)
        self.emit('kvstore-updated',
                  data={'id': eid, 'key': key, 'value': value})

    @on_event('kvstore-get')
    def event_kvstore_set(self, event):
        key = event.data.key
        value = self._get(key)
        self.emit('kvstore-get-result',
                  data={'id': value['eid'], 'key': key, 'value': value['value']})

    @on_message('kvstore {key}={value}', parse=True)
    def message_kvstore_set(self, message):
        key = message.data.key
        value = message.data.value
        eid = self._set(key, value)
        return 'Set {}: {!r} = {!r}'.format(eid, key, value)

    @on_message('kvstore {key}', parse=True)
    def message_kvstore_get(self, message):
        key = message.data.key
        value = self._get(key)
        return '{!r} = {!r}'.format(key, value)
