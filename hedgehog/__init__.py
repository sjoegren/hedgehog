import argparse
import json
import logging
import os
import pathlib
import shlex
import sys

from typing import Callable, Union

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

    @classmethod
    def instance(cls, color=False):
        """Create and return a single instance."""
        if not cls._instance:
            cls._instance = cls(color)
        return cls._instance

    def __call__(self, string, /, color=None, *, attrs=None, **kwargs):
        if self.color:
            termcolor.cprint(str(string), color=color, attrs=attrs, **kwargs)
        else:
            print(string, **kwargs)

    def colored(self, string, /, color=None, *, attrs=None):
        if self.color:
            return termcolor.colored(string, color=color, attrs=attrs)
        return string


class Logger(logging.getLoggerClass()):

    _level_colors = {
        "CRITICAL": "red",
        "ERROR": "red",
        "WARNING": "yellow",
        "INFO": "blue",
        "DEBUG": "green",
    }

    def __init__(self, name):
        super().__init__(name)

    def debug_obj(self, obj, msg, *args, level=logging.DEBUG, **kwargs):
        if getattr(self.root, "_hedgehog_debug", False) or level > logging.DEBUG:
            data = json.dumps(obj, indent=4)
            if getattr(self.root, "_color", False):
                data = termcolor.colored(data, "green")
            self.log(level, msg + ". data:\n%s", *args, data, **kwargs)

    # color each levelname in different colors
    # def makeRecord(self, *args, **kwargs):
    #     rv = super().makeRecord(*args, **kwargs)
    #     if getattr(self.root, "_color", False):
    #         rv.levelname = termcolor.colored(
    #             rv.levelname, self._level_colors[rv.levelname]
    #         )
    #     return rv


def _argument_parser(logger: bool, argp_kwargs: dict):
    """Initialize an ArgumentParser with a "cache_dir" attribute."""
    argp_kwargs.setdefault("formatter_class", argparse.RawDescriptionHelpFormatter)
    par = argparse.ArgumentParser(**argp_kwargs)
    py_version = ".".join((str(x) for x in sys.version_info[:3]))
    par.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}\nPython: {py_version} from {sys.exec_prefix}",
    )
    par.add_argument(
        "--color",
        action=argparse.BooleanOptionalAction,
        default=os.isatty(0),
    )
    if logger:
        par.set_defaults(log_level=0)
        par.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="Increase verbosity level.",
        )
        par.add_argument("--debug", action="store_true", help="Extra debug output.")
    return par


def init(
    hook_func: Callable[[argparse.ArgumentParser, list], argparse.Namespace],
    /,
    *,
    arguments: str = None,
    logger=False,
    argp_kwargs: dict = {},
    default_loglevel: Union[int, str] = "INFO",
    log_format_date=False,
) -> argparse.Namespace:
    """Initialize ArgumentParser and logging.

    Create an ArgumentParser with default options.

    Args:
        hook_func: A callable `func(parser, argv, /)` which is passed the
        ArgumentParser instance and argv which should be passed to
        `parser.parse_args()`. hook_func must return the Namespace returned by
        parse_args.

        arguments: String with shell arguments to the program.

        argp_kwargs: Keyword argument to pass to ArgumentParser().

        logger: Whether a logger instance should be initialized.

    Returns:
        The same Namespace instance that hook_func returns.
    """
    argv = sys.argv[1:] if arguments is None else shlex.split(arguments)
    parser = _argument_parser(logger, argp_kwargs)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    parser.set_defaults(cache_dir=CACHE_DIR)
    parser.set_defaults(log=None)
    args = hook_func(parser, argv)

    # Instantiate a Print object.
    p = Print.instance(args.color)

    # Adjust log level according to repeat of -v
    if logger:
        try:
            default = getattr(logging, default_loglevel)
        except TypeError:
            default = default_loglevel
        args.log_level = max(default - args.verbose * 10, logging.DEBUG)

        logging.setLoggerClass(Logger)
        log = logging.getLogger()
        log.setLevel(args.log_level)
        ch = logging.StreamHandler()
        ch.setLevel(args.log_level)
        datefmt = "{}%H:%M:%S".format("%Y-%m-%d" if log_format_date else "")

        if args.log_level == logging.DEBUG:
            fmt = logging.Formatter(
                "{} {} [{}{}{}] {} %(message)s".format(
                    p.colored("%(asctime)s", "magenta"),
                    p.colored("%(name)s", "yellow"),
                    p.colored("%(filename)s", "blue"),
                    p.colored(":%(lineno)s", "red"),
                    p.colored(":%(funcName)s", "yellow"),
                    p.colored("%(levelname)s:", "magenta"),
                ),
                datefmt,
            )
        else:
            fmt = logging.Formatter(
                "{} {} %(message)s".format(
                    p.colored("%(asctime)s", "magenta"),
                    p.colored("%(levelname)s:", "magenta"),
                ),
                datefmt,
            )
        ch.setFormatter(fmt)
        log.addHandler(ch)
        log._hedgehog_debug = args.debug
        log._color = args.color
        args.root_logger = log
        log.debug("Logging initialized. Args: %s", args)

    return args
