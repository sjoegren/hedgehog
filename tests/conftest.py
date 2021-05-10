import pytest

import hedgehog


@pytest.fixture(autouse=True)
def _cache_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(hedgehog, "CACHE_DIR", tmp_path)


@pytest.fixture(autouse=True)
def _config_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(hedgehog, "CONFIG_DIR", tmp_path)


@pytest.fixture(autouse=True)
def _tempdir(monkeypatch, tmp_path):
    monkeypatch.setattr("tempfile.tempdir", str(tmp_path))
