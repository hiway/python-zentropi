# coding=utf-8
version = '0.0.1'

import requests

POST = requests.post
GET = requests.get
DELETE = requests.delete
PATCH = requests.patch


class API(object):
    def __init__(self, endpoint='https://zentropi.com/api', token=''):
        self.endpoint = endpoint
        self.token = token

    def _api_call(self, method, path, headers=None, extract='', **payload):
        headers = headers or {}
        headers.update({"Accept": "application/json"})
        headers.update({"Content-Type": "application/json"})
        if path not in ['/login', '/register'] and not self.token:
            assert self.token, 'token not provided'
        else:
            headers.update({'Authorization': 'Bearer {}'.format(self.token)})

        r = method(self.endpoint + path, json=payload, headers=headers)
        if isinstance(extract, str):
            try:
                return r.json()[0][extract]
            except:
                pass
        elif extract is True:
            try:
                return r.json()[0]
            except:
                pass
        try:
            return r.json()
        except:
            return r.text

    def register(self, email, username, password):
        payload = {'email': email, 'username': username, 'pass': password}
        return self._api_call(POST, '/register', extract='message', **payload)

    def login(self, username, password):
        payload = {'username': username, 'pass': password}
        return self._api_call(POST, '/login', extract='token', **payload)

    def login_agent(self, agent_name):
        return self._api_call(POST, '/login_agent', extract='token', agent=agent_name)

    def agent(self, name):
        return self._api_call(GET, '/agent?name=eq.{}'.format(name))

    def all_agents(self):
        return self._api_call(GET, '/agent')

    def agent_create(self, name, description):
        return self._api_call(POST, '/agent', name=name, description=description)

    def agent_update(self, name, description):
        return self._api_call(PATCH, '/agent', name=name, description=description)

    def agent_delete(self, name):
        return self._api_call(DELETE, '/agent', name=name)

    def space(self, name):
        return self._api_call(GET, '/space?name=eq.{}'.format(name))

    def all_spaces(self):
        return self._api_call(GET, '/space')

    def space_create(self, name, description):
        return self._api_call(POST, '/space', name=name, description=description)

    def space_update(self, name, description):
        return self._api_call(PATCH, '/space', name=name, description=description)

    def space_delete(self, name, description):
        return self._api_call(DELETE, '/space', name=name)

    def join(self, space, agent):
        return self._api_call(POST, '/join', space=space, agent=agent)

    def leave(self, space, agent):
        return self._api_call(POST, '/leave', space=space, agent=agent)

    def spaces(self, agent):
        return self._api_call(POST, '/spaces', agent=agent)

    def agents(self, space):
        return self._api_call(POST, '/agents', space=space)
