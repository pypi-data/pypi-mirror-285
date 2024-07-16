from .future import Future
from .mailbox import Mailbox
from .message import Message
from functools import partial

class Spawn:

    def __init__(self, executor):
        self.executor = executor

    def __call__(self, *objs):
        'Create an actor backed by the given object(s), each of which is used in a single-threaded way.'
        def post(name, *args, **kwargs):
            future = Future()
            mailbox.add(Message(name, args, kwargs, future))
            return future
        def __getattr__(self, name):
            return partial(post, name)
        mailbox = Mailbox(self.executor, objs)
        return type(f"{''.join({type(obj).__name__: None for obj in objs})}Actor", (), {f.__name__: f for f in [__getattr__]})()
