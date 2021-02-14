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

    def formatted(self):
        for bm in sorted(self._bookmarks):
            yield str(bm)
            # print(colored(bm.path, "green"), f"({bm.description})")


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
