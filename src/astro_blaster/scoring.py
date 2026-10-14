"""Score et multiplicateur de combo."""

from dataclasses import dataclass

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

    def break_combo(self) -> None:
        self.combo = 0


def format_points(points: int) -> str:
    """12345 → « 12 345 » (espace comme séparateur des milliers, à la française)."""
    return f"{points:,}".replace(",", " ")
