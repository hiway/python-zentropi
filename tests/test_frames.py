# coding=utf-8
import json
import time
import unittest

from zentropi.frames import (
    Command,
    Event,
    Frame,
    FrameData,
    Message,
    Request,
    Response,
    State
)
from zentropi.symbols import KINDS


def test_frame_data():
    data = FrameData()
    data.test = 'test'
    assert data.test == 'test'
    assert data.unknown is None


def test_frame_empty():
    frame = Frame()
    assert frame.id
    assert frame.name is None
    assert frame.data == {}
    assert frame.source is None
    assert frame.target is None
    assert frame.space is None
    assert frame.reply_to is None

    frame.name = 'test'
    frame.data = {'a': 'b'}
    frame.target = 'test-target'
    frame.space = 'test-space'
    frame.reply_to = 'test-reply-to'
    assert frame.name == 'test'
    assert frame.data == {'a': 'b'}
    assert frame.target == 'test-target'
    assert frame.space == 'test-space'
    assert frame.reply_to == 'test-reply-to'


def test_frame_full():
    frame = Frame(
        name='test',
        data={'a': 'b'},
        meta={'c': 'd'},
        id='test-id',
        source='test-source',
        target='test-target',
        space='test-space',
        reply_to='test-reply-to',
        timestamp=int(time.time()),
    )
    assert frame.name == 'test'
    assert frame.data == {'a': 'b'}
    assert 'c' in frame.meta
    assert frame.id == 'test-id'
    assert frame.source == 'test-source'
    assert frame.target == 'test-target'
    assert frame.space == 'test-space'
    assert frame.reply_to == 'test-reply-to'


