from .model import Stream, Text
from .search import resolvedscopeornone
import os, sys

class Precedence:

    void, = range(-1, 0)
    default, colon = range(2)

    @classmethod
    def ofdirective(cls, d):
        return getattr(d, 'precedence', cls.default)

lookup = {}

def _directive(cls):
    obj = cls()
    lookup[Text(cls.name)] = obj
    return obj

@_directive
class Colon:
    'Ignore rest of logical line.'
    name = ':'
    precedence = Precedence.colon
    def __call__(self, prefix, suffix, scope):
        scope.execute(prefix, True)

@_directive
class Redirect:
    name = '!redirect'
    def __call__(self, prefix, suffix, scope):
        scope['stdout',] = Stream(suffix.tophrase().resolve(scope).openable(scope).open(True))

@_directive
class Write:
    name = '!write'
    def __call__(self, prefix, suffix, scope):
        scope.resolved('stdout').flush(suffix.tophrase().resolve(scope).cat())

@_directive
class Source:
    'Include path or resource at prefix.'
    name = '.'
    def __call__(self, prefix, suffix, scope):
        # XXX: Use full algo to get phrasescope?
        phrasescope = scope
        for word in prefix.topath(scope):
            s = resolvedscopeornone(phrasescope, [word])
            if s is None:
                break
            phrasescope = s
        suffix.tophrase().resolve(phrasescope).openable(phrasescope).source(scope, prefix)

@_directive
class CD:
    name = '!cd'
    def __call__(self, prefix, suffix, scope):
        scope['cwd',] = suffix.tophrase().resolve(scope).openable(scope)

@_directive
class Test:
    name = '!test'
    def __call__(self, prefix, suffix, scope):
        sys.stderr.write(str(suffix.tophrase().resolve(scope)))
        sys.stderr.write(os.linesep)

@_directive
class Equals:
    'Assign expression to path.'
    name = '='
    def __call__(self, prefix, suffix, scope):
        scope[prefix.topath(scope)] = suffix.tophrase()

@_directive
class ColonEquals:
    'Evaluate expression and assign result to path.'
    name = ':='
    def __call__(self, prefix, suffix, scope):
        path = prefix.topath(scope)
        scope[path] = suffix.tophrase().resolve(scope.getorcreatesubscope(path[:-1]))

@_directive
class PlusEquals:
    'Assign expression to prefix plus an opaque key, i.e. add to list.'
    name = '+='
    def __call__(self, prefix, suffix, scope):
        from .functions import OpaqueKey
        phrase = suffix.tophrase()
        scope[prefix.topath(scope) + (OpaqueKey(),)] = phrase

@_directive
class Cat:
    name = '<'
    def __call__(self, prefix, suffix, scope):
        scope = scope.getorcreatesubscope(prefix.topath(scope))
        scope.resolved('stdout').flush(suffix.tophrase().resolve(scope).openable(scope).processtemplate(scope))
