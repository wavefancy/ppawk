#!/usr/bin/env python3

"""

    An awk like python one line processor.
    @Author: Wallace Wang, wavefancy@gmail.com

    Usage:
        ppawk.py [-F <delim>] [-O <delim>] [-B <statement>] [-E <statement>] [--nc] [--cs <string>] [--co] [--ms int] [-u] [--xm] [-H] [-f <filter>] [<outexpr>]
        ppawk.py -h | --help | -v | --version | -f | --format

    Notes:
        1. Read from stdin and output to stdout.

    Options:
        <outexpr>      Output evaluation for each line, default as 'l' if not setted.
        -f <filter>    Test this filter expression before evaluating <outexpr>.
                         Only True of this filter will do the nexe evaluation.
                         The filter can be a python expression return true of false,
                         Or can be a regular expression pattern.

        -F <delim>     Input delimiter, default one or more whitespace,
                         call str.split(). tab for single tab separater.
        -O <delim>     Output delimiter, default tab.
        -H             Indicate the first line as header (except comments), do not apply -f filter.
        --co           Omit comment lines, default directly copy comment lines to stdout.
        --cs <string>  The start string for indicating comment line, default '#'.
        --nc           No Comments. Process all input data, do not treat any data as comment.
        --ms int       Split the input line by delimiter maxmium 'int' times.
                         The results array len(f) <= 'int' +1.
        --xm           Close the function for auto infer and load modules.
                         Python modules were auto-detected as: re.findall(r'([\w.]+)+(?=\.\w+)\b'
        -u             Do not auto-convert string to numerical.
        -B <statement> Begin statement.
        -E <statement> End statement.
        -h --help     Show this screen.
        -v --version  Show version.

"""
import sys
from docopt import docopt
from fastnumbers import fast_float,fast_int,fast_real
from signal import signal, SIGPIPE, SIG_DFL
import re

if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    # print(args)
    # sys.exit(-1)

    idelimiter = None #input delimiter
    if args['-F']:
        if args['-F'].lower() == 'tab':
            idelimiter = '\t'
        else:
            idelimiter = args['-F']

    if not args['<outexpr>']:
        args['<outexpr>'] = 'l'
    odelimiter          = args['-O']    if args['-O'] else '\t'
    begin_statement     = args['-B']    if args['-B'] else ''
    end_statement       = args['-E']    if args['-E'] else ''
    comment_start       = args['--cs']  if args['--cs'] else '#'
    copy_comments       = False         if args['--co'] else True
    filter_statement    = args['-f']    if args['-f'] else ''
    line_statement      = args['<outexpr>'].rsplit(';',maxsplit=1)
    line_action         = line_statement[0] if len(line_statement) == 2 else ''
    line_result         = line_statement[-1]
    auto_convert        = False         if args['-u'] else True
    without_header      = False         if args['-H'] else True
    NOT_all_data        = False         if args['--nc'] else True
    MAXMIUMSPLIT        = int(args['--ms']) if args['--ms'] else -1

    #auto import libraries.
    auto_load_modules = False if args['--xm'] else True
    #try auto-import modules dynamically, according statement.
    if auto_load_modules:
        modules = re.findall(r'([\w.]+)+(?=\.\w+)\b', args['<outexpr>']) + \
                re.findall(r'([\w.]+)+(?=\.\w+)\b', begin_statement) + \
                re.findall(r'([\w.]+)+(?=\.\w+)\b', filter_statement) + \
                re.findall(r'([\w.]+)+(?=\.\w+)\b', end_statement)

        for m in modules:
            try:
                cmd = '%s=__import__("%s")'%(m,m)
                exec(cmd)
            except:
                pass

    if begin_statement:
        exec(begin_statement)

    for line in sys.stdin:
        #deal with comment lines.
        if NOT_all_data and line.startswith(comment_start):
            if copy_comments:
                sys.stdout.write(line)
            continue

        l = line.strip()
        if not l:    #skip empty lines.
            continue

        nf = len(l)
        f = l.split(idelimiter,maxsplit=MAXMIUMSPLIT)
        if auto_convert:
            f = [fast_real(x) for x in f]
        # print(f)
        try:
            if filter_statement and without_header:
                if not eval(filter_statement):
                    continue
        except Exception as e:
            sys.stderr.write('ERROR at line:%s\n'%(l))
            sys.stderr.write(str(e))
            sys.exit(-1)

        # Evalute and output results.
        if line_action:
            exec(line_action)
        re = eval(line_result)
        #test whether the results is list or tuple
        out = odelimiter.join(map(str,re)) if isinstance(re, (list, tuple)) else re
        sys.stdout.write('%s\n'%(out))

        # header can only apply once.
        if without_header == False:
            without_header = True

    if end_statement:
        re = exec(end_statement)
        out = odelimiter.join(map(str,re)) if isinstance(re, (list, tuple)) else re
        sys.stdout.write('%s\n'%(out))

sys.stdout.flush()
sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
