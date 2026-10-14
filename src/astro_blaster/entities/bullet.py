"""Tirs du vaisseau."""

from dataclasses import dataclass

import pygame
from pygame.math import Vector2

from astro_blaster import config


@dataclass
class Bullet:
    position: Vector2
    velocity: Vector2
    radius: float = config.BULLET_RADIUS
    alive: bool = True

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        if self.position.y < -config.BULLET_LENGTH:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        tail = self.position + Vector2(0, config.BULLET_LENGTH)
        pygame.draw.line(surface, config.BULLET_COLOR, self.position, tail, 3)
