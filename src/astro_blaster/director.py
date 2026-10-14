"""Le « directeur » : décide du déroulé de la partie.

Météorites pendant BOSS_TRIGGER_TIME secondes → alerte → boss → nouveau cycle, plus dur.
Logique pure, sans affichage : elle se teste facilement.
"""

from enum import Enum, auto

from astro_blaster import config
from astro_blaster.difficulty import Difficulty, difficulty_at


class Stage(Enum):
    METEORS = auto()
    WARNING = auto()
    BOSS = auto()


class Director:
    def __init__(self, stage_time: float = 0.0) -> None:
        self.stage = Stage.METEORS
        self.cycle = 0
        self.stage_time = stage_time  # temps passé dans la phase de météorites du cycle
        self.warning_left = 0.0

    @property
    def difficulty(self) -> Difficulty:
        return difficulty_at(self.stage_time, self.cycle)

    @property
    def spawns_meteors(self) -> bool:
        return self.stage is Stage.METEORS

    def update(self, dt: float) -> Stage | None:
        """Avance le temps. Renvoie la nouvelle étape si on vient d'en changer."""
        if self.stage is Stage.METEORS:
            self.stage_time += dt
            if self.stage_time >= config.BOSS_TRIGGER_TIME:
                self.stage = Stage.WARNING
                self.warning_left = config.WARNING_DURATION
                return Stage.WARNING
        elif self.stage is Stage.WARNING:
            self.warning_left -= dt
            if self.warning_left <= 0:
                self.stage = Stage.BOSS
                return Stage.BOSS
        return None

    def boss_defeated(self) -> None:
        self.cycle += 1
        self.stage_time = 0.0
        self.stage = Stage.METEORS
