"""Météorites : trois tailles, les grosses se brisent en plus petites."""

import math
import random

import pygame
from pygame import Vector2

from astro_blaster import config
from astro_blaster.config import Color
from astro_blaster.difficulty import Difficulty
from astro_blaster.fx import neon
from astro_blaster.geometry import random_polygon

SMALL, MEDIUM, LARGE = 0, 1, 2
SIZES = (SMALL, MEDIUM, LARGE)


class Meteor:
    def __init__(
        self,
        position: Vector2,
        velocity: Vector2,
        size: int,
        rng: random.Random,
        zigzag: bool = False,
    ) -> None:
        self.position = position
        self.velocity = velocity
        self.size = size
        self.zigzag = zigzag
        visual_radius = config.METEOR_RADII[size]
        self.radius = visual_radius * config.METEOR_HITBOX_SCALE
        self.hit_points = config.METEOR_HIT_POINTS[size]
        self.shape = random_polygon(
            rng, visual_radius, config.METEOR_VERTEX_COUNT, config.METEOR_JAGGEDNESS
        )
        self.angle = rng.uniform(0, 360)
        self.spin = rng.uniform(-config.METEOR_MAX_SPIN, config.METEOR_MAX_SPIN)
        self.age = rng.uniform(0, 2 * math.pi)  # zigzags décalés entre météorites
        self.flash_time = 0.0
        self.alive = True

    @property
    def score(self) -> int:
        return config.METEOR_SCORES[self.size]

    @property
    def color(self) -> Color:
        return config.METEOR_COLORS[self.size]

    @property
    def visual_radius(self) -> float:
        return config.METEOR_RADII[self.size]

    def update(self, dt: float) -> None:
        self.age += dt
        self.angle += self.spin * dt
        self.flash_time = max(0.0, self.flash_time - dt)

        dx = self.velocity.x
        if self.zigzag:
            dx += math.cos(self.age * config.METEOR_ZIGZAG_FREQUENCY) * config.METEOR_ZIGZAG_SPEED
        self.position += Vector2(dx, self.velocity.y) * dt

        # Rebond sur les bords gauche et droit, pour que rien ne sorte par le côté.
        if self.position.x < self.radius:
            self.position.x = self.radius
            self.velocity.x = abs(self.velocity.x)
        elif self.position.x > config.SCREEN_WIDTH - self.radius:
            self.position.x = config.SCREEN_WIDTH - self.radius
            self.velocity.x = -abs(self.velocity.x)

        if self.position.y - config.METEOR_RADII[self.size] > config.SCREEN_HEIGHT:
            self.alive = False

    def take_hit(self) -> bool:
        """Retire un point de vie. Renvoie True si la météorite est détruite."""
        self.hit_points -= 1
        self.flash_time = config.METEOR_HIT_FLASH_TIME
        if self.hit_points <= 0:
            self.alive = False
        return not self.alive

    def split(self, rng: random.Random) -> list["Meteor"]:
        """Les deux morceaux d'une météorite détruite (aucun pour une petite)."""
        if self.size == SMALL:
            return []
        pieces = []
        # y pointe vers le bas à l'écran : une rotation positive envoie vers la gauche.
        for side in (1, -1):  # morceau de gauche, puis de droite
            deviation = side * rng.uniform(*config.METEOR_FRAGMENT_ANGLE)
            velocity = self.velocity.rotate(deviation) * config.METEOR_FRAGMENT_SPEED_BOOST
            pieces.append(Meteor(self.position.copy(), velocity, self.size - 1, rng))
        return pieces

    def draw(self, surface: pygame.Surface) -> None:
        color = config.METEOR_HIT_COLOR if self.flash_time > 0 else self.color
        neon.polygon(surface, color, [self.position + p.rotate(self.angle) for p in self.shape])
        if self.size != SMALL:
            # Contour intérieur plus sombre : donne du volume aux grosses météorites.
            inner = [self.position + p.rotate(-self.angle * 0.5) * 0.5 for p in self.shape]
            pygame.draw.polygon(surface, neon.scale_color(color, 0.45), inner, 1)


def spawn_meteors(difficulty: Difficulty, rng: random.Random) -> list[Meteor]:
    """Crée la ou les météorites de la prochaine apparition, en haut de l'écran."""
    if rng.random() < difficulty.burst_chance:
        return _spawn_burst(difficulty, rng)

    size = rng.choices(SIZES, weights=difficulty.size_weights)[0]
    radius = config.METEOR_RADII[size]
    spread = config.METEOR_SPEED_SPREAD
    speed = (
        difficulty.meteor_speed
        * rng.uniform(1 - spread, 1 + spread)
        * config.METEOR_SIZE_SPEED_FACTOR[size]
    )
    drift = rng.uniform(-config.METEOR_MAX_DRIFT, config.METEOR_MAX_DRIFT)
    position = Vector2(rng.uniform(radius, config.SCREEN_WIDTH - radius), -radius)
    zigzag = rng.random() < difficulty.zigzag_chance
    return [Meteor(position, Vector2(drift, speed), size, rng, zigzag)]


def _spawn_burst(difficulty: Difficulty, rng: random.Random) -> list[Meteor]:
    """Rafale : quelques petites météorites rapides, en file indienne décalée."""
    radius = config.METEOR_RADII[SMALL]
    count = rng.randint(*config.METEOR_BURST_SIZE)
    speed = difficulty.meteor_speed * config.METEOR_BURST_SPEED_BOOST
    start_x = rng.uniform(radius, config.SCREEN_WIDTH - radius)
    drift = rng.uniform(-config.METEOR_MAX_DRIFT, config.METEOR_MAX_DRIFT)
    return [
        Meteor(
            Vector2(start_x, -radius - index * config.METEOR_BURST_SPACING),
            Vector2(drift, speed),
            SMALL,
            rng,
        )
        for index in range(count)
    ]