class TestZenceliumFrame(unittest.TestCase):
    def test_frame_id(self):
        frame1 = Frame()
        frame2 = Frame()
        assert isinstance(frame1, Frame)
        assert isinstance(frame1.id, str)
        assert len(frame1.id) > 5
        assert frame1.id != frame2.id

    def test_frame_name(self):
        frame1 = Frame()
        frame1.name = 'this is a test'
        assert frame1.name == 'this is a test'
        frame2 = Frame('this is a test')
        assert frame2.name == 'this is a test'

    def test_frame_name_max_length(self):
        with self.assertRaises(ValueError):
            _ = Frame('X' * 129)

    def test_frame_name_min_length(self):
        with self.assertRaises(ValueError):
            _ = Frame('')

    def test_data(self):
        frame1 = Frame()
        frame1.data = {'a': 'test'}
        assert frame1.data == {'a': 'test'}
        frame2 = Frame(data={'a': 'test'})
        assert frame2.data == {'a': 'test'}

    def test_meta(self):
        frame1 = Frame(meta={'a': 'test'})
        assert 'a' in frame1.meta
        assert frame1.meta['a'] == 'test'

    def test_meta_assignment_fails(self):
        with self.assertRaises(AttributeError):
            frame1 = Frame()
            frame1.meta = {'a': 'test'}

    def test_kind(self):
        frame1 = Frame(kind=KINDS.EVENT)
        assert frame1.kind == KINDS.EVENT

    def test_kind_validation(self):
        with self.assertRaises(ValueError):
            _ = Frame(kind=99)
        with self.assertRaises(ValueError):
            _ = Frame(kind=-2)  # -1 is TIMER

    def test_given_id(self):
        frame1 = Frame(id='stuff')
        assert frame1.id == 'stuff'

    def test_command(self):
        command = Command()
        assert command.kind == KINDS.COMMAND

    def test_event(self):
        event = Event()
        assert event.kind == KINDS.EVENT
        del event
        event = Event('a test', data={'another': 'test'})
        assert event.id
        assert event.name == 'a test'
        assert event.data == {'another': 'test'}
        assert isinstance(Frame.build(**event.as_dict()), Event)

    def test_message(self):
        message = Message()
        assert message.kind == KINDS.MESSAGE
        del message
        message = Message('a test', data={'another': 'test'})
        assert message.id
        assert message.name == 'a test'
        assert message.data == {'another': 'test'}
        assert isinstance(Frame.build(**message.as_dict()), Message)

    def test_state(self):
        state = State()
        assert state.kind == KINDS.STATE
        del state
        state = State('a test', data={'another': 'test'})
        assert state.id
        assert state.name == 'a test'
        assert state.data == {'another': 'test'}
        assert isinstance(Frame.build(**state.as_dict()), State)

    def test_request(self):
        request = Request()
        assert request.kind == KINDS.REQUEST
        del request
        request = Request('a test', data={'another': 'test'})
        assert request.id
        assert request.name == 'a test'
        assert request.data == {'another': 'test'}
        assert isinstance(Frame.build(**request.as_dict()), Request)

    def test_response(self):
        response = Response()
        assert response.kind == KINDS.RESPONSE
        del response
        response = Response('a test', data={'another': 'test'})
        assert response.reply_to is None
        response.reply_to = 'okaythen'
        assert response.id
        assert response.name == 'a test'
        assert response.data == {'another': 'test'}
        assert response.reply_to == 'okaythen'
        assert isinstance(Frame.build(**response.as_dict()), Response)

    def test_unset(self):
        frame = Frame()
        assert frame.kind == KINDS.UNSET

    def test_build(self):
        frame = Frame.build('test', data={'a': 'test'}, meta={'another': 'test'})
        assert frame.name == 'test'
        assert frame.data == {'a': 'test'}
        assert 'another' in frame.meta
        assert frame.kind == KINDS.UNSET

    def test_build_command(self):
        frame = Frame.build('test', data={'a': 'test'}, meta={'another': 'test'}, kind=KINDS.COMMAND)
        assert frame.name == 'test'
        assert frame.data == {'a': 'test'}
        assert 'another' in frame.meta
        assert frame.kind == KINDS.COMMAND
        assert isinstance(frame, Command)

    def test_build_event(self):
        frame = Frame.build('test', data={'a': 'test'}, meta={'another': 'test'}, kind=KINDS.EVENT)
        assert frame.name == 'test'
        assert frame.data == {'a': 'test'}
        assert 'another' in frame.meta
        assert frame.kind == KINDS.EVENT
        assert isinstance(frame, Event)

    def test_frame_meta_properties(self):
        frame1 = Frame()
        assert frame1.space is None
        assert frame1.source is None
        assert frame1.target is None
        assert frame1.timestamp is not None
        frame1.space = 'sandbox'
        assert frame1.space == 'sandbox'

        frame2 = Frame.build('test', data={'yet': 'another', 'test': 'eh'},
                             meta={
                                 'space': 'zentropia',
                                 'source': 'stranger',
                                 'target': 'me',
                                 'timestamp': 'Just a string, really'
                             })
        assert frame2.space == 'zentropia'
        assert frame2.source == 'stranger'
        assert frame2.target == 'me'
        assert frame2.timestamp == 'Just a string, really'
        frame2.space = 'home'
        assert frame2.space == 'home'
        frame2.target = 'unknown'
        assert frame2.target == 'unknown'

        frame3 = Frame()
        frame3.target = 'test'
        assert frame3.target == 'test'

    def test_frame_as_dict(self):
        frame = Frame.build('hello', data={'name': 'world'})
        frame_as_dict = frame.as_dict()
        assert isinstance(frame_as_dict['id'], str)
        assert frame_as_dict['name'] == 'hello'
        assert frame_as_dict['data'] == {'name': 'world'}

    def test_frame_as_json(self):
        frame = Frame.build('hello', data={'name': 'world'})
        frame_as_json = frame.as_json()
        frame_as_dict = json.loads(frame_as_json)
        assert isinstance(frame_as_dict['id'], str)
        assert frame_as_dict['name'] == 'hello'
        assert frame_as_dict['data'] == {'name': 'world'}

    def test_frame_from_dict(self):
        frame = Frame.from_dict({'name': 'ohai', 'data': {'name': 'geek'}})
        assert frame.name == 'ohai'
        assert frame.data == {'name': 'geek'}

    def test_frame_from_json(self):
        frame_as_json = json.dumps({'name': 'ohai', 'data': {'name': 'geek'}})
        frame = Frame.from_json(frame_as_json)
        assert frame.name == 'ohai'
        assert frame.data == {'name': 'geek'}
