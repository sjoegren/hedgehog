"""
For development use.

Will update bash installer, README and some files.
"""
import importlib
import json
import logging
import sys
import pathlib
import re
import subprocess

import toml

import hedgehog
from . import Print, Error, META_FILE

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
    parser.add_argument(
        "--check-clean", action="store_true", help="Exit 1 if repo isn't clean."
    )
    args = parser.parse_args(argv)
    p = Print.instance(args.color)
    log_format = "{} {} {} %(message)s".format(
        p.colored("%(asctime)s", "magenta"),
        p.colored("%(levelname)s", "magenta"),
        p.colored("%(funcName)25s:", "yellow"),
    )
    return args, {"log_format": log_format}


def main(*, cli_args: str = None):
    args = hedgehog.init(
        _init,
        arguments=cli_args,
        logger=True,
        default_loglevel="INFO",
        argp_kwargs=dict(description=__doc__),
    )
    global log
    log = logging.getLogger("tool")
    if args.check_clean:
        if not repo_is_clean():
            sys.exit(1)
        return
    settings = toml.load(args.pyproject)
    log.debug_obj(settings, "pyproject settings")

    fail_dirty = False
    if not repo_is_clean() and not args.dryrun:
        fail_dirty = True
        args.dryrun = True

    update_installer(INSTALLER, settings, args)
    meta = get_metadata(settings, args)
    write_package_metadata(meta, args)
    write_readme(meta, settings["tool"]["poetry"]["readme"], args)
    update_package_version(meta, args)

    if fail_dirty:
        raise Error(
            "Did not write to any files since repo is dirty. "
            "Stash or commit any changes and try again."
        )


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
        log.debug("Write to %s: %r", filename, extra_content[-1])
    log.debug("New %s contents: %s", readme, extra_content)
    match = re.search(
        r"^<!-- following is automatically generated -->$", previous, flags=re.M
    )
    new = previous[: match.end() + 1] + "\n".join(extra_content) + "\n"
    if not args.dryrun:
        readme.write_text(new)
        log.info("Wrote back changes to %s", readme)


def write_package_metadata(meta, args):
    log.info("Metadata file: %s, exists: %s", META_FILE, META_FILE.exists())
    if not args.dryrun:
        with META_FILE.open("w") as metafile:
            json.dump(meta, metafile, indent=4)
        log.info("Wrote back changes to %s", META_FILE)


def update_package_version(meta, args):
    """Update __version__ in the main package."""
    pkgfile = pathlib.Path(hedgehog.__loader__.path)
    data = pkgfile.read_text()
    regex = re.compile(r'^(__version__ = )"(.+)"$', flags=re.M)
    old_version = regex.search(data).group(2)
    new, changes = regex.subn(rf'\1"{meta["version"]}"', data, count=1)
    if changes:
        log.info("Changed version %r -> %r", old_version, meta["version"])
        if not args.dryrun:
            pkgfile.write_text(new)
            log.info("Wrote back %d changes to %s", changes, pkgfile)


def repo_is_clean() -> bool:
    proc = subprocess.run(
        ["git", "status", "--porcelain=1", "-z"],
        check=True,
        capture_output=True,
        text=True,
    )
    out = proc.stdout.strip()
    rv = True
    for entry in out.split("\0"):
        if re.match(r"\w", entry[:2]):
            log.error("unclean repo: %s", entry)
            rv = False
    return rv


if __name__ == "__main__":
    try:
        main()
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)
