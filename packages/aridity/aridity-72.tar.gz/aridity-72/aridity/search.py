from .util import popattr, UnparseNoSuchPathException
from collections import namedtuple
from itertools import islice
import heapq

def scopedepths(scope):
    scopes = [scope]
    while scopes:
        nextscopes = []
        for s in scopes:
            nextscopes.extend(s.parents)
        yield scopes
        scopes = nextscopes

def resolvedscopeornone(s, path):
    for name in path:
        r = s.resolvableornone(name)
        if r is None:
            return
        s = r.resolve(s)
        if not hasattr(s, 'resolvableornone'):
            return
    return s

class Hit(namedtuple('BaseHit', 'revdepths scope resolvable')):

    def iterornone(self, word):
        contextscope = self.resolvable.resolve(self.scope) # XXX: Wise?
        if hasattr(contextscope, 'resolvableornone'):
            return Iterator(self.revdepths, contextscope, word)

    def shortcut(self, zerocount):
        return all(not d for d in islice(self.revdepths, None, zerocount))

class Iterable:

    def __iter__(self):
        return self.popiterator()

class Iterator(Iterable):

    def __init__(self, revdepths, contextscope, word):
        def g():
            for depth, scopes in enumerate(scopedepths(contextscope)):
                for scope in scopes:
                    resolvable = scope.resolvableornone(word)
                    if resolvable is not None:
                        yield Hit([depth] + revdepths, scope, resolvable)
        self.iterator = g()

    def next(self):
        return next(self.iterator)

    def popiterator(self):
        return popattr(self, 'iterator')

class Merge(Iterable):

    def __init__(self):
        self.iterables = []

    def add(self, iterable):
        self.iterables.append(iterable)

    def popiterator(self):
        return heapq.merge(*popattr(self, 'iterables'))

class Sump:

    besthit = None

    def add(self, iterable):
        pass

    def offer(self, hit):
        if self.besthit is None or hit.revdepths < self.besthit.revdepths:
            self.besthit = hit

    def __iter__(self):
        if self.besthit is not None:
            yield self.besthit

class Query:

    def __init__(self, path):
        assert path
        self.path = path

    def search(self, scope):
        root = Iterator([], scope, self.path[0])
        size = len(self.path)
        if 1 == size:
            for hit in root:
                return hit
        else:
            merges = [root]
            for _ in range(size - 2):
                merges.append(Merge())
            sump = Sump()
            merges.append(sump)
            for cursor, merge in enumerate(merges):
                xs = range(cursor + 1, size)
                for hit in sump:
                    if hit.shortcut(len(xs)):
                        return hit
                for hit in merge:
                    for x in xs:
                        i = hit.iterornone(self.path[x])
                        if i is None:
                            break
                        try:
                            hit = i.next()
                        except StopIteration:
                            break
                        merges[x].add(i)
                    else:
                        if hit.shortcut(len(xs)):
                            return hit
                        sump.offer(hit)
        raise UnparseNoSuchPathException(self.path)

def slices(path):
    n = len(path)
    for k in range(n)[::-1]:
        for start in range(n - k):
            v = path[start:start + k]
            yield v
            if not v:
                return
