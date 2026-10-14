from astro_blaster import config
from astro_blaster.director import Director, Stage


def run(director: Director, seconds: float, step: float = 0.1) -> list[Stage]:
    changes = []
    for _ in range(round(seconds / step)):
        change = director.update(step)
        if change is not None:
            changes.append(change)
    return changes


def test_meteors_first_then_warning_then_boss() -> None:
    director = Director()
    assert director.spawns_meteors
    changes = run(director, config.BOSS_TRIGGER_TIME + config.WARNING_DURATION + 1)
    assert changes == [Stage.WARNING, Stage.BOSS]
    assert not director.spawns_meteors


def test_boss_stays_until_defeated() -> None:
    director = Director(stage_time=config.BOSS_TRIGGER_TIME)
    run(director, config.WARNING_DURATION + 1)
    assert run(director, 600) == []
    assert director.stage is Stage.BOSS


def test_defeating_boss_starts_a_harder_cycle() -> None:
    director = Director(stage_time=config.BOSS_TRIGGER_TIME)
    run(director, config.WARNING_DURATION + 1)
    first_cycle_start = Director().difficulty.intensity
    director.boss_defeated()
    assert director.stage is Stage.METEORS
    assert director.cycle == 1
    assert director.difficulty.intensity > first_cycle_start
