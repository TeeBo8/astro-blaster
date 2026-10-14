"""Petites fonctions mathématiques, sans rien afficher (donc faciles à tester)."""

import random

from pygame.math import Vector2


def clamp(value: float, low: float, high: float) -> float:
    """Ramène value dans l'intervalle [low, high]."""
    return max(low, min(high, value))


def lerp(start: float, end: float, t: float) -> float:
    """Interpolation linéaire : t = 0 donne start, t = 1 donne end (t > 1 prolonge la droite)."""
    return start + (end - start) * t


def progress_between(value: float, start: float, end: float) -> float:
    """Où en est value entre start et end, de 0 à 1 (borné)."""
    return clamp((value - start) / (end - start), 0.0, 1.0)


def circles_overlap(a: Vector2, radius_a: float, b: Vector2, radius_b: float) -> bool:
    """Vrai si deux cercles se touchent.

    On compare les carrés des distances : même résultat, sans racine carrée à calculer.
    """
    reach = radius_a + radius_b
    return a.distance_squared_to(b) <= reach * reach


def random_polygon(
    rng: random.Random, radius: float, vertex_count: int, jaggedness: float
) -> list[Vector2]:
    """Contour irrégulier de rayon au plus `radius`, centré sur (0, 0).

    Les sommets sont répartis autour du cercle, chacun à une distance un peu au hasard.
    """
    step = 360.0 / vertex_count
    points: list[Vector2] = []
    for index in range(vertex_count):
        angle = index * step + rng.uniform(-step * 0.3, step * 0.3)
        distance = radius * rng.uniform(1.0 - jaggedness, 1.0)
        points.append(Vector2(0, -distance).rotate(angle))
    return points


def distance_to_segment(point: Vector2, start: Vector2, end: Vector2) -> float:
    """Distance la plus courte entre un point et un segment (sert à toucher avec un laser).

    On projette le point sur la droite du segment, puis on borne la projection aux extrémités.
    """
    segment = end - start
    length_squared = segment.length_squared()
    if length_squared == 0:
        return point.distance_to(start)
    t = clamp((point - start).dot(segment) / length_squared, 0.0, 1.0)
    return point.distance_to(start + segment * t)
