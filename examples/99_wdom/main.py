# coding=utf-8
from pprint import pformat

import os
from wdom import server
from wdom.server import start_server, stop_server
from wdom.document import get_document
from wdom.tag import Li, Style, Ul

from zentropi import Agent, KINDS, on_event, on_message, run_agents

server.set_server_type('tornado')

ZENTROPI_REDIS_PASSWORD = os.getenv('ZENTROPI_REDIS_PASSWORD', None)
FRAME_PREFIX = {
    KINDS.EVENT: '⚡︎',
    KINDS.MESSAGE: '✉',
    KINDS.STATE: '⇥',
    KINDS.COMMAND: '⎈',
    KINDS.REQUEST: '🔺',
    KINDS.RESPONSE: '🔻',
}

frame_template = """<span class='prefix'>{prefix}</span>
<span class='source_name'>@{source}:</span> 
<span class='frame_name'>{name}</span>"""

data_template = """<pre class="frame_data">{data}</pre>"""


style = """\
body {
    background-color: #F7F6F7;
    color: #3A3239;
    font-family: verdana, sans-serif;
}

ul {
    list-style-type: none;
}

li {
    padding: 0.2em;
}

.frame_name {
    color: #DD5564;
}

.frame_data {
    font-family: monospace;
    font-size: 0.9em;
    color: #8489AE;
    display: block;
    margin-left: 5em;
    margin-top: 1em;
    line-height: 1.1em;
}

.source_name {
}

.prefix {
    color: #A72D73;
    width: 10em;
    display: inline;
}
"""


class BrowserDOMAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.document = get_document()
        self.document.head.appendChild(Style(style))
        self.ul = Ul(class_='zen-log')
        self.document.body.appendChild(self.ul)

    @on_event('*')
    @on_message('*')
    def every_frame(self, frame):
        li = Li()
        prefix = FRAME_PREFIX[frame.kind]
        text = frame_template.format(prefix=prefix, source=frame.source, name=frame.name)
        data = frame.data
        if data and not (len(data.keys()) == 1 and 'text' in data):
            text += data_template.format(data=pformat(data))

        li.innerHTML = text
        self.ul.appendChild(li)


if __name__ == '__main__':
    start_server()
    try:
        dom_agent = BrowserDOMAgent('dom')
        run_agents(dom_agent, shell=True, endpoint='redis://127.0.0.1:6379', auth=ZENTROPI_REDIS_PASSWORD)
    except KeyboardInterrupt:
        stop_server()
    finally:
        stop_server()
