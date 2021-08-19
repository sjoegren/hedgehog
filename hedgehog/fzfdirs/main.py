"""
fzfdirs - print bookmarked directories to feed to fzf.

Shell function `cdg` opens fzf with the list of bookmarks and cd to the selected path.
`cdg -e` to open bookmarks file in $EDITOR.
"""
import argparse
import logging
import os
import pathlib
import sys

import hedgehog
from . import bookmarks
from .. import Error, Print

log = None
EXIT_NOOP = 3
EXIT_DELETED = 4
BOOKMARK_FILE = hedgehog.CONFIG_DIR / "bookmarks.yaml"
RECENTLY_USED_FILE = hedgehog.CACHE_DIR / "fzfdirs-recent.yaml"


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
        "--add-recent",
        metavar="PATH",
        help="Add %(metavar)s to recently used file",
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
    recent = bookmarks.RecentlyUsed(RECENTLY_USED_FILE)

    if args.edit:
        editor = os.environ.get("EDITOR", "vim")
        os.execlp(editor, editor, args.file)
    elif args.add_recent:
        path = pathlib.Path(args.add_recent)
        if not path.is_absolute():
            path = pathlib.Path.home() / path
        if path in bm:
            recent.add(path.as_posix())
        else:
            log.info("%s is not in bookmarks, skip adding to recent paths list", path)
        return

    if not bm:
        raise DirsException("There are no bookmarks yet. --edit opens file in editor.")

    for fmt in bm.sorted_formatted(recent):
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
