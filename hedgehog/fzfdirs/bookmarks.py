import functools
import glob
import logging
import os.path
import pathlib

from typing import Optional

import yaml

from .. import Print

log = logging.getLogger(__name__)
HOME = os.path.expanduser("~") + "/"


class RecentlyUsed:
    """
    List of recently used paths stored in a cache file.
    The most recently used path is first in the list.
    """

    store_paths = 10

    def __init__(self, path):
        self._file = pathlib.Path(path).resolve()
        self.paths = []
        if self._file.exists():
            self.paths = yaml.safe_load(self._file.read_bytes())
            log.info(
                "Read %d recently used paths from %s",
                len(self.paths),
                self._file,
            )
        log.debug("Recent paths: %s", self.paths)

    def add(self, path):
        """Add path to top of recently used list and write file."""
        try:
            self.paths.remove(path)
        except ValueError:
            pass
        self.paths.insert(0, path)
        self.paths = self.paths[: self.store_paths]
        with self._file.open("w") as fp:
            yaml.dump(self.paths, fp)
        log.debug("Wrote paths to %s: %s", self._file, self.paths)


class Bookmarks:
    def __init__(self, path):
        self._file = pathlib.Path(path).resolve()
        self._bookmarks: list[Bookmark] = []
        self._read()

    def _read(self):
        if not self._file.exists():
            return []
        entries = yaml.safe_load(self._file.read_bytes())
        for bm in entries:
            path = os.path.expanduser(bm["path"])
            if "*" not in path and not os.path.exists(path):
                log.warning("Bookmark %s doesn't exist, file: %s", bm, self._file)
                continue
            for p in glob.iglob(path):
                if os.path.isdir(p):
                    self._bookmarks.append(Bookmark(p, bm.get("desc")))

    def __str__(self):
        return "<Bookmarks: size={}, file={}>".format(len(self._bookmarks), self._file)

    def __len__(self):
        return len(self._bookmarks)

    def sorted_formatted(self, recently_used: Optional[RecentlyUsed] = None):
        bookmarks = sorted(self._bookmarks)
        indexes = {bm.path: index for index, bm in enumerate(bookmarks)}
        if recently_used:
            # Move paths from recent_paths to firs in the list of bookmarks
            for path in reversed(recently_used.paths):
                bm = bookmarks.pop(indexes[path])
                bookmarks.insert(0, bm)
        for bm in bookmarks:
            yield str(bm)


@functools.total_ordering
class Bookmark:
    def __init__(self, path: str, desc: Optional[str]):
        self.path = path
        self.description = desc

    def __eq__(self, other):
        return self.path == other.path

    def __gt__(self, other):
        return self.path > other.path

    def __str__(self):
        ret = Print.instance().colored(self.path.replace(HOME, ""), "green")
        if self.description is None:
            return ret
        return ret + f"\t({self.description})"
