"""Fond spatial : étoiles en trois couches de parallaxe et nébuleuses lentes.

Parallaxe : les étoiles proches (grosses, brillantes) défilent plus vite que les lointaines,
ce qui donne une impression de profondeur.
"""

import random
from dataclasses import dataclass

import pygame
from pygame.math import Vector2

from astro_blaster import config
from astro_blaster.fx import neon


@dataclass
class Star:
    position: Vector2
    speed: float
    size: int
    brightness: int


@dataclass
class Nebula:
    image: pygame.Surface
    position: Vector2


class Starfield:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.stars = [
            Star(self._random_position(), speed * rng.uniform(0.8, 1.2), size, brightness)
            for count, speed, size, brightness in config.STAR_LAYERS
            for _ in range(count)
        ]
        self.nebulae = [
            Nebula(self._make_nebula(color), self._random_position())
            for color in rng.sample(config.NEBULA_COLORS, config.NEBULA_COUNT)
        ]
        self.boost = 1.0  # accélération du défilement, liée à la difficulté

    def _random_position(self) -> Vector2:
        return Vector2(
            self.rng.uniform(0, config.SCREEN_WIDTH), self.rng.uniform(0, config.SCREEN_HEIGHT)
        )

    def _make_nebula(self, color: config.Color) -> pygame.Surface:
        """Nuage coloré très flou, dessiné une seule fois au démarrage."""
        radius = self.rng.randint(*config.NEBULA_RADIUS)
        image = pygame.Surface((radius * 2, radius * 2))
        # Plusieurs disques décalés donnent une forme irrégulière, le flou fait le reste.
        for _ in range(6):
            offset = Vector2(self.rng.uniform(-0.35, 0.35), self.rng.uniform(-0.35, 0.35))
            center = Vector2(radius, radius) + offset * radius
            dimmed = neon.scale_color(color, config.NEBULA_BRIGHTNESS)
            pygame.draw.circle(image, dimmed, center, radius * self.rng.uniform(0.25, 0.45))
        image = pygame.transform.box_blur(image, radius // 4)
        image = pygame.transform.box_blur(image, radius // 4)
        return image

    def update(self, dt: float, intensity: float = 0.0) -> None:
        self.boost = 1.0 + min(intensity, 1.5) * config.STAR_DIFFICULTY_BOOST
        for star in self.stars:
            star.position.y += star.speed * self.boost * dt
            if star.position.y > config.SCREEN_HEIGHT:
                star.position.update(self.rng.uniform(0, config.SCREEN_WIDTH), 0)
        for nebula in self.nebulae:
            nebula.position.y += config.NEBULA_SPEED * self.boost * dt
            if nebula.position.y - nebula.image.get_height() / 2 > config.SCREEN_HEIGHT:
                nebula.position.update(
                    self.rng.uniform(0, config.SCREEN_WIDTH), -nebula.image.get_height() / 2
                )

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(config.BACKGROUND_COLOR)
        for nebula in self.nebulae:
            # Addition de lumière : le noir de l'image n'ajoute rien, donc aucun bord visible.
            rect = nebula.image.get_rect(center=nebula.position)
            surface.blit(nebula.image, rect, special_flags=pygame.BLEND_RGB_ADD)
        for star in self.stars:
            shade = star.brightness
            # Les étoiles rapides laissent une petite traînée : effet de vitesse.
            streak = star.speed * self.boost * config.STAR_STREAK_FACTOR
            rect = (star.position.x, star.position.y, star.size, star.size + streak)
            surface.fill((shade * 3 // 4, shade * 4 // 5, shade), rect)  # blanc bleuté, froid
