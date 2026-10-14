"""Petits textes qui montent et s'effacent : « +100 », « TIR TRIPLE », « +1 VIE »…"""

from dataclasses import dataclass

import pygame
from pygame import Vector2

from astro_blaster import config
from astro_blaster.config import Color


@dataclass(slots=True)
class Popup:
    image: pygame.Surface
    position: Vector2
    life: float


class Popups:
    def __init__(self, font: pygame.Font) -> None:
        self.font = font
        self.items: list[Popup] = []

    def add(self, message: str, position: Vector2, color: Color) -> None:
        image = self.font.render(message, True, color)
        self.items.append(Popup(image, position.copy(), config.POPUP_LIFE))

    def update(self, dt: float) -> None:
        for item in self.items:
            item.life -= dt
            item.position.y -= config.POPUP_RISE_SPEED * dt
        self.items = [item for item in self.items if item.life > 0]

    def draw(self, surface: pygame.Surface) -> None:
        for item in self.items:
            item.image.set_alpha(round(255 * min(1.0, item.life / config.POPUP_LIFE * 2)))
            surface.blit(item.image, item.image.get_rect(center=item.position))
