import argparse
import sys
from os.path import basename

__version__ = "0.1.0"


def version_string():
    return f"{basename(sys.argv[0])} {__version__}"


def argument_parser(**kwargs):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, **kwargs
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser
