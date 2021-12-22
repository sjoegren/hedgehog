"""
git lstree - Print a tree of files from ls-files
"""
import argparse
import logging
import pathlib
import sys

import hedgehog
from .. import Error, Print
from . import common

log = None
ls_files_args = None


def _init(parser, argv: list, /):
    parser.add_argument("--dryrun", action="store_true", help=argparse.SUPPRESS)
    global ls_files_args
    args, ls_files_args = parser.parse_known_args(argv)
    return args


def main(*, cli_args: str = None):
    global log
    args = hedgehog.init(
        _init,
        arguments=cli_args,
        logger=True,
        argp_kwargs=dict(description=__doc__),
    )
    log = logging.getLogger(args.prog_name)
    log.debug(args)
    out = common.git_command("ls-files", "-z", *ls_files_args)
    filetree = paths_to_tree(pathlib.Path(f) for f in out.split("\0"))
    print_tree(filetree)


def print_tree(tree, level=0):
    printer = Print.instance()
    if not tree:
        return
    indent = "  " * level
    for path, subtree in tree.items():
        if subtree:
            printer("{}{}/".format(indent, path), color="blue")
            print_tree(subtree, level + 1)
        else:
            printer("{}{}".format(indent, path))


def paths_to_tree(paths) -> dict:
    """Return a dict with a tree from iterable paths.

    Example:
        >>> paths = ['foo', 'bar', 'bar/a/x', 'bar/a/y', 'bar/b']
        >>> paths_to_tree(map(pathlib.Path, paths))
        {'foo': {}, 'bar': {'a': {'x': {}, 'y': {}}, 'b': {}}}

    """
    tree = {}
    for p in paths:
        _update_tree(tree, p.parts)
    return tree


def _update_tree(tree: dict, parts: tuple):
    if not parts:
        return
    branch = tree.setdefault(parts[0], {})
    _update_tree(branch, parts[1:])


def main_wrap():
    try:
        main()
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)


if __name__ == "__main__":
    main_wrap()
