"""
fzfdirs - print bookmarked directories to feed to fzf.

Shell function `cdg` opens fzf with the list of bookmarks and cd to the selected path.
`cdg -e` to open bookmarks file in $EDITOR.
"""
import argparse
import logging
import os
import sys

import hedgehog
from . import bookmarks
from .. import Error, Print

log = None
EXIT_NOOP = 3
EXIT_DELETED = 4
BOOKMARK_FILE = hedgehog.CONFIG_DIR / "bookmarks.yaml"


class DirsException(Error):
    """Dirs exceptions, not necessarily errors."""


def _init(parser, argv: list, /):
    parser.add_argument(
        "--file",
        default=str(BOOKMARK_FILE),
        help="Bookmarks file (default: %(default)s)",
    )
    parser.add_argument(
        "-e",
        "--edit",
        action="store_true",
        help="Edit bookmarks file",
    )
    parser.add_argument(
        "--bookmark",
        metavar="DIR",
        help="Add bookmark",
    )
    parser.add_argument("--dryrun", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    return args


def main(*, cli_args: str = None):
    global log
    args = hedgehog.init(
        _init,
        arguments=cli_args,
        logger=True,
        argp_kwargs=dict(description=__doc__),
        default_loglevel="WARNING",
    )
    log = logging.getLogger(args.prog_name)
    log.debug(args)

    bm = bookmarks.Bookmarks(args.file)
    log.info("bookmarks: %s", bm)

    if args.edit:
        editor = os.environ.get("EDITOR", "vim")
        os.execlp(editor, editor, args.file)

    if not bm:
        raise DirsException("There are no bookmarks yet. --edit opens file in editor.")

    for fmt in bm.formatted():
        print(fmt)


def main_wrap():
    try:
        main()
    except DirsException as exc:
        Print.instance()(f"{exc}", color="yellow", file=sys.stderr)
        sys.exit(exc.retcode)
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red", file=sys.stderr)
        sys.exit(exc.retcode)


if __name__ == "__main__":
    main_wrap()
