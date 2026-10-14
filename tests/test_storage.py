import sys
from pathlib import Path

import pytest

from astro_blaster import storage
from astro_blaster.storage import BrowserRecordStore, FileRecordStore


def test_file_store_round_trip(tmp_path: Path) -> None:
    store = FileRecordStore(tmp_path / "record.json")
    assert store.load() == 0
    store.save(1234)
    assert store.load() == 1234


class BlockedStorage:
    """Imite un navigateur qui refuse l'accès au localStorage."""

    def getItem(self, key: str) -> str:  # noqa: N802 (nom imposé par l'API JavaScript)
        raise RuntimeError("SecurityError")

    def setItem(self, key: str, value: str) -> None:  # noqa: N802
        raise RuntimeError("QuotaExceededError")


class FakeWindow:
    localStorage = BlockedStorage()  # noqa: N815


class FakePlatform:
    window = FakeWindow()


def test_blocked_browser_storage_never_crashes(monkeypatch: pytest.MonkeyPatch) -> None:
    # `import platform` dans storage.py trouvera ce faux module à la place du vrai.
    monkeypatch.setitem(sys.modules, "platform", FakePlatform())
    store = BrowserRecordStore()
    assert store.load() == 0
    store.save(500)  # ne doit pas lever d'erreur


def test_default_store_on_desktop_is_a_file() -> None:
    assert isinstance(storage.default_store(), FileRecordStore)
