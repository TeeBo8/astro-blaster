"""Écran titre."""

import math
import random

import pygame
from pygame.math import Vector2

from astro_blaster import config
from astro_blaster.context import GameContext
from astro_blaster.entities.ship import HULL
from astro_blaster.fx import neon
from astro_blaster.fx.particles import ParticleSystem
from astro_blaster.scenes.base import Scene
from astro_blaster.scenes.play import PlayScene
from astro_blaster.scoring import format_points

FLICKER_CHANCE = 0.012  # probabilité, à chaque image, que le néon du titre grésille
FLICKER_DURATION = 0.09
SHIP_SCALE = 2.2
CONTROLS = (
    ("FLÈCHES", "se déplacer"),
    ("ESPACE", "tirer"),
    ("P", "pause"),
    ("M", "son"),
)


class TitleScene:
    def __init__(self, context: GameContext) -> None:
        self.context = context
        self.rng = random.Random()
        self.particles = ParticleSystem(self.rng)
        self.age = 0.0
        self.flicker = 0.0
        self.start = False
        context.audio.play_music("main")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.start = True

    def update(self, dt: float) -> Scene | None:
        if self.start:
            return PlayScene(self.context)
        self.age += dt
        self.context.starfield.update(dt, intensity=0.6)  # fond rapide : effet « hyperespace »
        self.flicker = max(0.0, self.flicker - dt)
        if self.rng.random() < FLICKER_CHANCE:
            self.flicker = FLICKER_DURATION
        self.particles.engine(dt, self._ship_position() + Vector2(0, 12 * SHIP_SCALE))
        self.particles.update(dt)
        return None

    def _ship_position(self) -> Vector2:
        bob = math.sin(self.age * 2) * 6
        return Vector2(config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT * 0.52 + bob)

    def draw(self, surface: pygame.Surface) -> None:
        self.context.starfield.draw(surface)
        fonts = self.context.fonts
        center_x = config.SCREEN_WIDTH / 2
        height = config.SCREEN_HEIGHT

        # Un néon qui grésille s'assombrit une fraction de seconde.
        dim = 0.35 if self.flicker > 0 else 1.0
        neon.text(
            surface,
            fonts.title,
            "ASTRO",
            neon.scale_color(config.SHIP_COLOR, dim),
            center=(center_x, height * 0.18),
        )
        neon.text(
            surface,
            fonts.title,
            "BLASTER",
            neon.scale_color(config.METEOR_COLORS[1], dim),
            center=(center_x, height * 0.27),
        )

        self.particles.draw(surface)
        ship = self._ship_position()
        neon.polygon(surface, config.SHIP_COLOR, [ship + p * SHIP_SCALE for p in HULL])

        if self.context.high_score:
            neon.text(
                surface,
                fonts.text,
                f"Record  {format_points(self.context.high_score)}",
                config.ACCENT_COLOR,
                center=(center_x, height * 0.66),
            )
        if math.sin(self.age * 5) > -0.4:
            neon.text(
                surface,
                fonts.text,
                "ESPACE pour jouer",
                config.HUD_COLOR,
                center=(center_x, height * 0.74),
            )
        for index, (key, action) in enumerate(CONTROLS):
            y = height * 0.83 + index * 22
            neon.text(surface, fonts.popup, key, config.SHIP_COLOR, midright=(center_x - 10, y))
            neon.text(surface, fonts.popup, action, config.HUD_COLOR, midleft=(center_x + 10, y))
