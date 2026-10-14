"""Bonus lâchés par les météorites : tir triple, bouclier, bombe."""

import math
import random
from enum import Enum

import pygame
from pygame import Vector2

from astro_blaster import config
from astro_blaster.config import Color
from astro_blaster.fx import neon


class PowerUpKind(Enum):
    """Une Enum liste des valeurs possibles fixes : impossible de se tromper de nom."""

    TRIPLE_SHOT = "TIR TRIPLE"
    SHIELD = "BOUCLIER"
    BOMB = "BOMBE"

    @property
    def color(self) -> Color:
        return {
            PowerUpKind.TRIPLE_SHOT: config.TRIPLE_SHOT_COLOR,
            PowerUpKind.SHIELD: config.SHIELD_COLOR,
            PowerUpKind.BOMB: config.BOMB_COLOR,
        }[self]


KINDS = tuple(PowerUpKind)


def roll_drop(rng: random.Random, meteor_size: int) -> PowerUpKind | None:
    """Tire au sort le bonus lâché par une météorite détruite (souvent aucun)."""
    if rng.random() >= config.POWERUP_DROP_CHANCE[meteor_size]:
        return None
    return rng.choices(KINDS, weights=config.POWERUP_WEIGHTS)[0]


class PowerUp:
    def __init__(self, position: Vector2, kind: PowerUpKind) -> None:
        self.position = position.copy()
        self.kind = kind
        self.radius = config.POWERUP_RADIUS
        self.age = 0.0
        self.alive = True

    def update(self, dt: float) -> None:
        self.age += dt
        amplitude, frequency = config.POWERUP_BOB
        self.position.x += math.cos(self.age * frequency) * amplitude * frequency * dt
        self.position.y += config.POWERUP_FALL_SPEED * dt
        if self.position.y - self.radius > config.SCREEN_HEIGHT:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        color = self.kind.color
        # Hexagone qui tourne et « respire », avec le symbole du bonus au centre.
        pulse = 1 + 0.12 * math.sin(self.age * 8)
        angle = self.age * config.POWERUP_SPIN
        hexagon = [
            self.position + Vector2(0, -self.radius * pulse).rotate(angle + 60 * k)
            for k in range(6)
        ]
        neon.polygon(surface, color, hexagon)
        center = self.position
        if self.kind is PowerUpKind.TRIPLE_SHOT:
            for dx in (-5, 0, 5):
                neon.line(surface, color, center + (dx, 5), center + (dx * 1.4, -6))
        elif self.kind is PowerUpKind.SHIELD:
            neon.circle(surface, color, center, 6)
        else:
            for k in range(4):
                direction = Vector2(0, 7).rotate(45 + 90 * k)
                neon.line(surface, color, center - direction, center + direction)
