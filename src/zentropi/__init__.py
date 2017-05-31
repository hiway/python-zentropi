# coding=utf-8

LICENSE = """
Copyright 2017 Harshad Sharma

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os

import zentropi.fields as fields
import zentropi.utils as utils
from zentropi.agent import Agent, on_timer
from zentropi.connections import Connection
from zentropi.connections.in_memory import \
    InMemoryConnection
from zentropi.events import Events
from zentropi.fields import Field
from zentropi.frames import (
    Command,
    Event,
    Frame,
    Message,
    State
)
from zentropi.shell import ZentropiShell
from zentropi.spaces import Spaces
from zentropi.symbols import KINDS
from zentropi.utils import (
    run_agents,
    run_agents_forever
)
from zentropi.zentropian import (
    Zentropian,
    on_event,
    on_message,
    on_state
)

__version__ = "0.1.3"

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

__all__ = [
    '__version__',
    'Agent',
    'BASE_PATH',
    'Command',
    'Connection',
    'Event',
    'Events',
    'Frame',
    'Field',
    'fields',
    'InMemoryConnection',
    'KINDS',
    'Message',
    'on_event',
    'on_message',
    'on_state',
    'on_timer',
    'run_agents',
    'run_agents_forever',
    'ZentropiShell',
    'Spaces',
    'State',
    'utils',
    'Zentropian',
]
