import random
from collections import Counter

from astro_blaster import config
from astro_blaster.entities.meteor import LARGE, SMALL
from astro_blaster.entities.powerup import PowerUpKind, roll_drop


def drop_rate(size: int, rolls: int = 20_000) -> float:
    rng = random.Random(1)
    return sum(roll_drop(rng, size) is not None for _ in range(rolls)) / rolls


def test_large_meteors_drop_more_often_than_small_ones() -> None:
    assert drop_rate(LARGE) > drop_rate(SMALL)


def test_drop_rate_matches_config() -> None:
    assert abs(drop_rate(LARGE) - config.POWERUP_DROP_CHANCE[LARGE]) < 0.01


def test_all_kinds_can_drop() -> None:
    rng = random.Random(2)
    kinds = Counter(roll_drop(rng, LARGE) for _ in range(20_000))
    assert set(PowerUpKind) <= set(kinds)
    # La bombe, le bonus le plus fort, est la plus rare.
    assert kinds[PowerUpKind.BOMB] < kinds[PowerUpKind.TRIPLE_SHOT]
