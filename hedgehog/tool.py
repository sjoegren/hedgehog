"""
For development use.

Will update bash installer, README and some files.
"""
import argparse
import importlib
import json
import logging
import sys
import pathlib
import re
import subprocess

import toml

from . import init, Print, Error, META_FILE

PROJECT_FILE = pathlib.Path.cwd() / "pyproject.toml"
INSTALLER = pathlib.Path.cwd() / "install-hedgehog.bash"
cprint = None
log = None


def _init(parser, argv: list, /):
    parser.add_argument(
        "-n", "--dryrun", action="store_true", help="Don't write any changes."
    )
    parser.add_argument(
        "--pyproject",
        metavar="FILE",
        type=pathlib.Path,
        default=PROJECT_FILE,
        help=f"Default: {PROJECT_FILE}",
    )
    args = parser.parse_args(argv)
    return args


def main(*, cli_args: str = None):
    args = init(
        _init,
        arguments=cli_args,
        logger=True,
        default_loglevel="INFO",
        argp_kwargs=dict(description=__doc__),
    )
    global log
    log = logging.getLogger("tool")
    settings = toml.load(args.pyproject)
    log.debug_obj(settings, "pyproject settings")
    check_repo_status(args)
    update_installer(INSTALLER, settings, args)
    meta = get_metadata(settings, args)
    write_package_metadata(meta, args)
    write_readme(meta, settings["tool"]["poetry"]["readme"], args)


def update_installer(installer_path, settings, args):
    data = installer_path.read_text()
    # Update minimum Python version to match pyproject settings
    match = re.search(
        r"(\d+)\.(\d+)", settings["tool"]["poetry"]["dependencies"]["python"]
    )
    if not match:
        raise Error("couldn't find python version in settings")
    log.info("Python version configured in project: %s", match.group(0))
    data, changes = re.subn(
        r"^(MIN_VERSION_MINOR=)\d+", rf"\g<1>{match[2]}", data, 1, re.M
    )
    if changes:
        log.info("Updated Python version to %s", match.group(0))

    # Update package git url with checked out branch
    proc = subprocess.run(
        ["git", "branch", "--show-current"], check=True, capture_output=True, text=True
    )
    branch = proc.stdout.strip()
    branch = "" if branch == "main" else f"@{branch}"
    data, changes = re.subn(
        r'^(PACKAGE=".+\.git).*(#egg.*")', rf"\g<1>{branch}\g<2>", data, 1, re.M
    )
    if changes:
        log.info("Updated package git url with branch '%s'", branch)

    if not args.dryrun:
        installer_path.write_text(data)
        log.info("Wrote back changes to %s", installer_path)


def get_metadata(settings, args):
    meta = {"scripts": {}}
    for key in ("name", "version", "description", "repository"):
        meta[key] = settings["tool"]["poetry"][key]
    for name, path in settings["tool"]["poetry"]["scripts"].items():
        modpath = path.split(":")[0]
        module = importlib.import_module(modpath)
        description = module.__doc__.strip()
        brief = re.split(r'\.[\s"]', description, maxsplit=1)[0].replace("\n", " ")
        log.info("%s: %s", name, brief)
        meta["scripts"][name] = {"brief": brief, "description": description}
    return meta


def write_readme(meta, filename, args):
    readme = pathlib.Path(filename)
    previous = readme.read_text()
    extra_content = []
    for name in sorted(meta["scripts"]):
        extra_content.append(f"* `{name}`: {meta['scripts'][name]['brief']}")
    log.debug("New %s contents: %s", readme, extra_content)
    new, changes = re.subn(
        r"<!-- following is automatically generated -->",
        "\\g<0>\n" + "\n".join(extra_content),
        previous,
        count=1,
    )
    log.info("%s changes: %d", filename, changes)

    if not args.dryrun:
        readme.write_text(new)
        log.info("Wrote back changes to %s", readme)


def write_package_metadata(meta, args):
    log.info("Metadata file: %s, exists: %s", META_FILE, META_FILE.exists())
    if not args.dryrun:
        with META_FILE.open("w") as metafile:
            json.dump(meta, metafile)
        log.info("Wrote back changes to %s", META_FILE)


def check_repo_status(args):
    proc = subprocess.run(
        ["git", "status", "--porcelain=1", "-z"],
        check=True,
        capture_output=True,
        text=True,
    )
    out = proc.stdout.strip()
    for entry in out.split("\0"):
        if re.match(r"\w", entry[:2]):
            log.error("unclean repo: %s", entry)
            if not args.dryrun:
                raise Error(
                    "Will not write to any files while repo is dirty. "
                    "Stash or commit any changes and try again."
                )


if __name__ == "__main__":
    try:
        main()
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)
