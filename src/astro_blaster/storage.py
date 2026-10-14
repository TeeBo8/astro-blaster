"""Le record : dans un fichier sur ordinateur, dans le localStorage du navigateur.

Dans les deux cas, une erreur (fichier illisible, stockage bloqué par le navigateur…) ne doit
jamais empêcher de jouer : on repart simplement de 0.
"""

import json
import os
import sys
from pathlib import Path
from typing import Protocol

# Dans le navigateur (pygbag), Python tourne compilé en WebAssembly : sys.platform le signale.
IN_BROWSER = sys.platform == "emscripten"
BROWSER_KEY = "astro-blaster.record"


def parse_high_score(text: str) -> int:
    """Lit le record dans un texte JSON. Illisible ou trafiqué : 0, sans planter."""
    try:
        value = json.loads(text)["high_score"]
    except (ValueError, KeyError, TypeError):
        return 0
    # type(...) is int : exclut aussi True/False, que Python considère comme des entiers.
    return value if type(value) is int and value > 0 else 0


def serialize_high_score(score: int) -> str:
    return json.dumps({"high_score": score})


def default_save_path() -> Path:
    """Fichier du record, dans le dossier de données de l'utilisateur.

    Windows : %APPDATA% ; ailleurs : $XDG_DATA_HOME, ou à défaut ~/.local/share.
    """
    base = os.environ.get("APPDATA") or os.environ.get("XDG_DATA_HOME")
    root = Path(base) if base else Path.home() / ".local" / "share"
    return root / "astro-blaster" / "record.json"


def load_high_score(path: Path) -> int:
    """Lit le record dans un fichier. Fichier absent ou illisible : 0."""
    try:
        return parse_high_score(path.read_text(encoding="utf-8"))
    except OSError:
        return 0


def save_high_score(path: Path, score: int) -> None:
    """Écrit le record. Si le disque refuse (dossier en lecture seule…), le jeu continue."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(serialize_high_score(score), encoding="utf-8")
    except OSError:
        pass


class RecordStore(Protocol):
    def load(self) -> int: ...

    def save(self, score: int) -> None: ...


class FileRecordStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> int:
        return load_high_score(self.path)

    def save(self, score: int) -> None:
        save_high_score(self.path, score)


class BrowserRecordStore:
    """Le localStorage du navigateur : il survit au rechargement de la page.

    Le module `platform` de pygbag donne accès aux objets JavaScript (window, document…).
    Le navigateur peut refuser l'accès (jeu intégré dans la page d'un autre site, navigation
    privée…) et l'erreur JavaScript arrive alors sous une forme imprévisible : d'où le
    `except Exception` large, exceptionnellement justifié ici.
    """

    def load(self) -> int:
        try:
            import platform

            text = platform.window.localStorage.getItem(BROWSER_KEY)
        except Exception:
            return 0
        return parse_high_score(str(text)) if text else 0

    def save(self, score: int) -> None:
        try:
            import platform

            platform.window.localStorage.setItem(BROWSER_KEY, serialize_high_score(score))
        except Exception:
            pass


def default_store() -> RecordStore:
    return BrowserRecordStore() if IN_BROWSER else FileRecordStore(default_save_path())
