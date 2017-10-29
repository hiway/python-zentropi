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
# from pkgutil import extend_path
# __path__ = extend_path(__path__, __name__)
import pkg_resources
pkg_resources.declare_namespace(__name__)

__version__ = "0.1.3"

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

from uzentropi import (
    RATE_LIMIT,
    PLATFORM,
    MICROPY,
    PYTHON,
    Kind,
    Frame,
    Session,
    Handler,
    on_command,
    on_event,
    on_message,
    on_request,
    on_state,
    on_timer,
    WebsocketConnection,
    RateLimitError,
)

from .agent import Agent

__all__ = [
    '__version__',
    'PLATFORM',
    'MICROPY',
    'PYTHON',
    'RATE_LIMIT',
    'Agent',
    'Frame',
    'Handler',
    'Kind',
    'Session',
    'WebsocketConnection',
    'asyncio',
    'on_command',
    'on_event',
    'on_message',
    'on_request',
    'on_state',
    'on_timer'
]
