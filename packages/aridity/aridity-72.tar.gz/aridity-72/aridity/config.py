from .functions import OpaqueKey
from .model import Entry, Function, Locator, Number, Resource, Scalar, Stream, Text, wrap
from .repl import Repl
from .scope import Scope
from .search import resolvedscopeornone
from .util import CycleException, dotpy, NoSuchPathException, qualname, selectentrypoints, solo
from functools import partial
from itertools import chain
from parabject import Parabject, register
import errno, logging, os, sys

log = logging.getLogger(__name__)

def _newnode(configcls, ctrl):
    node = configcls()
    register(ctrl, node)
    return node

def _processmainfunction(mainfunction):
    module = mainfunction.__module__
    if '__main__' == module:
        p = sys.argv[0]
        name = os.path.basename(p)
        if '__main__.py' == name:
            stem = os.path.basename(os.path.dirname(p))
        else:
            assert name.endswith(dotpy)
            stem = name[:-len(dotpy)]
        assert '-' not in stem
        appname = stem.replace('_', '-')
    else:
        attr = qualname(mainfunction)
        # FIXME: Requires metadata e.g. egg-info in projects that have not been installed:
        appname, = (ep.name for ep in selectentrypoints('console_scripts') if ep.module == module and ep.attr == attr)
    return module, appname

class ForeignScopeException(Exception):
    'The operation required a scope at precisely the given path.'

def _wrappathorstream(pathorstream):
    return (Stream if getattr(pathorstream, 'readable', lambda: False)() else Locator)(pathorstream)

class ConfigCtrl:
    'High level scope API.'

    @classmethod
    def _of(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @property
    def r(self):
        'Get config object for reading, i.e. missing scopes will error.'
        return _newnode(RConfig, self)

    @property
    def w(self):
        'Get config object for writing, i.e. missing scopes will be created.'
        return _newnode(WConfig, self)

    def __init__(self, basescope = None, prefix = None):
        self.node = _newnode(Config, self)
        self.basescope = Scope() if basescope is None else basescope
        self.prefix = [] if prefix is None else prefix

    def loadappconfig(self, mainfunction, moduleresource, encoding = 'ascii', settingsoptional = False):
        'Using app name as prefix load config from the given resource, apply user settings, and return config object for app. Context module for loading resource and the app name are deduced from `mainfunction`, or these can be provided as a tuple. Set `settingsoptional` to suppress the usual error if ~/.settings.arid does not exist.'
        try:
            module_name, appname = mainfunction
        except TypeError:
            module_name, appname = _processmainfunction(mainfunction)
        appconfig = self._loadappconfig(appname, Resource(module_name, moduleresource, encoding))
        try:
            self.loadsettings()
        except (IOError, OSError) as e:
            if not (settingsoptional and errno.ENOENT == e.errno):
                raise
            log.info("No such file: %s", e)
        return appconfig

    def _loadappconfig(self, appname, resource):
        resource.source(self.basescope.getorcreatesubscope(self.prefix + [appname]), Entry([]))
        return getattr(self.node, appname)

    def reapplysettings(self, mainfunction):
        if hasattr(mainfunction, 'encode'):
            appname = mainfunction
        else:
            _, appname = _processmainfunction(mainfunction)
        s = self.scope(True).duplicate()
        s.label = Text(appname)
        p = solo(s.parents)
        p[appname,] = s
        parent = self._of(p)
        parent.loadsettings()
        return getattr(parent.node, appname)

    def printf(self, template, *args):
        with Repl(self.basescope) as repl:
            repl.printf(''.join(chain(("%s " for _ in self.prefix), [template])), *chain(self.prefix, args))

    def load(self, pathorstream):
        'Execute config from the given path or stream.'
        s = self.scope(True)
        _wrappathorstream(pathorstream).source(s, Entry([]))

    def loadsettings(self):
        self.load(os.path.join(os.path.expanduser('~'), '.settings.arid'))

    def repl(self):
        assert not self.prefix # XXX: Support prefix?
        return Repl(self.basescope)

    def execute(self, text):
        'Execute given config text.'
        with self.repl() as repl:
            for line in text.splitlines():
                repl(line)

    def put(self, *path, **kwargs):
        def pairs():
            for t, k in [
                    [Function, 'function'],
                    [Number, 'number'],
                    [Scalar, 'scalar'],
                    [Text, 'text'],
                    [lambda x: x, 'resolvable']]:
                try:
                    yield t, kwargs[k]
                except KeyError:
                    pass
        # XXX: Support combination of types e.g. slash is both function and text?
        factory, = (partial(t, v) for t, v in pairs())
        self.basescope[tuple(self.prefix) + path] = factory()

    def scope(self, strict = False):
        if strict:
            s = resolvedscopeornone(self.basescope, self.prefix)
            if s is None:
                raise ForeignScopeException
            return s
        return self.basescope.resolved(*self.prefix) # TODO: Test what happens if it changes.

    def __iter__(self): # TODO: Add API to get keys without resolving values.
        'Yield keys and values.'
        for k, o in self.scope().resolveditems():
            try:
                yield k, o.scalar
            except AttributeError:
                yield k, self._of(self.basescope, self.prefix + [k]).node

    def processtemplate(self, frompathorstream, topathorstream):
        'Evaluate expression from path/stream and write result to path/stream.'
        s = self.scope()
        text = _wrappathorstream(frompathorstream).processtemplate(s)
        if getattr(topathorstream, 'writable', lambda: False)():
            topathorstream.write(text)
        else:
            with open(topathorstream, 'w') as g:
                g.write(text)

    def freectrl(self):
        return self._of(self.scope()) # XXX: Strict?

    def childctrl(self):
        return self._of(self.scope(True).createchild())

    def addname(self, name):
        return self._of(self.basescope, self.prefix + [name])

    def resolve(self):
        return self.basescope.resolved(*self.prefix)

class Config(Parabject):

    def __getattr__(self, name):
        ctrl = -self
        path = ctrl.prefix + [name]
        try:
            obj = ctrl.basescope.resolved(*path) # TODO LATER: Guidance for how lazy non-scalars should be in this situation.
        except (CycleException, NoSuchPathException): # XXX: Should this really translate CycleException?
            raise AttributeError(' '.join(path))
        try:
            return obj.scalar
        except AttributeError:
            return ctrl._of(ctrl.basescope, path).node

    def __iter__(self):
        for _, o in -self:
            yield o

    def __setattr__(self, name, value):
        (-self).scope(True)[name,] = wrap(value)

class RConfig(Parabject):

    def __getattr__(self, name):
        query = (-self).addname(name)
        try:
            obj = query.resolve()
        except NoSuchPathException:
            raise AttributeError
        try:
            return obj.scalar
        except AttributeError:
            return query.r

    def __iter__(self):
        'Yield values only. Iterate over `-self` for keys and values.'
        for _, o in (-self).scope().resolveditems(): # TODO: Investigate how iteration should work.
            yield o.scalar

class WConfig(Parabject):

    def __getattr__(self, name):
        return (-self).addname(name).w

    def __setattr__(self, name, value):
        query = (-self).addname(name)
        query.basescope[tuple(query.prefix)] = wrap(value)

    def __iadd__(self, value):
        query = (-self).addname(OpaqueKey())
        query.basescope[tuple(query.prefix)] = wrap(value)
        return self
