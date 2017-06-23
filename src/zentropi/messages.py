# coding=utf-8
from zentropi.frames import Message
from zentropi.handlers import Registry


class Messages(Registry):
    def message(self, name, data=None, space=None, internal=False, source=None, reply_to=None, target=None):
        frame_ = Message(name=name, data=data, space=space, source=source, reply_to=reply_to, internal=internal, target=target)
        # frame, handlers = self._registry.match(frame=frame_)
        # for handler in handlers:
        #     ret_val = self._trigger_frame_handler(
        #         frame=frame, handler=handler, internal=internal)
        #     if ret_val is not None:  # todo: is this needed? (see: agent.handle_return())
        #         raise NotImplementedError('Send message as reply.')
        # return frame
        return frame_
