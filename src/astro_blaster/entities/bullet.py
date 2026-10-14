"""Tirs du vaisseau."""

from dataclasses import dataclass

import pygame
from pygame.math import Vector2

from astro_blaster import config
from astro_blaster.fx import neon


@dataclass
class Bullet:
    position: Vector2
    velocity: Vector2
    radius: float = config.BULLET_RADIUS
    alive: bool = True

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        margin = config.BULLET_LENGTH
        if not (-margin < self.position.x < config.SCREEN_WIDTH + margin) or (
            self.position.y < -margin
        ):
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        # Le trait suit la direction du tir (utile pour les tirs en biais du tir triple).
        tail = self.position - self.velocity.normalize() * config.BULLET_LENGTH
        neon.line(surface, config.BULLET_COLOR, self.position, tail)
