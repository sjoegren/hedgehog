"""Command line interface to difflib.py providing diffs in four formats:

* ndiff:    lists every line and highlights interline changes.
* context:  highlights clusters of changes in a before/after format.
* unified:  highlights clusters of changes in an inline format.
* html:     generates side by side comparison with change highlights.

"""

import difflib
import os
import sys

from datetime import datetime, timezone

from .. import argument_parser
from . import colordiff


def file_mtime(path):
    t = datetime.fromtimestamp(os.stat(path).st_mtime, timezone.utc)
    return t.astimezone().isoformat()


def main():
    parser = argument_parser(description=__doc__)
    parser.add_argument(
        "-c",
        "--context",
        action="store_true",
        help="Produce a context format diff (default)",
    )
    parser.add_argument(
        "-u", "--unified", action="store_true", help="Produce a unified format diff"
    )
    parser.add_argument(
        "-m",
        "--html",
        action="store_true",
        help="Produce HTML side by side diff " "(can use -c and -l in conjunction)",
    )
    parser.add_argument(
        "-n", "--ndiff", action="store_true", help="Produce a ndiff format diff"
    )
    parser.add_argument(
        "--no-color",
        "-C",
        action="store_false",
        dest="color",
        help="Disable color output for --ndiff format",
    )
    parser.add_argument(
        "-l",
        "--lines",
        type=int,
        default=3,
        help="Set number of context lines (default 3)",
    )
    parser.add_argument("fromfile")
    parser.add_argument("tofile")
    options = parser.parse_args()

    n = options.lines
    fromfile = options.fromfile
    tofile = options.tofile

    fromdate = file_mtime(fromfile)
    todate = file_mtime(tofile)
    with open(fromfile) as ff:
        fromlines = ff.readlines()
    with open(tofile) as tf:
        tolines = tf.readlines()

    if options.unified:
        diff = difflib.unified_diff(
            fromlines, tolines, fromfile, tofile, fromdate, todate, n=n
        )
    elif options.context:
        diff = difflib.context_diff(
            fromlines, tolines, fromfile, tofile, fromdate, todate, n=n
        )
    elif options.html:
        diff = difflib.HtmlDiff().make_file(
            fromlines, tolines, fromfile, tofile, context=options.c, numlines=n
        )
    else:
        diff_gen = difflib.ndiff(fromlines, tolines)
        diff = colordiff.color_diff_lines(diff_gen) if options.color else diff_gen

    sys.stdout.writelines(diff)


if __name__ == "__main__":
    main()
