'Print given config (with optional path in config) as shell snippet.'
from .model import Boolean, Entry, Locator, Number, Text
from .scope import Scope
import os, sys

def _configpath(configname):
    if os.sep in configname:
        return configname
    for parent in os.environ['PATH'].split(os.pathsep):
        path = os.path.join(parent, configname)
        if os.path.exists(path):
            return path
    raise Exception("Not found: %s" % configname)

def _scopetobash(self, toplevel = False):
    if toplevel:
        return ''.join("%s=%s\n" % (name, obj.resolve(self).tobash()) for name, obj in self.resolvables.items())
    if self.islist:
        return "(%s)" % ' '.join(x.resolve(self).tobash() for _, x in self.resolvables.items())
    return Text(self.tobash(True)).tobash()

Scope.tobash = _scopetobash
Boolean.tobash = lambda self, toplevel: 'true' if self.booleanvalue else 'false'
Number.tobash = lambda self: str(self.numbervalue)
Text.tobash = lambda self: "'%s'" % self.textvalue.replace("'", r"'\''")

def main():
    scope = Scope()
    Locator(_configpath(sys.argv[1])).source(scope, Entry([]))
    sys.stdout.write(scope.resolved(*sys.argv[2:]).tobash(True))

if '__main__' == __name__:
    main()
