import pathlib
import pickle
import pytest
import time

from unittest.mock import Mock

from hedgehog.dirstack import dirstack


@pytest.fixture(autouse=True)
def testfile(tmp_path, monkeypatch):
    testfile = tmp_path / "dirstack.test"
    monkeypatch.setattr(dirstack.Dirstack, "DIRSTACK", testfile)
    yield testfile


@pytest.fixture
def dirstack_on_disk(testfile, monkeypatch):
    stack = dirstack.Dirstack(testfile)
    monkeypatch.setattr(pathlib.Path, "is_dir", Mock(return_value=True))
    stack.add("~/foo/bar")
    stack.add("relative/dir")
    stack.add("/etc")
    with testfile.open("wb") as fp:
        pickle.dump(stack, fp)
    yield testfile


def test_dirstack_load_and_save(testfile, monkeypatch):
    assert not testfile.exists()
    stack = dirstack.Dirstack.load()
    assert stack.sorted() == []
    assert len(stack) == 0
    monkeypatch.setattr(pathlib.Path, "is_dir", Mock(return_value=True))
    stack.add("/tmp")
    time.sleep(0.01)
    stack.add("~/foobar")
    assert len(stack) == 2
    stack.save()
    assert testfile.exists()
    del stack
    stack = dirstack.Dirstack.load()
    assert [e.path for e in stack.sorted()] == [
        pathlib.Path.home() / "foobar",
        pathlib.Path("/tmp"),
    ]


def test_dirstack_load_existing_from_file(dirstack_on_disk):
    assert dirstack_on_disk.is_file()
    stack = dirstack.Dirstack.load()
    assert [e.path for e in stack.sorted()] == [
        pathlib.Path("/etc"),
        pathlib.Path.cwd() / "relative/dir",
        pathlib.Path.home() / "foo/bar",
    ]


def test_dirstack_pop(dirstack_on_disk):
    stack = dirstack.Dirstack.load()
    assert len(stack) == 3
    item = stack.pop("/etc")
    assert len(stack) == 2
    assert item.path == pathlib.Path("/etc")
    with pytest.raises(KeyError):
        stack.pop("/etc")


def test_dirstack_delete(dirstack_on_disk):
    """Delete existing stack from disk."""
    assert dirstack_on_disk.exists()
    dirstack.Dirstack.load().delete()
    assert not dirstack_on_disk.exists()
