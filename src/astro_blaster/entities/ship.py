"""Le vaisseau du joueur."""

import math
import random
from enum import Enum, auto

import pygame
from pygame.math import Vector2

from astro_blaster import config
from astro_blaster.entities.bullet import Bullet
from astro_blaster.fx import neon
from astro_blaster.geometry import clamp
from astro_blaster.input import Controls

# Contour du vaisseau, pointe vers le haut, centré sur (0, 0).
HULL = (
    Vector2(0, -20),
    Vector2(6, -6),
    Vector2(16, 12),
    Vector2(5, 8),
    Vector2(0, 12),
    Vector2(-5, 8),
    Vector2(-16, 12),
    Vector2(-6, -6),
)
COCKPIT = (Vector2(0, -10), Vector2(3, -2), Vector2(-3, -2))
GUN_OFFSET = Vector2(0, -20)
ENGINE_OFFSET = Vector2(0, 12)
FLAME_BASE = (Vector2(-4, 11), Vector2(4, 11))
FLAME_LENGTH = (8.0, 18.0)


class HitResult(Enum):
    IGNORED = auto()  # invincible : rien ne se passe
    SHIELD_BROKEN = auto()  # le bouclier a encaissé à la place du vaisseau
    DAMAGED = auto()  # une vie perdue


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
        self.triple_shot_time = 0.0
        self.shield = False
        self.age = 0.0

    @property
    def is_invincible(self) -> bool:
        return self.invincible_time > 0

    @property
    def engine_position(self) -> Vector2:
        return self.position + ENGINE_OFFSET

    def update(self, dt: float, controls: Controls) -> list[Bullet]:
        """Déplace le vaisseau et renvoie les tirs créés pendant cette image."""
        self.age += dt
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
        self.triple_shot_time = max(0.0, self.triple_shot_time - dt)
        self.fire_cooldown = max(0.0, self.fire_cooldown - dt)
        if controls.fire and self.fire_cooldown == 0:
            self.fire_cooldown = config.SHIP_FIRE_COOLDOWN
            return self._shoot()
        return []

    def _shoot(self) -> list[Bullet]:
        angles = (0.0,)
        if self.triple_shot_time > 0:
            angles = (-config.TRIPLE_SHOT_SPREAD, 0.0, config.TRIPLE_SHOT_SPREAD)
        velocity = Vector2(0, -config.BULLET_SPEED)
        return [Bullet(self.position + GUN_OFFSET, velocity.rotate(angle)) for angle in angles]

    def hit(self) -> HitResult:
        """Encaisse un choc."""
        if self.is_invincible:
            return HitResult.IGNORED
        if self.shield:
            self.shield = False
            self.invincible_time = config.SHIELD_BREAK_INVINCIBLE_TIME
            return HitResult.SHIELD_BROKEN
        self.lives -= 1
        self.invincible_time = config.SHIP_INVINCIBLE_TIME
        return HitResult.DAMAGED

    def draw(self, surface: pygame.Surface) -> None:
        # Pendant l'invincibilité, on n'affiche le vaisseau qu'une demi-période sur deux.
        blink = math.sin(self.invincible_time * config.SHIP_BLINK_FREQUENCY * 2 * math.pi)
        if self.is_invincible and not self.shield and blink > 0:
            return
        tilt = self.velocity.x / config.SHIP_SPEED * config.SHIP_MAX_TILT

        flame_tip = Vector2(0, FLAME_BASE[0].y + random.uniform(*FLAME_LENGTH))
        flame = [self.position + p.rotate(tilt) for p in (FLAME_BASE[0], flame_tip, FLAME_BASE[1])]
        neon.polygon(surface, config.FLAME_COLOR, flame)

        hull_color = config.TRIPLE_SHOT_COLOR if self.triple_shot_time > 0 else config.SHIP_COLOR
        neon.polygon(surface, hull_color, [self.position + p.rotate(tilt) for p in HULL])
        neon.polygon(surface, config.HUD_COLOR, [self.position + p.rotate(tilt) for p in COCKPIT])

        if self.shield:
            pulse = config.SHIELD_RADIUS + 2 * math.sin(self.age * 6)
            neon.circle(surface, config.SHIELD_COLOR, self.position, pulse)
