"""La partie en cours."""

import random

import pygame
from pygame.math import Vector2

from astro_blaster import config
from astro_blaster.difficulty import difficulty_at
from astro_blaster.entities.bullet import Bullet
from astro_blaster.entities.meteor import Meteor, spawn_meteors
from astro_blaster.entities.ship import HULL, Ship
from astro_blaster.geometry import circles_overlap
from astro_blaster.input import read_controls
from astro_blaster.scenes.base import Scene
from astro_blaster.scenes.game_over import GameOverScene
from astro_blaster.scoring import Score, format_points

LIFE_ICON_SCALE = 0.6
LIFE_ICON_SPACING = 22


class PlayScene:
    def __init__(self) -> None:
        self.rng = random.Random()
        self.ship = Ship()
        self.bullets: list[Bullet] = []
        self.meteors: list[Meteor] = []
        self.score = Score()
        self.elapsed = 0.0
        self.spawn_timer = config.SPAWN_FIRST_DELAY
        self.paused = False
        self.hud_font = pygame.font.Font(None, config.FONT_SIZE_HUD)
        self.text_font = pygame.font.Font(None, config.FONT_SIZE_TEXT)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_p, pygame.K_ESCAPE):
            self.paused = not self.paused
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.paused = True

    def update(self, dt: float) -> Scene | None:
        if self.paused:
            return None
        self.elapsed += dt
        self._spawn(dt)

        self.bullets += self.ship.update(dt, read_controls())
        for bullet in self.bullets:
            bullet.update(dt)
        for meteor in self.meteors:
            meteor.update(dt)

        self._collide_bullets()
        self._collide_ship()
        self.bullets = [b for b in self.bullets if b.alive]
        self.meteors = [m for m in self.meteors if m.alive]

        if self.ship.lives <= 0:
            # On passe la classe PlayScene elle-même : le game over l'appellera pour rejouer.
            return GameOverScene(self.score.points, self.elapsed, restart=PlayScene)
        return None

    def _spawn(self, dt: float) -> None:
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            difficulty = difficulty_at(self.elapsed)
            self.meteors += spawn_meteors(difficulty, self.rng)
            self.spawn_timer += difficulty.spawn_interval

    def _collide_bullets(self) -> None:
        fragments: list[Meteor] = []
        for bullet in self.bullets:
            for meteor in self.meteors:
                if not meteor.alive or not circles_overlap(
                    bullet.position, bullet.radius, meteor.position, meteor.radius
                ):
                    continue
                bullet.alive = False
                if meteor.take_hit():
                    self.score.add_kill(meteor.score)
                    fragments += meteor.split(self.rng)
                break
        # Les morceaux sont ajoutés après la boucle : un même tir ne peut pas les toucher.
        self.meteors += fragments

    def _collide_ship(self) -> None:
        for meteor in self.meteors:
            if meteor.alive and circles_overlap(
                self.ship.position, self.ship.radius, meteor.position, meteor.radius
            ):
                if self.ship.hit():
                    meteor.alive = False
                    self.score.break_combo()
                return

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(config.BACKGROUND_COLOR)
        for meteor in self.meteors:
            meteor.draw(surface)
        for bullet in self.bullets:
            bullet.draw(surface)
        self.ship.draw(surface)
        self._draw_hud(surface)
        if self.paused:
            self._draw_pause(surface)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        margin = config.HUD_MARGIN
        score = self.hud_font.render(format_points(self.score.points), True, config.HUD_COLOR)
        surface.blit(score, (margin, margin))
        if self.score.multiplier > 1:
            combo = self.hud_font.render(f"x{self.score.multiplier}", True, config.ACCENT_COLOR)
            surface.blit(combo, (margin, margin + score.get_height() + 4))

        for index in range(self.ship.lives):
            center = Vector2(
                config.SCREEN_WIDTH - margin - 10 - index * LIFE_ICON_SPACING, margin + 12
            )
            icon = [center + p * LIFE_ICON_SCALE for p in HULL]
            pygame.draw.polygon(surface, config.SHIP_COLOR, icon, 2)

    def _draw_pause(self, surface: pygame.Surface) -> None:
        veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        veil.fill((0, 0, 0, config.OVERLAY_ALPHA))
        surface.blit(veil, (0, 0))
        text = self.text_font.render("PAUSE  -  P pour reprendre", True, config.HUD_COLOR)
        surface.blit(text, text.get_rect(center=surface.get_rect().center))
