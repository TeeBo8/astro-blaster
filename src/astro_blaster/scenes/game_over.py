"""Écran de fin de partie."""

import math

import pygame

from astro_blaster import config
from astro_blaster.context import GameContext
from astro_blaster.fx import neon
from astro_blaster.scenes.base import Scene
from astro_blaster.scoring import format_points


class GameOverScene:
    def __init__(self, context: GameContext, score: int, elapsed: float) -> None:
        self.context = context
        self.score = score
        self.elapsed = elapsed
        self.is_record = context.submit_score(score)
        self.wait = config.GAME_OVER_INPUT_DELAY
        self.age = 0.0
        self.next: str | None = None
        context.audio.stop_music()
        context.audio.play("game_over")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.wait > 0:
            return
        if event.key == pygame.K_SPACE:
            self.next = "play"
        elif event.key == pygame.K_ESCAPE:
            self.next = "title"

    def update(self, dt: float) -> Scene | None:
        # Imports placés ici : play.py importe déjà ce fichier. Les mettre en haut créerait
        # un import circulaire (A importe B qui importe A).
        from astro_blaster.scenes.play import PlayScene
        from astro_blaster.scenes.title import TitleScene

        self.wait = max(0.0, self.wait - dt)
        self.age += dt
        self.context.starfield.update(dt)
        if self.next == "play":
            return PlayScene(self.context)
        if self.next == "title":
            return TitleScene(self.context)
        return None

    def draw(self, surface: pygame.Surface) -> None:
        self.context.starfield.draw(surface)
        fonts = self.context.fonts
        center_x = config.SCREEN_WIDTH / 2
        height = config.SCREEN_HEIGHT
        minutes, seconds = divmod(int(self.elapsed), 60)

        neon.text(
            surface, fonts.title, "GAME OVER", config.DANGER_COLOR, center=(center_x, height * 0.3)
        )
        neon.text(
            surface,
            fonts.title,
            format_points(self.score),
            config.HUD_COLOR,
            center=(center_x, height * 0.45),
        )
        neon.text(
            surface,
            fonts.text,
            f"Temps  {minutes}:{seconds:02d}",
            config.HUD_COLOR,
            center=(center_x, height * 0.53),
        )
        if self.is_record:
            # Clignote deux fois par seconde.
            if math.sin(self.age * 4 * math.pi) > -0.3:
                neon.text(
                    surface,
                    fonts.text,
                    "NOUVEAU RECORD !",
                    config.ACCENT_COLOR,
                    center=(center_x, height * 0.6),
                )
        else:
            neon.text(
                surface,
                fonts.text,
                f"Record  {format_points(self.context.high_score)}",
                config.SHIP_COLOR,
                center=(center_x, height * 0.6),
            )
        if self.wait == 0:
            neon.text(
                surface,
                fonts.text,
                "ESPACE  rejouer",
                config.ACCENT_COLOR,
                center=(center_x, height * 0.76),
            )
            neon.text(
                surface,
                fonts.hud,
                "ÉCHAP  menu",
                config.HUD_COLOR,
                center=(center_x, height * 0.82),
            )
