"""Particules : explosions, étincelles, onde de choc, traînée du moteur.

Une particule vit quelques dixièmes de seconde : elle part vite, freine, rétrécit et s'éteint.
"""

import math
import random
from dataclasses import dataclass

import pygame
from pygame import Vector2

from astro_blaster import config
from astro_blaster.config import Color
from astro_blaster.fx import neon


@dataclass(slots=True)
class Particle:
    """`slots=True` : Python ne crée pas de dictionnaire par objet, c'est plus léger et plus
    rapide quand on en a des centaines."""

    position: Vector2
    velocity: Vector2
    color: Color
    life: float
    max_life: float
    size: float
    streak: bool  # étincelle : dessinée en trait dans le sens du mouvement


@dataclass(slots=True)
class Ring:
    """Onde de choc : un cercle qui grandit et s'efface."""

    position: Vector2
    color: Color
    max_radius: float
    life: float
    max_life: float


class ParticleSystem:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.particles: list[Particle] = []
        self.rings: list[Ring] = []
        self.engine_budget = 0.0

    def _add(self, particle: Particle) -> None:
        if len(self.particles) < config.PARTICLE_MAX:
            self.particles.append(particle)

    def _burst(
        self,
        position: Vector2,
        color: Color,
        count: int,
        speed: tuple[float, float],
        life: tuple[float, float],
        size: tuple[float, float],
        streak_ratio: float,
    ) -> None:
        rng = self.rng
        for _ in range(count):
            velocity = Vector2(rng.uniform(*speed), 0).rotate(rng.uniform(0, 360))
            duration = rng.uniform(*life)
            self._add(
                Particle(
                    position.copy(),
                    velocity,
                    color,
                    duration,
                    duration,
                    rng.uniform(*size),
                    rng.random() < streak_ratio,
                )
            )

    def explosion(self, position: Vector2, color: Color, radius: float) -> None:
        """Explosion proportionnelle à la taille de ce qui explose."""
        count = round(radius * config.EXPLOSION_PARTICLES_PER_RADIUS) + 8
        self._burst(
            position, color, count, config.EXPLOSION_SPEED, config.EXPLOSION_LIFE, (1.5, 3.5), 0.5
        )
        # Quelques éclats blancs, plus rapides : le « cœur » chaud de l'explosion.
        self._burst(
            position,
            config.METEOR_HIT_COLOR,
            count // 3,
            (config.EXPLOSION_SPEED[1] * 0.6, config.EXPLOSION_SPEED[1] * 1.3),
            config.SPARK_LIFE,
            (1.0, 2.0),
            1.0,
        )
        self.ring(position, color, radius * 2.2)

    def sparks(self, position: Vector2, color: Color) -> None:
        self._burst(
            position,
            color,
            config.SPARK_COUNT,
            config.SPARK_SPEED,
            config.SPARK_LIFE,
            (1.0, 2.0),
            1.0,
        )

    def ring(
        self,
        position: Vector2,
        color: Color,
        max_radius: float,
        duration: float = config.RING_DURATION,
    ) -> None:
        self.rings.append(Ring(position.copy(), color, max_radius, duration, duration))

    def engine(self, dt: float, position: Vector2) -> None:
        """Traînée continue du réacteur : un nombre de particules par seconde, pas par image."""
        self.engine_budget += config.ENGINE_PARTICLES_PER_SECOND * dt
        while self.engine_budget >= 1:
            self.engine_budget -= 1
            velocity = Vector2(self.rng.uniform(-25, 25), self.rng.uniform(*config.ENGINE_SPEED))
            duration = self.rng.uniform(*config.ENGINE_LIFE)
            self._add(
                Particle(
                    position + Vector2(self.rng.uniform(-3, 3), 0),
                    velocity,
                    config.FLAME_COLOR,
                    duration,
                    duration,
                    self.rng.uniform(1.5, 3.0),
                    False,
                )
            )

    def update(self, dt: float) -> None:
        # Freinage exponentiel : indépendant du nombre d'images par seconde.
        drag = math.exp(-config.PARTICLE_DRAG * dt)
        for particle in self.particles:
            particle.life -= dt
            particle.velocity *= drag
            particle.position += particle.velocity * dt
        self.particles = [p for p in self.particles if p.life > 0]
        for ring in self.rings:
            ring.life -= dt
        self.rings = [r for r in self.rings if r.life > 0]

    def draw(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            fade = particle.life / particle.max_life  # de 1 (naissance) à 0 (mort)
            color = neon.scale_color(particle.color, 0.35 + 0.65 * fade)
            if particle.streak:
                tail = particle.position - particle.velocity * 0.03
                pygame.draw.line(surface, color, particle.position, tail, 2)
            else:
                pygame.draw.circle(surface, color, particle.position, particle.size * fade + 0.5)
        for ring in self.rings:
            progress = 1 - ring.life / ring.max_life
            # Le cercle ralentit en grandissant (racine carrée), comme une vraie onde de choc.
            radius = ring.max_radius * math.sqrt(progress)
            width = max(1, round(4 * (1 - progress)))
            color = neon.scale_color(ring.color, 1 - progress)
            pygame.draw.circle(surface, color, ring.position, radius, width)
