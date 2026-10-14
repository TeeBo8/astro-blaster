"""Score, multiplicateur de combo et record sauvegardé."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

from astro_blaster import config


@dataclass
class Score:
    """Le score d'une partie.

    Le combo compte les météorites détruites d'affilée sans se faire toucher :
    toutes les COMBO_STEP destructions, le multiplicateur gagne +1.
    """

    points: int = 0
    combo: int = 0

    @property
    def multiplier(self) -> int:
        return min(1 + self.combo // config.COMBO_STEP, config.COMBO_MAX_MULTIPLIER)

    def add_kill(self, base_points: int) -> int:
        """Compte une destruction et renvoie les points gagnés."""
        self.combo += 1
        gained = base_points * self.multiplier
        self.points += gained
        return gained

    def add_bonus(self, points: int) -> None:
        """Points hors combo (coups sur le boss, prime de victoire…)."""
        self.points += points

    def break_combo(self) -> None:
        self.combo = 0


def format_points(points: int) -> str:
    """12345 → « 12 345 » (espace comme séparateur des milliers, à la française)."""
    return f"{points:,}".replace(",", " ")


def default_save_path() -> Path:
    """Fichier du record, dans le dossier de données de l'utilisateur.

    Windows : %APPDATA%, Linux : ~/.local/share (ou $XDG_DATA_HOME), sinon le dossier personnel.
    """
    base = os.environ.get("APPDATA") or os.environ.get("XDG_DATA_HOME")
    root = Path(base) if base else Path.home() / ".local" / "share"
    return root / "astro-blaster" / "record.json"


def load_high_score(path: Path) -> int:
    """Lit le record. Fichier absent, illisible ou trafiqué : on repart de 0 sans planter."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))["high_score"]
    except (OSError, ValueError, KeyError, TypeError):
        return 0
    # type(...) is int : exclut aussi True/False, que Python considère comme des entiers.
    return value if type(value) is int and value > 0 else 0


def save_high_score(path: Path, score: int) -> None:
    """Écrit le record. Si le disque refuse (dossier en lecture seule…), le jeu continue."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"high_score": score}), encoding="utf-8")
    except OSError:
        pass
