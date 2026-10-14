"""Écran de fin de partie."""

from collections.abc import Callable

import pygame

from astro_blaster import config
from astro_blaster.scenes.base import Scene
from astro_blaster.scoring import format_points


class GameOverScene:
    def __init__(self, score: int, elapsed: float, restart: Callable[[], Scene]) -> None:
        self.score = score
        self.elapsed = elapsed
        self.restart = restart
        self.wait = config.GAME_OVER_INPUT_DELAY
        self.wants_restart = False
        self.title_font = pygame.font.Font(None, config.FONT_SIZE_TITLE)
        self.text_font = pygame.font.Font(None, config.FONT_SIZE_TEXT)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.wait == 0:
            self.wants_restart = True

    def update(self, dt: float) -> Scene | None:
        self.wait = max(0.0, self.wait - dt)
        return self.restart() if self.wants_restart else None

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(config.BACKGROUND_COLOR)
        center_x = config.SCREEN_WIDTH / 2
        minutes, seconds = divmod(int(self.elapsed), 60)
        lines = [
            (self.title_font, "GAME OVER", config.METEOR_COLOR, 0.35),
            (self.text_font, f"Score : {format_points(self.score)}", config.HUD_COLOR, 0.5),
            (self.text_font, f"Temps : {minutes}:{seconds:02d}", config.HUD_COLOR, 0.56),
        ]
        if self.wait == 0:
            lines.append((self.text_font, "Espace pour rejouer", config.ACCENT_COLOR, 0.72))
        for font, text, color, height in lines:
            image = font.render(text, True, color)
            surface.blit(image, image.get_rect(center=(center_x, config.SCREEN_HEIGHT * height)))
