from pathlib import Path

import pytest

from astro_blaster import config
from astro_blaster.scoring import Score, format_points, load_high_score, save_high_score


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


def test_high_score_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "record.json"
    save_high_score(path, 4200)
    assert load_high_score(path) == 4200


def test_missing_save_file_means_no_record(tmp_path: Path) -> None:
    assert load_high_score(tmp_path / "absent.json") == 0


@pytest.mark.parametrize(
    "content",
    [
        "pas du json",
        "[]",
        '{"autre": 3}',
        '{"high_score": "beaucoup"}',
        '{"high_score": -5}',
        '{"high_score": true}',
    ],
)
def test_corrupted_save_file_is_ignored(tmp_path: Path, content: str) -> None:
    path = tmp_path / "record.json"
    path.write_text(content, encoding="utf-8")
    assert load_high_score(path) == 0
