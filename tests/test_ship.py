from pygame import Vector2

from astro_blaster import config
from astro_blaster.entities.ship import HitResult, Ship
from astro_blaster.input import Controls

FIRE = Controls(move=Vector2(), fire=True)
IDLE = Controls(move=Vector2(), fire=False)


def test_ship_fires_one_bullet_then_waits_for_cooldown() -> None:
    ship = Ship()
    assert len(ship.update(1 / 60, FIRE)) == 1
    assert ship.update(1 / 60, FIRE) == []
    ship.update(config.SHIP_FIRE_COOLDOWN, IDLE)
    assert len(ship.update(1 / 60, FIRE)) == 1


def test_triple_shot_fires_three_spread_bullets() -> None:
    ship = Ship()
    ship.triple_shot_time = config.TRIPLE_SHOT_DURATION
    bullets = ship.update(1 / 60, FIRE)
    assert len(bullets) == 3
    left, middle, right = (b.velocity.x for b in bullets)
    assert left < middle == 0 < right


def test_triple_shot_runs_out() -> None:
    ship = Ship()
    ship.triple_shot_time = 1.0
    ship.update(1.01, IDLE)
    ship.fire_cooldown = 0
    assert len(ship.update(1 / 60, FIRE)) == 1


def test_shield_absorbs_one_hit() -> None:
    ship = Ship()
    ship.shield = True
    assert ship.hit() is HitResult.SHIELD_BROKEN
    assert ship.lives == config.SHIP_START_LIVES
    assert not ship.shield


def test_hit_costs_a_life_then_grants_invincibility() -> None:
    ship = Ship()
    assert ship.hit() is HitResult.DAMAGED
    assert ship.lives == config.SHIP_START_LIVES - 1
    assert ship.hit() is HitResult.IGNORED
    ship.update(config.SHIP_INVINCIBLE_TIME, IDLE)
    assert ship.hit() is HitResult.DAMAGED


def test_ship_stays_on_screen() -> None:
    ship = Ship()
    left = Controls(move=Vector2(-1, 0), fire=False)
    for _ in range(600):
        ship.update(1 / 60, left)
    assert ship.position.x >= config.SHIP_SIDE_MARGIN
