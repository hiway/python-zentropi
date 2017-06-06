# coding=utf-8
import asyncio
import gettext
import json
import logging
import signal
import traceback
from concurrent.futures import CancelledError
from typing import Any, Optional, TypeVar
import sys
import select
import time
import atexit

import locale as lib_locale
import os
import warnings
from zentropi.defaults import FRAME_DATA_MAX_LENGTH, FRAME_META_MAX_LENGTH

LoggerType = TypeVar('LoggerType', bound=logging.Logger)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def log_to_stream(stream: Optional[Any] = None, *,
                  level: Optional[Any] = None,
                  enable=True) -> LoggerType:
    """
    Send zentropi logs to stream, at logging.[DEBUG] level.
    Default: zentropi.defaults.LOG_LEVEL => logging.DEBUG

    Returns: handler instance.

    Example:
        >>> from zentropi.utils import log_to_stream
        >>> _ = log_to_stream()  # logs to sys.stdout

    Or

        >>> from zentropi.utils import log_to_stream
        >>> _ = log_to_stream(level=logging.WARNING)  # Only warning and higher
    """
    from zentropi.defaults import LOG_LEVEL

    global logger

    if not enable:
        return logger

    if not stream:
        stream = sys.stdout  # pragma: no cover
    handler = logging.StreamHandler(stream)
    handler.setLevel(level or LOG_LEVEL)
    formatter = logging.Formatter(
        '%(asctime)s %(threadName)-10s %(levelname)-6s '
        '%(filename)10s:%(lineno)03d %(funcName)-10s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def i18n_wrapper(locale: Optional[str] = None) -> Any:
    """
    Internationalize using gettext.

    Returns gettext for provided locale
    or default (zentropi.defaults.LOCALE).

    Example:
        >>> from zentropi.utils import i18n_wrapper
        >>> _ = i18n_wrapper()
        >>> print(_('Hello, world.'))
        Hello, world.
    """
    from zentropi import BASE_PATH
    from zentropi.defaults import LOCALE

    locale = locale or lib_locale.getlocale()[0] or LOCALE
    locale_dir = os.path.join(BASE_PATH, 'locale')
    locale_file = os.path.join(locale_dir, '{}.mo'.format(locale))
    try:
        translation = gettext.GNUTranslations(open(locale_file, 'rb'))
    except IOError:
        warnings.warn('Translation file for {} not found at: {}. Using default.'
                      ''.format(locale, locale_file))
        translation = gettext.NullTranslations()  # type: ignore
    translation.install()
    return translation.gettext


def deflate_dict(frame_as_dict):
    return {k: v for k, v in frame_as_dict.items() if v}


def validate_handler(handler):
    from zentropi.handlers import Handler

    if handler is None:
        return None
    if isinstance(handler, Handler):
        return handler
    raise ValueError('Expected handler to an instance of Handler. '
                     'Got: {!r}'.format(handler))


def validate_name(name):
    from zentropi.defaults import FRAME_NAME_MAX_LENGTH

    if name is None:
        return None
    if not name or not isinstance(name, str) or len(name.strip()) == 0:
        raise ValueError('Expected name to be a non-empty string. '
                         'Got: {!r}'.format(name))
    if len(name) > FRAME_NAME_MAX_LENGTH:
        raise ValueError('Expected name to be <= {} unicode characters long. '
                         'Got: {} characters: {!r}'.format(FRAME_NAME_MAX_LENGTH, len(name), name))
    return name


def validate_kind(kind):
    from zentropi.symbols import KINDS

    if kind is None:
        return KINDS.UNSET
    if isinstance(kind, int):
        return KINDS(kind)
    if kind not in KINDS:
        raise ValueError('Expected kind to be one of zentropi.symbols.Kinds: {!r}. '
                         'Got: {!r}'.format(', '.join([str(k) for k in KINDS]), kind))
    return kind


def validate_data(data):
    from zentropi.frames import FrameData

    if not data:
        return FrameData()  # type: ignore
    assert isinstance(data, (dict, FrameData)), data
    if isinstance(data, FrameData):
        data = data.data
    assert len(json.dumps(data)) < FRAME_DATA_MAX_LENGTH
    return FrameData(data)  # type: ignore


def validate_meta(meta: dict = None) -> dict:
    if meta is None:
        return {}
    assert isinstance(meta, dict)
    assert len(json.dumps(meta)) < FRAME_META_MAX_LENGTH
    return meta


def validate_id(id: str = None) -> Optional[str]:
    if id is None:
        return None
    assert isinstance(id, str)
    return id


def validate_endpoint(endpoint: str) -> str:
    if not isinstance(endpoint, str):
        raise ValueError('Expected endpoint to be a string.'
                         'Got: {!r}'.format(endpoint))
    endpoint = endpoint.strip().lower()
    return endpoint


def validate_space(space):
    if not isinstance(space, str):
        raise ValueError('Expected space to be a string.'
                         'Got: {!r}'.format(space))
    return space


def validate_auth(auth):
    if auth is None:
        return auth
    if not isinstance(auth, str):
        raise AssertionError('Expected auth to be str. Got: {!r}'.format(auth))
    return auth


SCHEDULER_INSTANCE = None


def scheduler_emit(**kwargs):
    scheduler = SCHEDULER_INSTANCE
    if not scheduler:
        print('!!! No SCHEDULER_INSTANCE set! Skipping: {!r}'.format(kwargs))
        return
    print('*** scheduler emit: {!r}'.format(kwargs))
    scheduler.emit(**kwargs)


def env_split(line):
    key, value = line.split('=')
    return key, value


def load_env_variables(file_path):
    with open(os.path.expanduser(file_path)) as envfile:
        env = envfile.readlines()
    env = [env_split(l) for l in env if l.strip()]
    for key, value in env:
        os.environ[key] = value


def select_timed_input(prompt, timeout):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().strip()
    else:
        return None


class StopAgent(Exception):
    pass


def stop_agent_signal(signum, frame):
    print('Caught signal %d' % signum)
    raise StopAgent


def run_final_agent(loop, last_agent):
    try:
        last_agent.run()
    except (KeyboardInterrupt, StopAgent):
        last_agent.stop()
    except Exception as e:
        last_agent.stop()
        raise e
    finally:
        pending = asyncio.Task.all_tasks()
        len_pending = len(pending)
        if not len_pending:
            return
        log_message = 'Waiting for {} pending tasks'.format(len_pending)
        logger.debug(log_message)
        print(log_message)
        try:
            loop.run_until_complete(asyncio.gather(*pending))
        except CancelledError:
            pass


def run_agents(*agents, endpoint='inmemory://', auth=None, space='zentropia',
               loop=None, shell=False, env=None):
    import asyncio
    from zentropi import Agent
    signal.signal(signal.SIGTERM, stop_agent_signal)
    signal.signal(signal.SIGINT, stop_agent_signal)
    signal.signal(signal.SIGALRM, stop_agent_signal)

    if env:
        load_env_variables(env)

    endpoint = validate_endpoint(endpoint)
    space = validate_space(space)

    if not agents:
        return
    agents = list(agents)
    for agent in agents:
        if not isinstance(agent, Agent):
            raise ValueError('Expected an instance of Agent. Got: {!r}'.format(agent))
    if shell:
        from zentropi import ZentropiShell
        shell = ZentropiShell('shell', auth='4cb1c5fe714b469caae03f26e635f676')
        agents.append(shell)
    if not loop:
        loop = asyncio.get_event_loop()

    if len(agents) == 1:
        agent = agents[0]
        if not endpoint.startswith('inmemory://'):
            agent.connect(endpoint, auth=auth)
            agent.join(space)
        run_final_agent(loop, agent)
        return
    if len(agents) == 2:
        first_agent = agents[0]
        last_agent = agents[1]
        more_agents = []
    else:  # if len(agents) > 2:
        first_agent = agents[0]
        last_agent = agents[-1]
        more_agents = agents[1:-1]

    if endpoint.startswith('inmemory://'):
        # bind the first agent for inmemory:// connections
        first_agent.start(loop=loop)
        first_agent.bind(endpoint)
        first_agent.join(space)
        connect_agents = more_agents
    else:
        connect_agents = [first_agent] + more_agents

    for agent in connect_agents:
        agent.start(loop=loop)
        agent.connect(endpoint, auth=auth)
        agent.join(space)

    last_agent.connect(endpoint, auth=auth)
    last_agent.join(space)
    last_agent.loop = loop

    @last_agent.on_event('*** stop')
    def exit_other_agents(event):
        logger.debug('stopping agent {}'.format(type(first_agent).__name__))
        first_agent.stop()
        for agent in connect_agents:
            try:
                logger.debug('stopping agent {}'.format(type(agent).__name__))
                agent.stop()
            except:
                traceback.print_exc()
                pass

    run_final_agent(loop, last_agent)


def run_agents_forever(*agents, endpoint='inmemory://', auth=None, space='zentropia',
                       loop=None, shell=False, env=None, timeout=10, confirm=True):
    try:
        run_agents(*agents, endpoint=endpoint, auth=auth, space=space,
                   loop=loop, shell=shell, env=env)
    except StopAgent as e:
        pass
    except Exception as e:
        traceback.print_exc()
    if confirm:
        try:
            text = select_timed_input('Restarting in {} seconds... press ENTER to quit...'
                                      ''.format(timeout), timeout=timeout)
            if text is not None and text.lower() in ['', 'q', 'quit', 'exit']:
                return
        except StopAgent as e:
            pass
        except Exception as e:
            traceback.print_exc()
    else:
        time.sleep(timeout)  # Wait to avoid rapid restarts.
    atexit._run_exitfuncs()
    python = sys.executable
    # hard restart, resources will NOT free up automatically.
    os.execl(python, python, *sys.argv)
