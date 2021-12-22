import collections
import datetime
import logging
import pathlib
import pickle

from typing import Union

import hedgehog

Entry = collections.namedtuple("Entry", "time, path")


class Dirstack:
    """Stack of directory `Entry`'s with last visited timestamps recorded on file."""

    DIRSTACK = hedgehog.CACHE_DIR / "dirstack.dat"

    def __init__(self, path):
        self.log = None
        self._path = path
        self._stack = {}

    @classmethod
    def load(cls, path=None):
        """Load dirstack from file, or return a new instance."""
        path = path or cls.DIRSTACK
        logger = logging.getLogger(cls.__name__)
        try:
            with path.open("rb") as fp:
                stack = pickle.load(fp)
        except OSError:
            logger.debug("Cannot open %s", path, exc_info=True)
            stack = cls(path=path)
        stack.log = logger
        return stack

    def sorted(self):
        return sorted(self._stack.values(), reverse=True)

    @staticmethod
    def _item_to_stack_key(item: Union[str, pathlib.Path, Entry]) -> pathlib.Path:
        if isinstance(item, Entry):
            return item.path
        if isinstance(item, str):
            return pathlib.Path(item).expanduser().resolve()
        return item

    def pop(self, item: Union[str, pathlib.Path, Entry]):
        path = self._item_to_stack_key(item)
        return self._stack.pop(path)

    def add(self, item: Union[str, pathlib.Path, Entry]):
        path = self._item_to_stack_key(item)

        if not path.is_dir():
            self.log.warning("%s doesn't exist, skip adding it", path)
            return
        if entry := self._stack.get(path):
            self.log.debug("Overwriting entry: %s", entry)
        self._stack[path] = Entry(datetime.datetime.now(), path)

    def save(self):
        if not self._stack:
            self.log.info("Stack is empty, removing %s", self._path)
            self._path.unlink(missing_ok=True)
            return
        with self._path.open("wb") as fp:
            pickle.dump(self, fp)
        self.log.debug("Wrote stack to %s", self._path)

    def delete(self):
        self._stack = {}
        self.save()

    def __len__(self):
        return len(self._stack)
