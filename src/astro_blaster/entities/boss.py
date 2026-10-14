"""Le boss : un vaisseau-mère néon en trois phases.

1. Éventails de projectiles et tirs visés.
2. Spirales, et deux tourelles qui tirent sur le joueur (on peut les détruire).
3. Rage : il accélère, vire au rouge et balaie l'écran avec un rayon laser annoncé.

On ne l'abîme qu'en touchant son cœur ; le reste de la coque renvoie les tirs.
"""

import math
import random
from dataclasses import dataclass
from enum import Enum, auto

import pygame
from pygame import Vector2

from astro_blaster import config
from astro_blaster.config import Color
from astro_blaster.entities.bullet import EnemyBullet
from astro_blaster.fx import neon
from astro_blaster.geometry import circles_overlap, lerp

# Silhouette, centrée sur (0, 0), y vers le bas.
HULL = tuple(
    Vector2(x, y)
    for x, y in (
        (0, -48), (34, -38), (62, -12), (128, -2), (118, 22), (64, 26), (34, 52), (0, 40),
        (-34, 52), (-64, 26), (-118, 22), (-128, -2), (-62, -12), (-34, -38),
    )
)  # fmt: skip
PANELS = (
    (Vector2(-62, -12), Vector2(-26, 8)),
    (Vector2(62, -12), Vector2(26, 8)),
    (Vector2(-118, 22), Vector2(-40, 18)),
    (Vector2(118, 22), Vector2(40, 18)),
)
CORE_OFFSET = Vector2(0, 8)
CORE_RADIUS = 22.0
# Plaques de blindage : un tir qui les touche est renvoyé (étincelles, pas de dégâts).
ARMOR = (
    (Vector2(-95, 8), 30.0),
    (Vector2(95, 8), 30.0),
    (Vector2(-52, 6), 26.0),
    (Vector2(52, 6), 26.0),
    (Vector2(0, -28), 22.0),
)
TURRET_OFFSETS = (Vector2(-92, 16), Vector2(92, 16))
TURRET_RADIUS = 14.0
START_Y = -120.0
DOWN = 90.0  # angle « vers le bas » : dans pygame, y augmente vers le bas


class LaserState(Enum):
    IDLE = auto()
    CHARGING = auto()  # trait d'avertissement : le joueur a le temps de s'écarter
    FIRING = auto()


class BossHit(Enum):
    """Ce qui s'est passé quand quelque chose a touché le boss."""

    IGNORED = auto()  # touché pendant qu'il est invulnérable
    ARMOR = auto()
    TURRET_DAMAGED = auto()
    TURRET_DESTROYED = auto()
    DAMAGED = auto()
    PHASE_CHANGED = auto()
    KILLED = auto()


def phase_for(health_ratio: float) -> int:
    """Numéro de phase (1, 2 ou 3) selon la part de vie restante."""
    phase_two, phase_three = config.BOSS_PHASE_THRESHOLDS
    if health_ratio > phase_two:
        return 1
    if health_ratio > phase_three:
        return 2
    return 3


def fan(
    origin: Vector2, count: int, spread: float, speed: float, center: float = DOWN
) -> list[EnemyBullet]:
    """`count` projectiles répartis régulièrement sur un angle de `spread` degrés."""
    if count == 1:
        angles = [center]
    else:
        step = spread / (count - 1)
        angles = [center - spread / 2 + index * step for index in range(count)]
    return [EnemyBullet(origin.copy(), Vector2(speed, 0).rotate(angle)) for angle in angles]


def aimed(
    origin: Vector2, target: Vector2, count: int, spread: float, speed: float
) -> list[EnemyBullet]:
    """Éventail serré dirigé vers la cible."""
    center = Vector2(1, 0).angle_to(target - origin)
    return fan(origin, count, spread, speed, center)


class Timer:
    """Minuteur d'attaque : `tick` renvoie True chaque fois que l'intervalle est écoulé."""

    def __init__(self, interval: float, first_delay: float | None = None) -> None:
        self.interval = interval
        self.remaining = interval if first_delay is None else first_delay

    def tick(self, dt: float) -> bool:
        self.remaining -= dt
        if self.remaining > 0:
            return False
        self.remaining += self.interval
        # Après une image très lente, on oublie le retard au lieu de tirer à chaque image
        # pour le rattraper.
        if self.remaining <= 0:
            self.remaining = self.interval
        return True


