import random

import pytest
from pygame.math import Vector2

from astro_blaster.geometry import (
    circles_overlap,
    clamp,
    lerp,
    progress_between,
    random_polygon,
)


def test_clamp_keeps_value_inside_bounds() -> None:
    assert clamp(-5, 0, 10) == 0
    assert clamp(15, 0, 10) == 10
    assert clamp(4, 0, 10) == 4


def test_lerp() -> None:
    assert lerp(10, 20, 0) == 10
    assert lerp(10, 20, 0.5) == 15
    assert lerp(10, 20, 1) == 20


def test_progress_between_is_bounded() -> None:
    assert progress_between(0.0, 0.2, 0.6) == 0
    assert progress_between(0.4, 0.2, 0.6) == pytest.approx(0.5)
    assert progress_between(1.0, 0.2, 0.6) == 1


def test_circles_touching_overlap() -> None:
    assert circles_overlap(Vector2(0, 0), 5, Vector2(10, 0), 5)
    assert circles_overlap(Vector2(0, 0), 5, Vector2(3, 4), 1)


def test_distant_circles_do_not_overlap() -> None:
    assert not circles_overlap(Vector2(0, 0), 5, Vector2(10.1, 0), 5)


def test_random_polygon_stays_within_radius() -> None:
    rng = random.Random(42)
    points = random_polygon(rng, radius=30, vertex_count=11, jaggedness=0.3)
    assert len(points) == 11
    for point in points:
        assert 30 * 0.7 - 1e-9 <= point.length() <= 30 + 1e-9


def test_random_polygon_is_reproducible_with_same_seed() -> None:
    first = random_polygon(random.Random(7), 20, 8, 0.3)
    second = random_polygon(random.Random(7), 20, 8, 0.3)
    assert first == second
