# coding=utf-8
from .connections.connection import Connection
from .frames import Command

class Space(object):
    def __init__(self, name):
        self._name = name
        self._agents = set()

    @property
    def agents(self):
        return self._agents

    @property
    def name(self):
        return self._name

    def join(self, agent_name):
        if agent_name in self._agents:  # todo: is exception needed/useful/harmful?
            raise ValueError('Agent {!r} failed to join space {!r} because'
                             'another agent by same name had already joined.'
                             ''.format(agent_name, self._name))
        self._agents.add(agent_name)

    def leave(self, agent_name):
        if agent_name not in self._agents:
            raise ValueError('Agent: {} not found in space: {}'
                             ''.format(agent_name, self._name))
        self._agents.remove(agent_name)


class Spaces(object):
    def __init__(self):
        super().__init__()
        self._spaces = {}  # {space_name: space_instance}
        self._agents = {}  # todo: weak reference

    def agents(self, space=None):
        if not space:
            return [a for a in self._agents]  # ['agent_name', ]
        if space not in self._spaces:
            raise ValueError('Space: {} not found in spaces.'
                             ''.format(space))
        return [a for a in self._spaces[space].agents]  # ['agent_name', ]

    def spaces(self, agent=None):
        if not agent:
            return list(self._spaces.keys())
        return [n for n, s in self._spaces.items() if agent in s.agents]

    def join(self, agent_name, space_name):
        spaces = self._spaces
        if space_name not in spaces:
            space = Space(name=space_name)
        else:
            space = spaces[space_name]
        try:
            space.join(agent_name)
            self._spaces[space_name] = space
            return Command('join', data={'space': str(space.name)})
        except ValueError:
            return Command('join-failed', data={'space': str(space.name)})

    def agent_connect(self, agent_name, connection):
        agents = self._agents
        if agent_name in agents:
            raise ValueError('Agent: {} failed to connect to Spaces because '
                             'another agent by same name is already connected.'
                             ''.format(agent_name))
        if connection and not isinstance(connection, Connection):
            raise ValueError('Expected instance of Connection, got: {}'
                             ''.format(connection))
        self._agents[agent_name] = connection

    def broadcast(self, frame):
        if isinstance(frame, Command):
            return self.handle_command(frame)
        space = frame.space
        source = frame.source
        if space and space in self.spaces(source):
            spaces_ = [self._spaces[space]]
        else:
            spaces_ = [self._spaces[s] for s in self.spaces(source)]
        spaces = [self._spaces[s.name] for s in spaces_]
        # print(self._agents)
        for space in spaces:
            for connection in [self._agents[a] for a in space.agents]:
                connection.send(frame=frame, internal=True)

    def handle_command(self, command):
        if not isinstance(command, Command):
            raise ValueError('Expected command to be instance of Command, got: {}'
                             ''.format(command))
        connection = self._agents[command.source]
        # todo: handle joins and leaves
        if command.name == 'join':
            frame = self.join(command.source, command.data.space)
            connection.broadcast(frame)

    def agent_close(self, agent_name):
        # connection = self._agents[agent_name]
        print('*** noop closing')
        # connection.close()
