import pytest

from astro_blaster import config
from astro_blaster.difficulty import difficulty_at, intensity_at


def test_intensity_starts_at_zero_and_reaches_one() -> None:
    assert intensity_at(0) == 0
    assert intensity_at(config.DIFFICULTY_RAMP_DURATION) == pytest.approx(1)


def test_intensity_keeps_rising() -> None:
    times = [0, 10, 30, 60, 90, 120, 150, 200, 300, 600]
    values = [intensity_at(t) for t in times]
    assert values == sorted(values)
    assert len(set(values)) == len(values)


def test_curve_is_gentle_at_first_then_steep() -> None:
    first_30_seconds = intensity_at(30) - intensity_at(0)
    last_30_seconds = intensity_at(150) - intensity_at(120)
    assert last_30_seconds > 3 * first_30_seconds


def test_meteors_come_faster_and_more_often_over_time() -> None:
    early, late = difficulty_at(0), difficulty_at(150)
    assert late.spawn_interval < early.spawn_interval
    assert late.meteor_speed > early.meteor_speed


def test_start_is_only_small_slow_meteors() -> None:
    start = difficulty_at(0)
    assert start.size_weights == (1.0, 0.0, 0.0)
    assert start.zigzag_chance == 0
    assert start.burst_chance == 0


def test_no_large_meteor_during_first_30_seconds() -> None:
    assert difficulty_at(30).size_weights[2] == 0


def test_all_threats_present_at_full_intensity() -> None:
    late = difficulty_at(config.DIFFICULTY_RAMP_DURATION * 1.5)
    assert late.size_weights[1] > 0
    assert late.size_weights[2] > 0
    assert late.zigzag_chance > 0
    assert late.burst_chance > 0


def test_limits_hold_even_after_a_very_long_game() -> None:
    endless = difficulty_at(60 * 60)
    assert endless.spawn_interval == config.SPAWN_INTERVAL_MIN
    assert endless.meteor_speed == config.METEOR_SPEED_MAX
