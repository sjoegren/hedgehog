import logging
import pytest
import re
import subprocess

import hedgehog


@pytest.mark.parametrize(
    "name",
    [
        "hhdiff",
        "sshansible",
        "dirstack",
        "git-rmb",
        "hedgehog",
    ],
)
def test_installed_scripts(name):
    """Test that expected scripts can execute and report correct version."""
    proc = subprocess.run(
        [name, "--version"], check=True, capture_output=True, text=True
    )
    assert re.search(rf"^{name} \d+\.\d+\.\d+", proc.stdout, re.M)


@pytest.mark.parametrize(
    "args, expected",
    [
        (("hello world",), "hello world"),
        (("hello my %d pals %s, %s", 2, "foo", "bar"), "hello my 2 pals foo, bar"),
    ],
)
def test_error_exception_format(args, expected):
    assert str(hedgehog.Error(*args)) == expected


def test_error_exception_retcode():
    assert hedgehog.Error("foo", retcode=2).retcode == 2


def test_init():
    args = hedgehog.init(
        lambda p, v: p.parse_args(v),
        arguments="-vv --no-color",
        logger=True,
        default_loglevel="CRITICAL",
        argp_kwargs=dict(description="test text", prog="test"),
    )
    assert hedgehog.CACHE_DIR.is_dir()
    assert args.verbose == 2
    assert args.color is False
    assert logging.getLogger().getEffectiveLevel() == logging.WARNING