@dataclass
class Turret:
    offset: Vector2
    health: int = config.TURRET_HEALTH

    @property
    def alive(self) -> bool:
        return self.health > 0


class Boss:
    def __init__(self, cycle: int = 0) -> None:
        # Chaque cycle, le boss revient plus solide et plus agressif.
        self.aggression = 1 + cycle * config.BOSS_CYCLE_SCALING
        self.max_health = round(config.BOSS_MAX_HEALTH * self.aggression)
        self.health = self.max_health
        self.position = Vector2(config.SCREEN_WIDTH / 2, START_Y)
        self.age = 0.0
        self.sway = 0.0
        self.phase = 1
        self.transition_time = 0.0
        self.flash_time = 0.0
        self.dying_time: float | None = None
        self.turrets = [Turret(offset.copy()) for offset in TURRET_OFFSETS]
        self.turret_timers = [Timer(config.TURRET_INTERVAL) for _ in TURRET_OFFSETS]
        self.fan_timer = Timer(config.FAN_INTERVAL)
        self.aimed_timer = Timer(config.AIMED_INTERVAL)
        self.spiral_timer = Timer(config.SPIRAL_INTERVAL, first_delay=0.0)
        self.rage_fan_timer = Timer(config.RAGE_FAN_INTERVAL)
        self.spiral_angle = 0.0
        self.laser_state = LaserState.IDLE  # IDLE → CHARGING → FIRING → IDLE
        self.laser_time = config.LASER_COOLDOWN
        self.laser_direction = 1

    # --- État ----------------------------------------------------------------------------------

    @property
    def entering(self) -> bool:
        return self.age < config.BOSS_ENTRY_TIME

    @property
    def dying(self) -> bool:
        return self.dying_time is not None

    @property
    def dead(self) -> bool:
        return self.dying_time is not None and self.dying_time >= config.BOSS_DEATH_DURATION

    @property
    def invulnerable(self) -> bool:
        return self.entering or self.transition_time > 0 or self.dying

    @property
    def core_position(self) -> Vector2:
        return self.position + CORE_OFFSET

    @property
    def health_ratio(self) -> float:
        return self.health / self.max_health

    # --- Mise à jour ---------------------------------------------------------------------------

    def update(self, dt: float, target: Vector2) -> list[EnemyBullet]:
        """Déplace le boss et renvoie les projectiles tirés pendant cette image."""
        self.age += dt
        self.flash_time = max(0.0, self.flash_time - dt)
        if self.dying_time is not None:
            self.dying_time += dt
            return []
        if self.entering:
            # Descente qui ralentit à l'arrivée (« ease out ») : plus majestueux.
            progress = self.age / config.BOSS_ENTRY_TIME
            eased = 1 - (1 - progress) ** 3
            self.position.y = lerp(START_Y, config.BOSS_HOVER_Y, eased)
            return []

        self._move(dt)
        if self.transition_time > 0:
            self.transition_time -= dt
            return []
        # Plus le boss est agressif, plus ses minuteurs de tir défilent vite.
        hurried = dt * self.aggression
        if self.phase == 1:
            return self._phase_one(hurried, target)
        if self.phase == 2:
            return self._phase_two(hurried, target)
        # Le laser garde son rythme : l'avertissement doit toujours laisser le temps de fuir.
        self._update_laser(dt)
        return self._phase_three(hurried)

    def _move(self, dt: float) -> None:
        amplitude, frequency = config.BOSS_SWAY
        if self.phase == 3:
            frequency *= config.BOSS_RAGE_SWAY_SPEEDUP
        self.sway += frequency * dt
        self.position.x = config.SCREEN_WIDTH / 2 + math.sin(self.sway) * amplitude
        self.position.y = config.BOSS_HOVER_Y + math.sin(self.sway * 2) * 12

    def _phase_one(self, dt: float, target: Vector2) -> list[EnemyBullet]:
        bullets: list[EnemyBullet] = []
        speed = config.ENEMY_BULLET_SPEED
        if self.fan_timer.tick(dt):
            bullets += fan(self.core_position, config.FAN_COUNT, config.FAN_SPREAD, speed)
        if self.aimed_timer.tick(dt):
            bullets += aimed(
                self.core_position, target, config.AIMED_COUNT, config.AIMED_SPREAD, speed * 1.3
            )
        return bullets

    def _phase_two(self, dt: float, target: Vector2) -> list[EnemyBullet]:
        bullets = self._spiral(dt)
        for turret, timer in zip(self.turrets, self.turret_timers, strict=True):
            if turret.alive and timer.tick(dt):
                origin = self.position + turret.offset
                bullets += aimed(origin, target, 1, 0, config.ENEMY_BULLET_SPEED * 1.4)
        return bullets

    def _spiral(self, dt: float) -> list[EnemyBullet]:
        self.spiral_angle += config.SPIRAL_ROTATION * dt
        if not self.spiral_timer.tick(dt):
            return []
        speed = config.ENEMY_BULLET_SPEED * config.SPIRAL_SPEED_FACTOR
        step = 360 / config.SPIRAL_ARMS
        return [
            EnemyBullet(
                self.core_position, Vector2(speed, 0).rotate(self.spiral_angle + arm * step)
            )
            for arm in range(config.SPIRAL_ARMS)
        ]

    def _phase_three(self, dt: float) -> list[EnemyBullet]:
        bullets: list[EnemyBullet] = []
        if self.rage_fan_timer.tick(dt):
            bullets += fan(
                self.core_position,
                config.FAN_COUNT + 2,
                config.FAN_SPREAD * 1.4,
                config.ENEMY_BULLET_SPEED * 1.15,
            )
        return bullets

    def _update_laser(self, dt: float) -> None:
        self.laser_time -= dt
        if self.laser_time > 0:
            return
        if self.laser_state is LaserState.IDLE:
            self.laser_state, self.laser_time = LaserState.CHARGING, config.LASER_CHARGE_TIME
        elif self.laser_state is LaserState.CHARGING:
            self.laser_state, self.laser_time = LaserState.FIRING, config.LASER_FIRE_TIME
        else:
            self.laser_state, self.laser_time = LaserState.IDLE, config.LASER_COOLDOWN
            self.laser_direction *= -1  # le balayage suivant part de l'autre côté

    def laser_beam(self) -> tuple[Vector2, Vector2] | None:
        """Le rayon (début, fin) s'il est en train de tirer, sinon None."""
        if self.laser_state is not LaserState.FIRING or self.dying:
            return None
        progress = 1 - self.laser_time / config.LASER_FIRE_TIME
        return self._laser_segment(progress)

    def laser_warning(self) -> tuple[Vector2, Vector2] | None:
        """Le trait d'avertissement pendant la charge : il montre où le rayon va partir."""
        if self.laser_state is not LaserState.CHARGING or self.dying:
            return None
        return self._laser_segment(0.0)

    def _laser_segment(self, progress: float) -> tuple[Vector2, Vector2]:
        sweep = config.LASER_SWEEP * self.laser_direction
        angle = DOWN + lerp(-sweep, sweep, progress)
        start = self.core_position
        return start, start + Vector2(config.LASER_LENGTH, 0).rotate(angle)

    # --- Dégâts --------------------------------------------------------------------------------

    def damage(self, amount: int) -> BossHit:
        if self.invulnerable:
            return BossHit.IGNORED
        self.health = max(0, self.health - amount)
        self.flash_time = config.BOSS_HIT_FLASH_TIME
        if self.health == 0:
            self.dying_time = 0.0
            self.laser_state = LaserState.IDLE
            return BossHit.KILLED
        new_phase = phase_for(self.health_ratio)
        if new_phase > self.phase:
            self.phase = new_phase
            self.transition_time = config.BOSS_PHASE_TRANSITION_TIME
            self.laser_state, self.laser_time = LaserState.IDLE, config.LASER_COOLDOWN / 2
            return BossHit.PHASE_CHANGED
        return BossHit.DAMAGED

    def absorb_bullet(self, point: Vector2, radius: float) -> BossHit | None:
        """Teste un tir du joueur contre le boss. None si le tir ne touche rien."""
        if circles_overlap(point, radius, self.core_position, CORE_RADIUS):
            return self.damage(1)
        # Les tourelles s'activent en phase 2 : avant, elles font partie du blindage.
        for turret in self.turrets if self.phase >= 2 else ():
            if turret.alive and circles_overlap(
                point, radius, self.position + turret.offset, TURRET_RADIUS
            ):
                if self.invulnerable:
                    return BossHit.IGNORED
                turret.health -= 1
                return BossHit.TURRET_DESTROYED if not turret.alive else BossHit.TURRET_DAMAGED
        if self.touches(point, radius):
            return BossHit.ARMOR
        return None

    def touches(self, point: Vector2, radius: float) -> bool:
        """Vrai si un cercle touche la coque (cœur ou blindage)."""
        if circles_overlap(point, radius, self.core_position, CORE_RADIUS):
            return True
        return any(
            circles_overlap(point, radius, self.position + offset, size) for offset, size in ARMOR
        )

    def random_hull_point(self, rng: random.Random) -> Vector2:
        """Un point au hasard sur la coque : pour la chaîne d'explosions finale."""
        offset, size = rng.choice(ARMOR)
        return self.position + offset + Vector2(rng.uniform(0, size), 0).rotate(rng.uniform(0, 360))

    # --- Dessin --------------------------------------------------------------------------------

    def _color(self) -> Color:
        if self.transition_time > 0 and int(self.age * 16) % 2:
            return config.METEOR_HIT_COLOR  # clignote pendant qu'il change de phase
        if self.phase == 3:
            # En rage, il « pulse » entre son rouge et un rouge plus sombre.
            return neon.scale_color(config.BOSS_RAGE_COLOR, 0.75 + 0.25 * math.sin(self.age * 10))
        return config.BOSS_COLOR

    def draw(self, surface: pygame.Surface) -> None:
        color = self._color()
        position = self.position
        if self.dying_time is not None:
            # En train d'exploser : tremble et s'éteint peu à peu.
            fade = 1 - self.dying_time / config.BOSS_DEATH_DURATION
            color = neon.scale_color(color, 0.3 + 0.7 * fade)
            position = position + Vector2(math.sin(self.age * 70) * 4, math.cos(self.age * 55) * 3)

        neon.polygon(surface, color, [position + p for p in HULL])
        for start, end in PANELS:
            pygame.draw.line(
                surface, neon.scale_color(color, 0.5), position + start, position + end, 1
            )

        for turret in self.turrets:
            center = position + turret.offset
            hexagon = [
                center + Vector2(0, -TURRET_RADIUS).rotate(60 * k + self.age * 90) for k in range(6)
            ]
            if turret.alive:
                neon.polygon(surface, config.ACCENT_COLOR, hexagon)
            else:
                pygame.draw.polygon(
                    surface, neon.scale_color(config.ACCENT_COLOR, 0.25), hexagon, 1
                )

        # Le cœur : la seule zone vulnérable, qui bat comme un cœur.
        core = position + CORE_OFFSET
        beat = 1 + 0.12 * max(0.0, math.sin(self.age * (8 if self.phase == 3 else 5)))
        # Seul le cœur s'illumine quand on le touche : on voit tout de suite si on fait mal.
        core_color = config.METEOR_HIT_COLOR if self.flash_time > 0 else config.BOSS_CORE_COLOR
        pygame.draw.circle(
            surface, neon.scale_color(core_color, 0.5), core, CORE_RADIUS * 0.6 * beat
        )
        neon.circle(surface, core_color, core, CORE_RADIUS * beat)
        pygame.draw.circle(surface, config.METEOR_HIT_COLOR, core, CORE_RADIUS * 0.25 * beat)

        self._draw_laser(surface)

    def _draw_laser(self, surface: pygame.Surface) -> None:
        warning = self.laser_warning()
        if warning is not None:
            # Trait fin qui clignote de plus en plus vite : « attention, ça arrive ».
            progress = 1 - self.laser_time / config.LASER_CHARGE_TIME
            if math.sin(self.age * (20 + 40 * progress)) > 0:
                pygame.draw.line(surface, config.BOSS_RAGE_COLOR, *warning, 2)
            pygame.draw.circle(
                surface, config.BOSS_RAGE_COLOR, warning[0], CORE_RADIUS * (0.5 + progress), 2
            )
        beam = self.laser_beam()
        if beam is not None:
            width = round(config.LASER_WIDTH * (0.85 + 0.15 * math.sin(self.age * 60)))
            pygame.draw.line(surface, config.BOSS_RAGE_COLOR, *beam, width)
            pygame.draw.line(surface, neon.lighten(config.BOSS_RAGE_COLOR, 0.6), *beam, width // 2)
            pygame.draw.line(surface, config.METEOR_HIT_COLOR, *beam, max(2, width // 6))
            pygame.draw.circle(surface, config.METEOR_HIT_COLOR, beam[0], width)
