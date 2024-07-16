from .future import AbruptOutcome, NormalOutcome
from diapyr.util import innerclass
from functools import partial
from inspect import iscoroutinefunction

nulloutcome = NormalOutcome(None)

class Message:

    def __init__(self, methodname, args, kwargs, future):
        self.methodname = methodname
        self.args = args
        self.kwargs = kwargs
        self.future = future

    def taskornone(self, obj, mailbox):
        try:
            method = getattr(obj, self.methodname)
        except AttributeError:
            return
        if iscoroutinefunction(method):
            return partial(Coro(obj, method(*self.args, **self.kwargs), self.future).fire, nulloutcome, mailbox)
        return partial(self._fire, method)

    def _fire(self, method):
        try:
            value = method(*self.args, **self.kwargs)
        except BaseException as e:
            self.future.set(AbruptOutcome(e))
        else:
            self.future.set(NormalOutcome(value))

class Coro:

    @innerclass
    class Message:

        def __init__(self, outcome):
            self.outcome = outcome

        def taskornone(self, obj, mailbox):
            if obj is self.obj:
                return partial(self.fire, self.outcome, mailbox)

    def __init__(self, obj, coro, future):
        self.obj = obj
        self.coro = coro
        self.future = future

    def fire(self, outcome, mailbox):
        try:
            g = outcome.propagate(self.coro)
        except StopIteration as e:
            self.future.set(NormalOutcome(e.value))
        except BaseException as e:
            self.future.set(AbruptOutcome(e))
        else:
            try:
                listenoutcome = g.listenoutcome
            except AttributeError:
                self.future.set(AbruptOutcome(RuntimeError(f"Unusable yield: {g}")))
            else:
                listenoutcome(lambda o: mailbox.add(self.Message(o)))
