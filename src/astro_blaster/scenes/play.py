"""La partie en cours."""

import random

import pygame
from pygame.math import Vector2

from astro_blaster import config
from astro_blaster.context import GameContext
from astro_blaster.difficulty import difficulty_at
from astro_blaster.entities.bullet import Bullet
from astro_blaster.entities.meteor import LARGE, Meteor, spawn_meteors
from astro_blaster.entities.powerup import PowerUp, PowerUpKind, roll_drop
from astro_blaster.entities.ship import HULL, HitResult, Ship
from astro_blaster.fx import neon
from astro_blaster.fx.impact import HitStop, ScreenFlash, ScreenShake
from astro_blaster.fx.particles import ParticleSystem
from astro_blaster.fx.popups import Popups
from astro_blaster.geometry import circles_overlap
from astro_blaster.input import read_controls
from astro_blaster.scenes.base import Scene
from astro_blaster.scenes.game_over import GameOverScene
from astro_blaster.scoring import Score, format_points

SCREEN_SIZE = (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
LIFE_ICON_SCALE = 0.55
LIFE_ICON_SPACING = 24
TRIPLE_BAR_SIZE = (60, 4)


class PlayScene:
    def __init__(self, context: GameContext) -> None:
        self.context = context
        self.audio = context.audio
        self.rng = random.Random()
        self.ship = Ship()
        self.bullets: list[Bullet] = []
        self.meteors: list[Meteor] = []
        self.powerups: list[PowerUp] = []
        self.score = Score()
        self.elapsed = 0.0
        self.spawn_timer = config.SPAWN_FIRST_DELAY
        self.paused = False
        self.death_time: float | None = None  # None tant que le vaisseau est en vie

        self.particles = ParticleSystem(self.rng)
        self.shake = ScreenShake(self.rng)
        self.flash = ScreenFlash(SCREEN_SIZE)
        self.hitstop = HitStop()
        self.popups = Popups(context.fonts.popup)
        self.combo_pulse = 0.0
        # Le monde est dessiné à part, puis posé sur l'écran avec le décalage du tremblement :
        # l'interface (score, vies) reste immobile.
        self.world = pygame.Surface(SCREEN_SIZE)

    @property
    def ship_alive(self) -> bool:
        return self.death_time is None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_p, pygame.K_ESCAPE):
            self.paused = not self.paused
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.paused = True

    # --- Mise à jour ---------------------------------------------------------------------------

    def update(self, dt: float) -> Scene | None:
        if self.paused:
            return None
        # Ces effets avancent en temps réel, même pendant la micro-pause et le ralenti.
        self.shake.update(dt)
        self.flash.update(dt)
        self.combo_pulse = max(0.0, self.combo_pulse - dt * 3)
        if self.hitstop.consume(dt):
            return None

        if self.death_time is not None:
            self.death_time += dt
            if self.death_time >= config.DEATH_DURATION:
                return GameOverScene(self.context, self.score.points, self.elapsed)
            dt *= config.DEATH_TIME_SCALE

        self.elapsed += dt
        difficulty = difficulty_at(self.elapsed)
        self.context.starfield.update(dt, difficulty.intensity)
        self._spawn(dt)

        if self.ship_alive:
            new_bullets = self.ship.update(dt, read_controls())
            if new_bullets:
                self.audio.play("laser")
            self.bullets += new_bullets
            self.particles.engine(dt, self.ship.engine_position)

        for entity in (*self.bullets, *self.meteors, *self.powerups):
            entity.update(dt)
        self.particles.update(dt)
        self.popups.update(dt)

        self._collide_bullets()
        if self.ship_alive:
            self._collide_ship()
            self._collect_powerups()
        self.bullets = [b for b in self.bullets if b.alive]
        self.meteors = [m for m in self.meteors if m.alive]
        self.powerups = [p for p in self.powerups if p.alive]
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
                    fragments += self._destroy_meteor(meteor)
                else:
                    self.particles.sparks(bullet.position, meteor.color)
                    self.audio.play("hit")
                break
        # Les morceaux sont ajoutés après la boucle : un même tir ne peut pas les toucher.
        self.meteors += fragments

    def _destroy_meteor(self, meteor: Meteor, split: bool = True) -> list[Meteor]:
        """Score, explosion, bonus éventuel. Renvoie les morceaux de la météorite."""
        meteor.alive = False
        previous_multiplier = self.score.multiplier
        gained = self.score.add_kill(meteor.score)
        self.popups.add(f"+{gained}", meteor.position, config.HUD_COLOR)
        if self.score.multiplier > previous_multiplier:
            self.combo_pulse = 1.0
            self.audio.play("combo")

        self.particles.explosion(meteor.position, meteor.color, meteor.visual_radius)
        self.shake.add(config.METEOR_SHAKE[meteor.size])
        if meteor.size == LARGE:
            self.hitstop.trigger()
            self.audio.play("big_explosion")
        else:
            self.audio.play("explosion")

        if not split:
            return []
        kind = roll_drop(self.rng, meteor.size)
        if kind is not None:
            self.powerups.append(PowerUp(meteor.position, kind))
        return meteor.split(self.rng)

    def _collide_ship(self) -> None:
        ship = self.ship
        for meteor in self.meteors:
            if not meteor.alive or not circles_overlap(
                ship.position, ship.radius, meteor.position, meteor.radius
            ):
                continue
            result = ship.hit()
            if result is HitResult.IGNORED:
                return
            meteor.alive = False
            self.particles.explosion(meteor.position, meteor.color, meteor.visual_radius)
            if result is HitResult.SHIELD_BROKEN:
                self.particles.ring(ship.position, config.SHIELD_COLOR, config.SHIELD_RADIUS * 3)
                self.shake.add(0.4)
                self.audio.play("shield_break")
                return
            self.score.break_combo()
            self.shake.add(config.SHIP_HIT_SHAKE)
            self.flash.trigger(config.SHIP_HIT_FLASH, config.DANGER_COLOR)
            self.hitstop.trigger(config.HITSTOP_DURATION * 2)
            self.audio.play("ship_hit")
            if ship.lives <= 0:
                self._destroy_ship()
            return

    def _destroy_ship(self) -> None:
        self.death_time = 0.0
        position = self.ship.position
        self.particles.explosion(position, config.SHIP_COLOR, 60)
        self.particles.explosion(position, config.FLAME_COLOR, 40)
        self.particles.ring(position, config.HUD_COLOR, 260, duration=0.8)
        self.flash.trigger(config.SHIP_DEATH_FLASH)
        self.shake.add(1.0)
        self.audio.play("big_explosion")

    def _collect_powerups(self) -> None:
        ship = self.ship
        for powerup in self.powerups:
            if not circles_overlap(
                ship.position, config.SHIELD_RADIUS, powerup.position, powerup.radius
            ):
                continue
            powerup.alive = False
            kind = powerup.kind
            self.popups.add(kind.value, powerup.position, kind.color)
            self.particles.ring(powerup.position, kind.color, 60)
            self.audio.play("powerup")
            if kind is PowerUpKind.TRIPLE_SHOT:
                ship.triple_shot_time = config.TRIPLE_SHOT_DURATION
            elif kind is PowerUpKind.SHIELD:
                ship.shield = True
            else:
                self._detonate_bomb()

    def _detonate_bomb(self) -> None:
        """Détruit toutes les météorites à l'écran (sans morceaux ni bonus)."""
        for meteor in self.meteors:
            if meteor.alive:
                self._destroy_meteor(meteor, split=False)
        self.particles.ring(self.ship.position, config.BOMB_COLOR, config.BOMB_RING_RADIUS, 0.7)
        self.flash.trigger(config.BOMB_FLASH, config.BOMB_COLOR)
        self.shake.add(config.BOMB_SHAKE)
        self.hitstop.trigger(config.HITSTOP_DURATION * 2)
        self.audio.play("bomb")

    # --- Dessin --------------------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        world = self.world
        self.context.starfield.draw(world)
        for entity in (*self.powerups, *self.meteors, *self.bullets):
            entity.draw(world)
        if self.ship_alive:
            self.ship.draw(world)
        self.particles.draw(world)
        self.popups.draw(world)

        surface.fill(config.BACKGROUND_COLOR)
        surface.blit(world, self.shake.offset())
        self.flash.draw(surface)
        self._draw_hud(surface)
        if self.paused:
            self._draw_pause(surface)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        fonts = self.context.fonts
        margin = config.HUD_MARGIN
        score_rect = neon.text(
            surface,
            fonts.hud,
            format_points(self.score.points),
            config.HUD_COLOR,
            topleft=(margin, margin),
        )
        if self.score.multiplier > 1:
            combo = fonts.hud.render(f"x{self.score.multiplier}", True, config.ACCENT_COLOR)
            combo = pygame.transform.smoothscale_by(combo, 1 + 0.6 * self.combo_pulse)
            surface.blit(combo, combo.get_rect(topleft=(margin, score_rect.bottom + 4)))

        right = config.SCREEN_WIDTH - margin - 12
        for index in range(self.ship.lives):
            center = Vector2(right - index * LIFE_ICON_SPACING, margin + 12)
            neon.polygon(surface, config.SHIP_COLOR, [center + p * LIFE_ICON_SCALE for p in HULL])

        if self.ship.triple_shot_time > 0:
            width, height = TRIPLE_BAR_SIZE
            share = min(1.0, self.ship.triple_shot_time / config.TRIPLE_SHOT_DURATION)
            bar = pygame.Rect(right + 12 - width, margin + 30, round(width * share), height)
            surface.fill(config.TRIPLE_SHOT_COLOR, bar)

    def _draw_pause(self, surface: pygame.Surface) -> None:
        veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        veil.fill((0, 0, 0, config.OVERLAY_ALPHA))
        surface.blit(veil, (0, 0))
        fonts = self.context.fonts
        center_x, center_y = surface.get_rect().center
        neon.text(
            surface, fonts.title, "PAUSE", config.SHIP_COLOR, center=(center_x, center_y - 20)
        )
        neon.text(
            surface,
            fonts.text,
            "P pour reprendre",
            config.HUD_COLOR,
            center=(center_x, center_y + 30),
        )
