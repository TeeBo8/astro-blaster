import pytest
from pygame import Vector2

from astro_blaster import config
from astro_blaster.entities.boss import (
    CORE_OFFSET,
    TURRET_OFFSETS,
    Boss,
    BossHit,
    LaserState,
    Timer,
    aimed,
    fan,
    phase_for,
)

PLAYER = Vector2(config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT - 60)


def arrived_boss(cycle: int = 0) -> Boss:
    boss = Boss(cycle)
    boss.update(config.BOSS_ENTRY_TIME + 0.01, PLAYER)
    return boss


def test_phases_follow_remaining_health() -> None:
    assert phase_for(1.0) == 1
    assert phase_for(0.5) == 2
    assert phase_for(0.2) == 3
    assert phase_for(0.0) == 3


def test_fan_is_symmetric_around_downward_direction() -> None:
    bullets = fan(Vector2(), count=5, spread=60, speed=100)
    assert len(bullets) == 5
    xs = [b.velocity.x for b in bullets]
    assert xs[0] == pytest.approx(-xs[-1])
    assert bullets[2].velocity.x == pytest.approx(0, abs=1e-9)
    assert all(b.velocity.y > 0 for b in bullets)


def test_aimed_shot_flies_toward_target() -> None:
    (bullet,) = aimed(Vector2(0, 0), Vector2(100, 100), count=1, spread=0, speed=10)
    assert bullet.velocity.x == pytest.approx(bullet.velocity.y)


def test_timer_fires_at_each_interval() -> None:
    timer = Timer(1.0)
    assert [timer.tick(0.5) for _ in range(4)] == [False, True, False, True]


def test_boss_is_invulnerable_while_entering() -> None:
    boss = Boss()
    assert boss.damage(10) is BossHit.IGNORED
    assert boss.health == boss.max_health


def test_boss_does_not_shoot_while_entering() -> None:
    boss = Boss()
    assert boss.update(config.BOSS_ENTRY_TIME * 0.9, PLAYER) == []


def test_crossing_threshold_changes_phase_with_a_breather() -> None:
    boss = arrived_boss()
    to_phase_two = boss.health - int(boss.max_health * config.BOSS_PHASE_THRESHOLDS[0])
    assert boss.damage(to_phase_two) is BossHit.PHASE_CHANGED
    assert boss.phase == 2
    assert boss.damage(1) is BossHit.IGNORED  # invulnérable pendant la transition
    assert boss.update(config.BOSS_PHASE_TRANSITION_TIME * 0.5, PLAYER) == []


def test_boss_dies_then_disappears_after_death_sequence() -> None:
    boss = arrived_boss()
    assert boss.damage(boss.max_health) is BossHit.KILLED
    assert boss.dying and not boss.dead
    boss.update(config.BOSS_DEATH_DURATION, PLAYER)
    assert boss.dead


def test_later_cycles_bring_a_tougher_boss() -> None:
    assert Boss(cycle=1).max_health > Boss(cycle=0).max_health


def test_only_the_core_takes_damage() -> None:
    boss = arrived_boss()
    assert boss.absorb_bullet(boss.position + CORE_OFFSET, 3) is BossHit.DAMAGED
    assert boss.absorb_bullet(boss.position + Vector2(-60, 6), 3) is BossHit.ARMOR
    assert boss.absorb_bullet(Vector2(0, config.SCREEN_HEIGHT), 3) is None


def enter_phase(boss: Boss, phase: int) -> None:
    """Abîme le boss juste assez pour entrer dans la phase voulue, puis attend la transition."""
    threshold = config.BOSS_PHASE_THRESHOLDS[phase - 2]
    boss.damage(boss.health - int(boss.max_health * threshold))
    boss.update(config.BOSS_PHASE_TRANSITION_TIME + 0.01, PLAYER)
    assert boss.phase == phase


def test_timer_forgets_backlog_after_a_very_slow_frame() -> None:
    timer = Timer(0.1)
    assert timer.tick(5.0)  # image très lente : un seul tir
    assert not timer.tick(0.01)  # pas de rafale de rattrapage à l'image suivante


def test_turrets_are_armor_during_phase_one() -> None:
    boss = arrived_boss()
    assert boss.absorb_bullet(boss.position + TURRET_OFFSETS[0], 3) is BossHit.ARMOR
    assert all(turret.alive for turret in boss.turrets)


def test_laser_warning_keeps_its_length_in_later_cycles() -> None:
    boss = arrived_boss(cycle=6)
    enter_phase(boss, 2)
    enter_phase(boss, 3)
    step = 1 / 60
    while boss.laser_state is not LaserState.CHARGING:
        boss.update(step, PLAYER)
    warning = 0.0
    while boss.laser_state is LaserState.CHARGING:
        boss.update(step, PLAYER)
        warning += step
    assert warning == pytest.approx(config.LASER_CHARGE_TIME, abs=2 * step)


def test_turret_can_be_destroyed() -> None:
    boss = arrived_boss()
    enter_phase(boss, 2)
    turret_position = boss.position + TURRET_OFFSETS[0]
    for _ in range(config.TURRET_HEALTH - 1):
        assert boss.absorb_bullet(turret_position, 3) is BossHit.TURRET_DAMAGED
    assert boss.absorb_bullet(turret_position, 3) is BossHit.TURRET_DESTROYED
    assert not boss.turrets[0].alive


def test_laser_only_in_rage_and_always_announced() -> None:
    boss = arrived_boss()
    for _ in range(600):
        boss.update(1 / 60, PLAYER)
        assert boss.laser_beam() is None
    boss.damage(boss.health - 1)  # passe directement en phase 3
    assert boss.phase == 3
    saw_warning = False
    for _ in range(60 * 15):
        boss.update(1 / 60, PLAYER)
        saw_warning = saw_warning or boss.laser_warning() is not None
        if boss.laser_beam() is not None:
            break
    assert saw_warning
    assert boss.laser_beam() is not None
