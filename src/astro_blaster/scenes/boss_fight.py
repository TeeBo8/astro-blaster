"""Le combat contre le boss : alerte, projectiles, laser, explosion finale.

Séparé de play.py pour que chaque fichier garde une seule responsabilité. Il utilise les
effets de la scène de jeu (particules, tremblement, son…) qu'il reçoit à sa création.
"""

# `from __future__ import annotations` : les annotations ne sont pas évaluées à l'exécution.
# On peut donc annoter avec PlayScene sans l'importer pour de vrai (sinon import circulaire).
from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame
from pygame import Vector2

from astro_blaster import config
from astro_blaster.config import Color
from astro_blaster.entities.boss import Boss, BossHit, LaserState
from astro_blaster.entities.bullet import Bullet, EnemyBullet
from astro_blaster.fx import neon
from astro_blaster.geometry import circles_overlap, distance_to_segment

if TYPE_CHECKING:  # vrai seulement pour l'éditeur et les vérificateurs de types
    from astro_blaster.scenes.play import PlayScene

HEALTH_BAR_SIZE = (320, 8)
HEALTH_BAR_Y = 62
BANNER_DURATION = 3.0
WARNING_STRIPE_HEIGHT = 34


class BossFight:
    def __init__(self, scene: PlayScene) -> None:
        self.scene = scene
        self.boss: Boss | None = None
        self.enemy_bullets: list[EnemyBullet] = []
        self.warning_age: float | None = None  # None quand aucune alerte n'est en cours
        self.explosion_timer = 0.0
        self.seen_laser_state = LaserState.IDLE
        self.banner: tuple[str, Color] | None = None
        self.banner_time = 0.0

    @property
    def boss_dying(self) -> bool:
        return self.boss is not None and self.boss.dying

    # --- Déroulé -------------------------------------------------------------------------------

    def start_warning(self) -> None:
        self.warning_age = 0.0
        self.scene.audio.stop_music()
        self.scene.audio.play("warning")

    def spawn_boss(self, cycle: int) -> None:
        self.warning_age = None
        self.boss = Boss(cycle)
        self.seen_laser_state = LaserState.IDLE
        self.scene.audio.play_music("boss")
        self.scene.audio.play("roar")
        self.scene.shake.add(0.5)

    def update(self, dt: float) -> None:
        if self.warning_age is not None:
            self.warning_age += dt
        self.banner_time = max(0.0, self.banner_time - dt)
        for bullet in self.enemy_bullets:
            bullet.update(dt)
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]

        boss = self.boss
        if boss is None:
            return
        shots = boss.update(dt, self.scene.ship.position)
        if shots:
            self.scene.audio.play("enemy_shot")
            room = config.ENEMY_BULLET_MAX - len(self.enemy_bullets)
            self.enemy_bullets += shots[: max(0, room)]
        self._follow_laser(dt, boss)
        if boss.dying:
            self._explode_hull(dt, boss)
        if boss.dead:
            self._finish(boss)

    def _follow_laser(self, dt: float, boss: Boss) -> None:
        """Joue les sons du laser quand il change d'état, et fait trembler pendant le tir."""
        if boss.laser_state != self.seen_laser_state:
            self.seen_laser_state = boss.laser_state
            if boss.laser_state is LaserState.CHARGING:
                self.scene.audio.play("laser_charge")
            elif boss.laser_state is LaserState.FIRING:
                self.scene.audio.play("laser_beam")
        if boss.laser_beam() is not None:
            self.scene.shake.add(0.9 * dt)

    def _explode_hull(self, dt: float, boss: Boss) -> None:
        """Pendant l'agonie du boss : des explosions éclatent un peu partout sur la coque."""
        scene = self.scene
        self.explosion_timer -= dt
        if self.explosion_timer > 0:
            return
        self.explosion_timer = config.BOSS_DEATH_EXPLOSION_INTERVAL
        color = scene.rng.choice((config.BOSS_COLOR, config.BOSS_RAGE_COLOR, config.FLAME_COLOR))
        scene.particles.explosion(boss.random_hull_point(scene.rng), color, 22)
        scene.shake.add(0.25)
        scene.audio.play("explosion")

    def _finish(self, boss: Boss) -> None:
        scene = self.scene
        core = boss.core_position
        scene.particles.explosion(core, config.METEOR_HIT_COLOR, 90)
        scene.particles.explosion(core, config.BOSS_RAGE_COLOR, 70)
        scene.particles.explosion(core, config.BOSS_COLOR, 70)
        scene.particles.ring(core, config.METEOR_HIT_COLOR, 600, duration=1.2)
        scene.flash.trigger(0.6)
        scene.shake.add(1.0)
        scene.hitstop.trigger(0.15)
        scene.audio.play("bomb")

        bonus = config.BOSS_SCORE * (scene.director.cycle + 1)
        scene.score.add_bonus(bonus)
        scene.popups.add(f"+{bonus}", core, config.ACCENT_COLOR)
        if scene.ship_alive and scene.ship.lives < config.SHIP_MAX_LIVES:
            scene.ship.lives += 1
            scene.popups.add("+1 VIE", scene.ship.position, config.SHIP_COLOR)
        self.show_banner("VAISSEAU-MÈRE DÉTRUIT", config.ACCENT_COLOR)

        self.boss = None
        scene.director.boss_defeated()
        scene.audio.play_music("main")

    def show_banner(self, message: str, color: Color) -> None:
        self.banner = (message, color)
        self.banner_time = BANNER_DURATION

    # --- Collisions ----------------------------------------------------------------------------

    def bullet_hits_boss(self, bullet: Bullet) -> bool:
        """Teste un tir du joueur contre le boss. Renvoie True si le tir a été arrêté."""
        if self.boss is None or self.boss.dying:
            return False
        result = self.boss.absorb_bullet(bullet.position, bullet.radius)
        if result is None:
            return False
        bullet.alive = False
        self._react(result, bullet.position)
        return True

    def _react(self, result: BossHit, where: Vector2) -> None:
        """Réaction à un coup porté au boss.

        `match` (Python 3.10+) compare une valeur à plusieurs cas, comme un switch.
        """
        scene = self.scene
        match result:
            case BossHit.ARMOR | BossHit.IGNORED:
                scene.particles.sparks(where, config.HUD_COLOR)
                scene.audio.play("armor")
            case BossHit.DAMAGED | BossHit.TURRET_DAMAGED:
                scene.particles.sparks(where, config.BOSS_CORE_COLOR)
                scene.score.add_bonus(config.BOSS_HIT_SCORE)
                scene.audio.play("boss_hit")
            case BossHit.TURRET_DESTROYED:
                scene.particles.explosion(where, config.ACCENT_COLOR, 30)
                scene.score.add_bonus(config.TURRET_SCORE)
                scene.popups.add(f"+{config.TURRET_SCORE}", where, config.ACCENT_COLOR)
                scene.shake.add(0.4)
                scene.audio.play("explosion")
            case BossHit.PHASE_CHANGED:
                self._phase_changed()
            case BossHit.KILLED:
                self.clear_bullets()
                scene.flash.trigger(0.4)
                scene.shake.add(0.8)
                scene.hitstop.trigger(0.2)
                scene.audio.stop_music()
                scene.audio.play("big_explosion")

    def _phase_changed(self) -> None:
        """Le boss passe en phase 2 ou 3 : rugissement, onde de choc, l'écran est nettoyé."""
        assert self.boss is not None  # `assert` : garde-fou, plante tout de suite si c'est faux
        scene = self.scene
        rage = self.boss.phase == 3
        color = config.BOSS_RAGE_COLOR if rage else config.BOSS_COLOR
        self.clear_bullets()
        scene.particles.ring(self.boss.core_position, color, 500, duration=0.9)
        scene.flash.trigger(0.3, color)
        scene.shake.add(0.7)
        scene.hitstop.trigger(0.12)
        scene.audio.play("roar")
        self.show_banner("RAGE !" if rage else "PHASE 2", color)

    def clear_bullets(self) -> None:
        """Fait éclater tous les projectiles ennemis (changement de phase, bombe…)."""
        for bullet in self.enemy_bullets:
            self.scene.particles.sparks(bullet.position, config.ENEMY_BULLET_COLOR)
        self.enemy_bullets.clear()

    def bomb(self) -> None:
        """La bombe nettoie les projectiles et abîme sérieusement le boss."""
        self.clear_bullets()
        if self.boss is not None and not self.boss.dying:
            result = self.boss.damage(config.BOMB_BOSS_DAMAGE)
            self._react(result, self.boss.core_position)

    def threatens(self, position: Vector2, radius: float) -> Vector2 | None:
        """Ce qui touche le vaisseau (projectile ou laser). Renvoie l'endroit du choc.

        Le vaisseau ne monte jamais assez haut pour heurter la coque du boss.
        """
        for bullet in self.enemy_bullets:
            if circles_overlap(position, radius, bullet.position, bullet.radius):
                bullet.alive = False
                return bullet.position
        boss = self.boss
        if boss is None or boss.dying:
            return None
        beam = boss.laser_beam()
        if (
            beam is not None
            and distance_to_segment(position, *beam) < config.LASER_WIDTH / 2 + radius
        ):
            return position
        return None

    # --- Dessin --------------------------------------------------------------------------------

    def draw_world(self, surface: pygame.Surface) -> None:
        if self.boss is not None:
            self.boss.draw(surface)
        for bullet in self.enemy_bullets:
            bullet.draw(surface)

    def draw_overlay(self, surface: pygame.Surface) -> None:
        if self.warning_age is not None:
            self._draw_warning(surface)
        if self.boss is not None and not self.boss.dying:
            self._draw_health_bar(surface, self.boss)
        if self.banner is not None and self.banner_time > 0:
            message, color = self.banner
            fade = min(1.0, self.banner_time / (BANNER_DURATION / 3))
            neon.text(
                surface,
                self.scene.context.fonts.text,
                message,
                neon.scale_color(color, fade),
                center=(config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT * 0.4),
            )

    def _draw_warning(self, surface: pygame.Surface) -> None:
        assert self.warning_age is not None
        age = self.warning_age
        fonts = self.scene.context.fonts
        width, height = surface.get_size()
        blink = math.sin(age * 2 * math.pi * 1.5) > -0.2
        color = config.DANGER_COLOR if blink else neon.scale_color(config.DANGER_COLOR, 0.35)
        # Bandes rouges qui défilent en haut et en bas, comme un ruban « danger ».
        for y in (WARNING_STRIPE_HEIGHT * 2, height - WARNING_STRIPE_HEIGHT * 3):
            pygame.draw.line(surface, color, (0, y), (width, y), 2)
            pygame.draw.line(
                surface,
                color,
                (0, y + WARNING_STRIPE_HEIGHT),
                (width, y + WARNING_STRIPE_HEIGHT),
                2,
            )
            offset = (age * 120) % 40
            for x in range(-40, width + 40, 40):
                start = (x + offset, y + WARNING_STRIPE_HEIGHT - 4)
                end = (x + offset + 18, y + 4)
                pygame.draw.line(surface, neon.scale_color(color, 0.6), start, end, 3)
        if blink:
            neon.text(
                surface,
                fonts.title,
                "WARNING",
                config.DANGER_COLOR,
                center=(width / 2, height * 0.42),
            )
        neon.text(
            surface,
            fonts.hud,
            "VAISSEAU-MÈRE EN APPROCHE",
            config.HUD_COLOR,
            center=(width / 2, height * 0.5),
        )

    def _draw_health_bar(self, surface: pygame.Surface, boss: Boss) -> None:
        bar_width, bar_height = HEALTH_BAR_SIZE
        frame = pygame.Rect(0, 0, bar_width, bar_height)
        frame.midtop = (config.SCREEN_WIDTH // 2, HEALTH_BAR_Y)
        color = config.BOSS_RAGE_COLOR if boss.phase == 3 else config.BOSS_COLOR
        # Pendant l'entrée du boss, la barre se remplit : un classique des jeux d'arcade.
        shown = boss.health_ratio * min(1.0, boss.age / config.BOSS_ENTRY_TIME)
        fill = frame.copy()
        fill.width = round(bar_width * shown)
        surface.fill(color, fill)
        pygame.draw.rect(surface, neon.lighten(color, 0.5), frame, 1)
        for threshold in config.BOSS_PHASE_THRESHOLDS:
            x = frame.left + round(bar_width * threshold)
            pygame.draw.line(
                surface, config.HUD_COLOR, (x, frame.top - 3), (x, frame.bottom + 2), 1
            )
        neon.text(
            surface,
            self.scene.context.fonts.popup,
            "VAISSEAU-MÈRE",
            config.HUD_COLOR,
            midbottom=(frame.centerx, frame.top - 4),
        )
