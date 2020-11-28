import argparse
import os
import pathlib
import shlex
import sys

import termcolor

__version__ = "0.1.0"

CACHE_DIR = pathlib.Path.home() / ".cache/hedgehog"


class Error(Exception):
    """Exceptions originating from Hedgehog toolset."""

    def __init__(self, /, message, *args, retcode=1):
        self._message = message
        self._args = args
        self.retcode = retcode
        super().__init__(message, *args)

    def __str__(self):
        return self._message % self._args


class Print:
    """Instantiate a printer with color on/off, which is used for subsequent
    print calls."""

    _instance = None

    def __init__(self, color):
        self.color = color
        self._last_color = None
        self._last_attrs = None

    @classmethod
    def instance(cls, color=False):
        """Create and return a single instance."""
        if not cls._instance:
            cls._instance = cls(color)
        return cls._instance

    def __call__(self, string, /, color=None, *, attrs=None, reset=False, **kwargs):
        if self.color:
            if reset:
                self._last_color = None
                self._last_attrs = None
            if color:
                self._last_color = color
            else:
                color = self._last_color
            if attrs:
                self._last_attrs = attrs
            else:
                attrs = self._last_attrs
            termcolor.cprint(string, color=color, attrs=attrs, **kwargs)
        else:
            print(string, **kwargs)


def init_args(**kwargs):
    """Initialize an ArgumentParser with a "cache_dir" attribute."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, **kwargs
    )
    parser.set_defaults(cache_dir=CACHE_DIR)
    py_version = ".".join((str(x) for x in sys.version_info[:3]))
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}\nPython: {py_version} from {sys.exec_prefix}",
    )
    parser.add_argument(
        "--color",
        action=argparse.BooleanOptionalAction,
        default=os.isatty(0),
    )
    return parser


def init_wrap(func, /, args):
    """Call func and return it's return value, with a argv type list if args is
    a string of arguments."""
    if args is not None:
        return func(shlex.split(args))
    return func()
