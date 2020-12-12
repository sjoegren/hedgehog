"""
dirstack - keep a list of recently visited directories to choose from, invoke
with `ds` shell function.
"""
import argparse
import functools
import logging
import pathlib
import sys

from simple_term_menu import TerminalMenu

import hedgehog
from .dirstack import Dirstack
from .. import Error, Print

log = None
EXIT_NOOP = 3
EXIT_DELETED = 4


class DirstackException(Error):
    """Dirstack exceptions, not necessarily errors."""


def _init(parser, argv: list, /):
    parser.add_argument(
        "--add",
        metavar="DIR",
        help="Add path to dirstack",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete the dirstack file.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List current dirstack entries sorted on access time on stdout.",
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

    stack = Dirstack.load()
    if args.add:
        stack.add(args.add)
        stack.save()
        return
    if args.delete:
        stack.delete()
        return
    if args.list:
        for entry in stack.sorted():
            print("{} | {}".format(*entry))
        return

    ordered_entries = stack.sorted()
    menu_entries = [
        f"[{i + 1}] {e.time.isoformat(sep=' ', timespec='seconds')}  {e.path}"
        for i, e in enumerate(ordered_entries)
    ]
    options = [
        "[p] pop an entry",
        "[d] delete an entry",
        "[o] delete entries older than...",
        "[l] last visited directory",
    ]
    menu = functools.partial(TerminalMenu, show_search_hint=True)
    main_menu = menu(menu_entries + options)
    index = main_menu.show()

    if index is None:
        raise DirstackException("Nothing selected", retcode=EXIT_NOOP)

    try:
        entry = ordered_entries[index]
        log.debug("selected: %s", entry)
    except IndexError:  # one of the options after stack entries selected
        opt = index - len(ordered_entries)
        option = options[opt]

        if "last visited directory" in option:
            # Find first entry in list (sorted by visit time desc) that is not CWD
            for entry in ordered_entries:
                if entry.path != pathlib.Path.cwd():
                    stack.add(entry)
                    print(entry.path)
                    stack.save()
                    return
            else:
                raise DirstackException("No entry available", retcode=EXIT_NOOP)

        kwargs = {}
        if "older than" in option:
            kwargs["title"] = "Delete all entries from selected and older:"

        # Show menu of directories again, without the options
        selected_entry = menu(menu_entries, **kwargs).show()
        if selected_entry is None:
            raise DirstackException("Nothing selected", retcode=EXIT_NOOP)

        if "pop an entry" in option:
            entry = stack.pop(ordered_entries[selected_entry].path)
            print(entry.path)
        elif "delete an entry" in option:
            entry = stack.pop(ordered_entries[selected_entry].path)
            stack.save()
            raise DirstackException(f"Deleted: {entry.path}", retcode=EXIT_DELETED)
        elif "older than" in option:
            popped = []
            for entry in ordered_entries[selected_entry:]:
                log.info("delete %s", entry)
                popped.append(stack.pop(entry))
            stack.save()
            raise DirstackException(
                "\n".join((f"Deleted: {e.path}" for e in popped)), retcode=EXIT_DELETED
            )
        stack.save()
        return

    # re-add selected path entry to stack
    stack.add(entry)
    stack.save()

    print(entry.path)


def main_wrap():
    """Called from script created at package install."""
    try:
        main()
    except DirstackException as exc:
        print(str(exc))
        sys.exit(exc.retcode)
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)


if __name__ == "__main__":
    main_wrap()
