#!/usr/bin/env python

"""

    An awk like python one line processor.
    @Author: wavefancy@gmail.com

    Usage:
        ppawk.py [-F <delim>] [-O <delim>] [-B <statement>] [-E <statement>] [--cs <string>] [--co] [-f <filter>] <outexpr>
        ppawk.py -h | --help | -v | --version | -f | --format

    Notes:
        1. Read from stdin and output to stdout.

    Options:
        <outexpr>      Output evaluation for each line.
        -f <filter>    Test this filter expression before evaluating <outexpr>.
                         Only True of this filter will do the nexe evaluation.
                         The filter can be a python expression return true of false,
                         Or can be a regular expression pattern.

        -F <delim>     Input delimiter, default one or more whitespace,
                         call str.split(). tab for single tab separater.
        -O <delim>     Output delimiter, default tab.
        --co           Omit comment lines, default directly copy comment lines to stdout.
        --cs <string>  The start string for indicating comment line, default '#'.
        -B <statement> Begin statement.
        -E <statement> End statement.
        -h --help     Show this screen.
        -v --version  Show version.

"""
import sys
from docopt import docopt
from fastnumbers import fast_float,fast_int
from signal import signal, SIGPIPE, SIG_DFL

if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    print(args)
    # sys.exit(-1)

    idelimiter = None #input delimiter
    if args['-F']:
        if args['-F'].lower() == 'tab':
            idelimiter = '\t'
        else:
            idelimiter = args['-F']

    odelimiter          = args['-O']    if args['-O'] else '\t'
    begin_statement     = args['-B']    if args['-B'] else ''
    end_statement       = args['-E']    if args['-E'] else ''
    comment_start       = args['--cs']  if args['--cs'] else '#'
    copy_comments       = False         if args['--co'] else True
    filter_statement    = args['-f']    if args['-f'] else ''
    line_statement      = args['<outexpr>'].rsplit(';',maxsplit=1)
    line_action         = line_statement[0] if len(line_statement) == 2 else ''
    line_result         = line_statement[-1]


    print(line_action)
    print(line_result)

    if begin_statement:
        exec(begin_statement)

    for line in sys.stdin:
        #deal with comment lines.
        if line.startswith(comment_start):
            if copy_comments:
                sys.stdout.write(line)
            continue

        l = line.strip()
        nf = len(l)
        f = [fast_float(x) for x  in l.split(idelimiter)]
        # print(f)

        if filter_statement:
            if not eval(filter_statement):
                continue

        # Evalute and output results.
        if line_action:
            exec(line_action)
        re = eval(line_result)
        #test whether the results is list or tuple
        out = odelimiter.join(map(str,re)) if isinstance(re, (list, tuple)) else re
        sys.stdout.write('%s\n'%(out))

    if end_statement:
        re = eval(end_statement)
        out = odelimiter.join(map(str,re)) if isinstance(re, (list, tuple)) else re
        sys.stdout.write('%s\n'%(out))

sys.stdout.flush()
sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
