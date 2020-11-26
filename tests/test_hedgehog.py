import subprocess

import pytest

import hedgehog


def test_version():
    assert hedgehog.__version__ == "0.1.0"


def test_run_package_as_module_prints_version():
    proc = subprocess.run(
        ["python", "-m", "hedgehog"], check=True, capture_output=True, text=True
    )
    assert proc.stdout.strip() == hedgehog.__version__


@pytest.mark.parametrize(
    "name",
    [
        "hhdiff",
    ],
)
def test_installed_scripts(name):
    """Test that expected scripts can execute and report correct version."""
    proc = subprocess.run(
        [name, "--version"], check=True, capture_output=True, text=True
    )
    assert name in proc.stdout
    assert hedgehog.__version__ in proc.stdout


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
