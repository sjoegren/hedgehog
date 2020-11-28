import pytest

import hedgehog


@pytest.fixture(autouse=True)
def _cache_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(hedgehog, "CACHE_DIR", tmp_path)
