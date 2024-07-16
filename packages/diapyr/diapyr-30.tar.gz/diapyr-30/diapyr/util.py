import sys

ispy2 = sys.version_info.major < 3

class Proxy(object):

    def __getattr__(self, name):
        try:
            return getattr(self._enclosinginstance, name)
        except AttributeError:
            superclass = super(Proxy, self)
            try:
                supergetattr = superclass.__getattr__
            except AttributeError:
                raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__, name))
            return supergetattr(name)

def innerclass(cls):
    'An instance of the decorated class may access its enclosing instance via `self`.'
    class InnerMeta(type):
        def __get__(self, enclosinginstance, owner):
            clsname = (cls if self is Inner else self).__name__
            return type(clsname, (Proxy, self), dict(_enclosinginstance = enclosinginstance))
    Inner = InnerMeta('Inner', (cls,), {})
    return Inner

def singleton(t):
    'The decorated class is replaced with a no-arg instance.'
    return t()

@singleton
class outerzip:

    class Session:

        def __init__(self, iterables):
            self.iterators = [iter(i) for i in iterables]

        def row(self):
            self.validrow = len(self.iterators)
            for i in self.iterators:
                try:
                    yield next(i)
                except StopIteration:
                    self.validrow -= 1
                    yield

    def __call__(self, *iterables):
        session = self.Session(iterables)
        while True:
            values = tuple(session.row())
            if not session.validrow:
                break
            yield values

def enum(*lists):
    def d(cls):
        cls.enum = v = []
        for args in lists:
            obj = cls(*args)
            setattr(cls, args[0], obj)
            v.append(obj)
        return cls
    return d

def _rootcontext(e):
    while True:
        c = getattr(e, '__context__', None)
        if c is None:
            return e
        e = c

def invokeall(callables):
    '''Invoke every callable, even if one or more of them fail. This is mostly useful for synchronising with futures.
    If all succeeded return their return values as a list, otherwise raise all exceptions thrown as a chain.'''
    values = []
    failure = None
    for c in callables:
        try:
            obj = c()
        except Exception as e:
            _rootcontext(e).__context__ = failure
            failure = e
        else:
            values.append(obj)
    if failure is None:
        return values
    raise failure
