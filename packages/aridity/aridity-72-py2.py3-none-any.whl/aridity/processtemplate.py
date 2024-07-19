'Process the given template to stdout using config from stdin.'
from .repl import Repl
import os, sys

def main():
    templatepath, = sys.argv[1:]
    with Repl() as repl:
        for line in sys.stdin:
            repl(line)
        repl.printf("< %s", os.path.abspath(templatepath))

if '__main__' == __name__:
    main()
