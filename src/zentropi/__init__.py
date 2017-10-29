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

__version__ = "0.1.3"

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

from uzentropi import (
    MICROPY,
    PLATFORM,
    PYTHON,
    RATE_LIMIT,
    Frame,
    Handler,
    Kind,
    Session,
    WebsocketConnection,
    asyncio,
    on_event,
    on_message,
    on_request,
    on_state,
    on_timer,
)

from .agent import Agent, on_command
from .errors import RateLimitError

__all__ = [
    '__version__',
    'MICROPY',
    'PLATFORM',
    'PYTHON',
    'RATE_LIMIT',
    'Agent',
    'Frame',
    'Handler',
    'Kind',
    'RateLimitError',
    'Session',
    'WebsocketConnection',
    'asyncio',
    'on_command',
    'on_event',
    'on_message',
    'on_request',
    'on_state',
    'on_timer',
]
