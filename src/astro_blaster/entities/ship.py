"""Le vaisseau du joueur."""

import math
import random

import pygame
from pygame.math import Vector2

from astro_blaster import config
from astro_blaster.entities.bullet import Bullet
from astro_blaster.geometry import clamp
from astro_blaster.input import Controls

# Contour du vaisseau, pointe vers le haut, centré sur (0, 0).
HULL = (Vector2(0, -18), Vector2(14, 14), Vector2(0, 7), Vector2(-14, 14))
GUN_OFFSET = Vector2(0, -18)
FLAME_BASE = (Vector2(-5, 10), Vector2(5, 10))
FLAME_LENGTH = (8.0, 18.0)


class Ship:
    def __init__(self) -> None:
        self.position = Vector2(
            config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT - config.SHIP_BOTTOM_MARGIN
        )
        self.velocity = Vector2()
        self.radius = config.SHIP_HITBOX_RADIUS
        self.lives = config.SHIP_START_LIVES
        self.fire_cooldown = 0.0
        self.invincible_time = 0.0

    @property
    def is_invincible(self) -> bool:
        return self.invincible_time > 0

    def update(self, dt: float, controls: Controls) -> list[Bullet]:
        """Déplace le vaisseau et renvoie les tirs créés pendant cette image."""
        # Inertie : la vitesse rejoint la vitesse voulue progressivement, pas d'un coup.
        target = controls.move * config.SHIP_SPEED
        blend = min(1.0, config.SHIP_RESPONSIVENESS * dt)
        self.velocity += (target - self.velocity) * blend
        self.position += self.velocity * dt

        margin = config.SHIP_SIDE_MARGIN
        self.position.x = clamp(self.position.x, margin, config.SCREEN_WIDTH - margin)
        self.position.y = clamp(
            self.position.y,
            config.SHIP_TOP_LIMIT,
            config.SCREEN_HEIGHT - config.SHIP_BOTTOM_MARGIN / 2,
        )

        self.invincible_time = max(0.0, self.invincible_time - dt)
        self.fire_cooldown = max(0.0, self.fire_cooldown - dt)
        if controls.fire and self.fire_cooldown == 0:
            self.fire_cooldown = config.SHIP_FIRE_COOLDOWN
            return [Bullet(self.position + GUN_OFFSET, Vector2(0, -config.BULLET_SPEED))]
        return []

    def hit(self) -> bool:
        """Encaisse un choc. Renvoie False si le vaisseau était invincible."""
        if self.is_invincible:
            return False
        self.lives -= 1
        self.invincible_time = config.SHIP_INVINCIBLE_TIME
        return True

    def draw(self, surface: pygame.Surface) -> None:
        # Pendant l'invincibilité, on n'affiche le vaisseau qu'une demi-période sur deux.
        if (
            self.is_invincible
            and math.sin(self.invincible_time * config.SHIP_BLINK_FREQUENCY * 2 * math.pi) > 0
        ):
            return
        tilt = self.velocity.x / config.SHIP_SPEED * config.SHIP_MAX_TILT

        flame_tip = Vector2(0, FLAME_BASE[0].y + random.uniform(*FLAME_LENGTH))
        flame = [self.position + p.rotate(tilt) for p in (FLAME_BASE[0], flame_tip, FLAME_BASE[1])]
        pygame.draw.polygon(surface, config.FLAME_COLOR, flame, 2)

        hull = [self.position + p.rotate(tilt) for p in HULL]
        pygame.draw.polygon(surface, config.SHIP_COLOR, hull, 2)
