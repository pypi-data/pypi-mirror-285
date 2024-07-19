'Interactive REPL.'
from .model import Stream
from .repl import Repl
from .scope import Scope
from .util import NoSuchPathException
import sys

assert NoSuchPathException

def main():
    scope = Scope()
    scope['stdout',] = Stream(sys.stdout)
    with Repl(scope, True) as repl:
        for line in sys.stdin:
            repl(line)

if '__main__' == __name__:
    main()
