import argparse
import sys
import pathlib
from os.path import basename

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
    return parser
