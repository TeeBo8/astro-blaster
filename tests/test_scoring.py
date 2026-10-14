from astro_blaster import config
from astro_blaster.scoring import Score, format_points


def test_first_kills_count_once() -> None:
    score = Score()
    assert score.add_kill(100) == 100
    assert score.points == 100
    assert score.multiplier == 1


def test_combo_raises_multiplier() -> None:
    score = Score()
    for _ in range(config.COMBO_STEP):
        score.add_kill(10)
    assert score.multiplier == 2
    assert score.add_kill(10) == 20


def test_multiplier_is_capped() -> None:
    score = Score(combo=config.COMBO_STEP * 100)
    assert score.multiplier == config.COMBO_MAX_MULTIPLIER


def test_getting_hit_resets_combo_but_keeps_points() -> None:
    score = Score()
    for _ in range(config.COMBO_STEP * 2):
        score.add_kill(10)
    points = score.points
    score.break_combo()
    assert score.multiplier == 1
    assert score.points == points


def test_format_points_uses_french_thousands_separator() -> None:
    assert format_points(0) == "0"
    assert format_points(1234567) == "1 234 567"
