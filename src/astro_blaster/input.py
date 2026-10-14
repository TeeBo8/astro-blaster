"""Traduit l'état du clavier en intentions de jeu (se déplacer, tirer)."""

from dataclasses import dataclass

import pygame
from pygame.math import Vector2


@dataclass(frozen=True)
class Controls:
    move: Vector2  # direction voulue, de longueur 0 ou 1
    fire: bool


def read_controls() -> Controls:
    keys = pygame.key.get_pressed()
    move = Vector2(
        keys[pygame.K_RIGHT] - keys[pygame.K_LEFT],
        keys[pygame.K_DOWN] - keys[pygame.K_UP],
    )
    # En diagonale, on normalise : sinon le vaisseau irait 1,4 fois plus vite.
    if move.length_squared() > 0:
        move.normalize_ip()
    return Controls(move=move, fire=bool(keys[pygame.K_SPACE]))
