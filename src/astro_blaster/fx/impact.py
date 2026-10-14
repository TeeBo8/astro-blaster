"""Effets d'impact : tremblement d'écran, flash, micro-pause (hit-stop).

Ce sont eux qui font « sentir » les chocs, bien plus que les dessins.
"""

import random

import pygame
from pygame import Vector2

from astro_blaster import config
from astro_blaster.config import Color


class ScreenShake:
    """Modèle du « traumatisme » : chaque choc ajoute du traumatisme (0 à 1), qui retombe
    avec le temps. Le décalage est proportionnel à son carré : les petits chocs tremblent
    à peine, les gros secouent fort."""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.trauma = 0.0

    def add(self, amount: float) -> None:
        self.trauma = min(1.0, self.trauma + amount)

    def update(self, dt: float) -> None:
        self.trauma = max(0.0, self.trauma - config.SHAKE_DECAY * dt)

    def offset(self) -> Vector2:
        strength = self.trauma**2 * config.SHAKE_MAX_OFFSET
        return Vector2(self.rng.uniform(-1, 1), self.rng.uniform(-1, 1)) * strength


class ScreenFlash:
    """Voile coloré plein écran qui s'efface rapidement."""

    def __init__(self, size: tuple[int, int]) -> None:
        self.veil = pygame.Surface(size)
        self.strength = 0.0
        self.color: Color = (255, 255, 255)

    def trigger(self, strength: float, color: Color = (255, 255, 255)) -> None:
        self.strength = max(self.strength, strength)
        self.color = color

    def update(self, dt: float) -> None:
        self.strength = max(0.0, self.strength - config.FLASH_DECAY * dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.strength <= 0:
            return
        red, green, blue = (round(c * self.strength) for c in self.color)
        self.veil.fill((red, green, blue))
        surface.blit(self.veil, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


class HitStop:
    """Fige le jeu quelques centièmes de seconde sur un gros impact."""

    def __init__(self) -> None:
        self.remaining = 0.0

    def trigger(self, duration: float = config.HITSTOP_DURATION) -> None:
        self.remaining = max(self.remaining, duration)

    def consume(self, dt: float) -> bool:
        """Renvoie True si le jeu doit rester figé pendant cette image."""
        if self.remaining <= 0:
            return False
        self.remaining -= dt
        return True
