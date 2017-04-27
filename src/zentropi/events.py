# coding=utf-8
from zentropi.frames import Event
from zentropi.handlers import Registry


class Events(Registry):
    """
    class Zentropian:
        self.events = Events(callback=self._trigger_frame_handler)


    zen.emit('event-name', data={}, internal=False)

    @zen.on_event('event-name', parse=True)
    def handle_event_name(event):
        pass
    """
    def emit(self, name, data=None, space=None, internal=False, source=None, reply_to=None):
        frame_ = Event(name=name, data=data, space=space, source=source, reply_to=reply_to)
        frame, handlers = self._registry.match(frame=frame_)
        for handler in handlers:
            ret_val = self._trigger_frame_handler(
                frame=frame, handler=handler, internal=internal)
            if ret_val is not None:
                raise ValueError('Returning values from event handler has no effect. '
                                 'Got: {}'.format(ret_val))
        return frame
