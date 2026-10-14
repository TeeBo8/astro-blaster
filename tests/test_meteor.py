import random

from pygame import Vector2

from astro_blaster import config
from astro_blaster.difficulty import difficulty_at
from astro_blaster.entities.meteor import LARGE, MEDIUM, SMALL, Meteor, spawn_meteors


def make_meteor(size: int) -> Meteor:
    return Meteor(Vector2(200, 300), Vector2(0, 100), size, random.Random(1))


def test_large_meteor_needs_several_hits() -> None:
    meteor = make_meteor(LARGE)
    hits = [meteor.take_hit() for _ in range(config.METEOR_HIT_POINTS[LARGE])]
    assert hits[-1] is True
    assert not any(hits[:-1])
    assert not meteor.alive


def test_meteors_split_into_two_smaller_pieces() -> None:
    rng = random.Random(3)
    assert [p.size for p in make_meteor(LARGE).split(rng)] == [MEDIUM, MEDIUM]
    assert [p.size for p in make_meteor(MEDIUM).split(rng)] == [SMALL, SMALL]
    assert make_meteor(SMALL).split(rng) == []


def test_fragments_fly_apart_and_keep_falling() -> None:
    left, right = make_meteor(LARGE).split(random.Random(5))
    assert left.velocity.x < 0 < right.velocity.x
    assert left.velocity.y > 0
    assert right.velocity.y > 0


def test_meteor_dies_after_leaving_the_bottom() -> None:
    meteor = make_meteor(SMALL)
    meteor.position.y = config.SCREEN_HEIGHT + 100
    meteor.update(1 / 60)
    assert not meteor.alive


def test_meteor_bounces_on_side_walls() -> None:
    meteor = Meteor(Vector2(1, 300), Vector2(-50, 100), SMALL, random.Random(1))
    meteor.update(1 / 60)
    assert meteor.velocity.x > 0
    assert meteor.position.x >= meteor.radius


def test_first_spawns_are_single_small_meteors_inside_screen() -> None:
    rng = random.Random(11)
    for _ in range(200):
        meteors = spawn_meteors(difficulty_at(0), rng)
        assert len(meteors) == 1
        meteor = meteors[0]
        assert meteor.size == SMALL
        assert not meteor.zigzag
        assert 0 <= meteor.position.x <= config.SCREEN_WIDTH
        assert meteor.position.y < 0
