"""
Multiple diff formats - colorize intraline diffs.

* ndiff:    lists every line and highlights interline changes.
* context:  highlights clusters of changes in a before/after format.
* unified:  highlights clusters of changes in an inline format.
* html:     generates side by side comparison with change highlights.
"""

import difflib
import os
import sys

from datetime import datetime, timezone

from .. import init
from . import colordiff


def file_mtime(path):
    t = datetime.fromtimestamp(os.stat(path).st_mtime, timezone.utc)
    return t.astimezone().isoformat()


def _init(parser, argv: list, /):
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
        "-l",
        "--lines",
        type=int,
        default=3,
        help="Set number of context lines (default 3)",
    )
    parser.add_argument("fromfile")
    parser.add_argument("tofile")
    return parser.parse_args(argv)


def main():
    args = init(
        _init,
        argp_kwargs=dict(description=__doc__),
    )

    n = args.lines
    fromfile = args.fromfile
    tofile = args.tofile

    fromdate = file_mtime(fromfile)
    todate = file_mtime(tofile)
    with open(fromfile) as ff:
        fromlines = ff.readlines()
    with open(tofile) as tf:
        tolines = tf.readlines()

    if args.unified:
        diff = difflib.unified_diff(
            fromlines, tolines, fromfile, tofile, fromdate, todate, n=n
        )
    elif args.context:
        diff = difflib.context_diff(
            fromlines, tolines, fromfile, tofile, fromdate, todate, n=n
        )
    elif args.html:
        diff = difflib.HtmlDiff().make_file(
            fromlines, tolines, fromfile, tofile, context=args.c, numlines=n
        )
    else:
        diff_gen = difflib.ndiff(fromlines, tolines)
        diff = colordiff.color_diff_lines(diff_gen) if args.color else diff_gen

    sys.stdout.writelines(diff)


if __name__ == "__main__":
    main()
