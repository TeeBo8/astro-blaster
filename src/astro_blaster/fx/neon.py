"""Rendu néon : des traits « tubes lumineux » et un halo (bloom) sur toute l'image."""

from collections.abc import Sequence

import pygame
from pygame import Vector2

from astro_blaster import config
from astro_blaster.config import Color

Point = Vector2 | tuple[float, float]


def lighten(color: Color, amount: float) -> Color:
    """Rapproche une couleur du blanc (amount = 0 : inchangée, 1 : blanc)."""
    red, green, blue = (round(c + (255 - c) * amount) for c in color)
    return (red, green, blue)


def scale_color(color: Color, factor: float) -> Color:
    """Assombrit (factor < 1) une couleur."""
    red, green, blue = (round(min(255, c * factor)) for c in color)
    return (red, green, blue)


def polygon(surface: pygame.Surface, color: Color, points: Sequence[Point]) -> None:
    """Contour néon : un trait coloré épais, puis un cœur fin presque blanc par-dessus."""
    pygame.draw.polygon(surface, color, points, config.NEON_LINE_WIDTH)
    pygame.draw.polygon(surface, lighten(color, config.NEON_CORE_LIGHTEN), points, 1)


def line(surface: pygame.Surface, color: Color, start: Point, end: Point) -> None:
    pygame.draw.line(surface, color, start, end, config.NEON_LINE_WIDTH)
    pygame.draw.line(surface, lighten(color, config.NEON_CORE_LIGHTEN), start, end, 1)


def circle(surface: pygame.Surface, color: Color, center: Point, radius: float) -> None:
    pygame.draw.circle(surface, color, center, radius, config.NEON_LINE_WIDTH)
    pygame.draw.circle(surface, lighten(color, config.NEON_CORE_LIGHTEN), center, radius, 1)


def text(
    surface: pygame.Surface,
    font: pygame.Font,
    message: str,
    color: Color,
    **position: tuple[float, float],
) -> pygame.Rect:
    """Écrit un texte. `position` se passe comme pour un Rect : center=(x, y), topleft=…

    Le halo vient tout seul du bloom, appliqué à la fin de l'image.
    """
    image = font.render(message, True, color)
    rect = image.get_rect(**position)
    surface.blit(image, rect)
    return rect


class Bloom:
    """Halo lumineux autour de tout ce qui brille.

    Principe : on réduit l'image, on la floute (le flou coûte bien moins cher sur une petite
    image), on la ré-agrandit et on l'ajoute par-dessus l'original. Les zones claires
    « bavent » alors sur le noir, comme un vrai néon.
    """

    def __init__(self, size: tuple[int, int]) -> None:
        width, height = size
        self.full = pygame.Surface(size)
        # Pour chaque passe, deux petites surfaces réutilisées à chaque image (pas d'allocation).
        self.passes = [
            (
                pygame.Surface((width // factor, height // factor)),
                pygame.Surface((width // factor, height // factor)),
                radius,
                iterations,
                strength,
            )
            for factor, radius, iterations, strength in config.BLOOM_PASSES
        ]

    def apply(self, surface: pygame.Surface) -> None:
        for small, spare, radius, iterations, strength in self.passes:
            pygame.transform.smoothscale(surface, small.get_size(), dest_surface=small)
            # Un flou « boîte » répété ressemble beaucoup à un flou gaussien,
            # pour 5 à 10 fois moins cher.
            for _ in range(iterations):
                pygame.transform.box_blur(small, radius, dest_surface=spare)
                small, spare = spare, small
            if strength < 255:
                small.fill((strength, strength, strength), special_flags=pygame.BLEND_RGB_MULT)
            pygame.transform.smoothscale(small, self.full.get_size(), dest_surface=self.full)
            surface.blit(self.full, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
