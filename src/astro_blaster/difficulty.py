"""Courbe de difficulté : facile au début, de plus en plus dur ensuite.

Tout part d'une seule valeur, l'intensité, calculée à partir du temps de jeu.
Les réglages se changent dans config.py.
"""

from dataclasses import dataclass

from astro_blaster import config
from astro_blaster.geometry import lerp, progress_between


@dataclass(frozen=True)
class Difficulty:
    """Ce que le générateur de météorites doit faire à un instant donné."""

    intensity: float
    spawn_interval: float  # secondes entre deux apparitions
    meteor_speed: float  # vitesse de chute moyenne
    size_weights: tuple[float, float, float]  # poids relatifs petite / moyenne / grosse
    zigzag_chance: float  # probabilité qu'une météorite zigzague
    burst_chance: float  # probabilité d'une rafale de petites météorites rapides


def intensity_at(elapsed: float, cycle: int = 0) -> float:
    """Intensité après `elapsed` secondes du cycle : 0 au début, 1 à la fin de la montée.

    À partir du 2e cycle (après un boss), on ne repart plus de 0 mais d'un cran plus haut.
    """
    start = min(cycle * config.CYCLE_START_INTENSITY, config.CYCLE_START_INTENSITY_MAX)
    progress = max(elapsed, 0.0) / config.DIFFICULTY_RAMP_DURATION
    if progress <= 1.0:
        return start + (1.0 - start) * progress**config.DIFFICULTY_CURVE_EXPONENT
    return 1.0 + (progress - 1.0) * config.DIFFICULTY_OVERDRIVE_SLOPE


def difficulty_at(elapsed: float, cycle: int = 0) -> Difficulty:
    """Tous les paramètres de la vague, à partir du temps écoulé dans le cycle."""
    intensity = intensity_at(elapsed, cycle)
    spawn_interval = lerp(config.SPAWN_INTERVAL_START, config.SPAWN_INTERVAL_END, intensity)
    meteor_speed = lerp(config.METEOR_SPEED_START, config.METEOR_SPEED_END, intensity)
    return Difficulty(
        intensity=intensity,
        spawn_interval=max(spawn_interval, config.SPAWN_INTERVAL_MIN),
        meteor_speed=min(meteor_speed, config.METEOR_SPEED_MAX),
        size_weights=(
            1.0,
            progress_between(intensity, *config.MEDIUM_METEOR_RAMP),
            progress_between(intensity, *config.LARGE_METEOR_RAMP) * config.LARGE_METEOR_MAX_WEIGHT,
        ),
        zigzag_chance=progress_between(intensity, *config.ZIGZAG_RAMP) * config.ZIGZAG_MAX_CHANCE,
        burst_chance=progress_between(intensity, *config.BURST_RAMP) * config.BURST_MAX_CHANCE,
    )
