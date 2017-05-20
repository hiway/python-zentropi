# coding=utf-8
from zentropi import (
    Agent,
    ZentropiShell,
    on_event,
    on_message,
    run_agents
)


class SnippetBot(Agent):
    """
    An agent that can save and search text snippets.
    """
    def save(self, text: str) -> None:
        """Saves text to data-store."""
        print('DUMMY Save: {!r}'.format(text))

    def search(self, query: str) -> list:
        """Searches data-store for query, returns list of matching strings."""
        print('DUMMY Search: {!r}'.format(query))
        return []

    def delete(self, id: str) -> None:
        print('DUMMY Delete: {!r}'.format(id))

    @on_event('snippet-save')
    def on_snippet_save(self, event):
        text = event.data.text
        if not text:
            self.emit('snippet-save-error', data={'error': '`data.text` not found in event-id: {}'.format(event.id)})
            return
        self.save(text)
        self.emit('snippet-save-complete')

    @on_event('snippet-search')
    def on_snippet_search(self, event):
        query = event.data.query
        if not query:
            self.emit('snippet-query-error', data={'error': '`data.query` not found in event-id: {}'.format(event.id)})
            return
        results = self.search(query)
        self.emit('snippet-query-results', data={'results': results})

    @on_event('snippet-delete')
    def on_snippet_delete(self, event):
        id_ = event.data.id
        if not id_:
            self.emit('snippet-delete-error', data={'error': '`data.id` not found in event-id: {}'.format(event.id)})
            return
        self.delete(id_)
        self.emit('snippet-delete-complete')

    @on_message('snip {snippet}', parse=True)
    def on_save(self, message):
        snippet = message.data.snippet
        self.save(snippet)
        return 'Saved'

    @on_message('snips {query}', parse=True)
    def on_search(self, message):
        query = message.data.query.strip().lower()
        results = self.search(query)
        if not results:
            return 'Found nothing.'
        return '\n'.join(results)


if __name__ == '__main__':
    snippet_bot = SnippetBot(name='snip')
    run_agents(snippet_bot, shell=True)
