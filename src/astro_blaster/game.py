"""La boucle principale : lire le clavier, faire avancer la scène, dessiner, recommencer."""

import asyncio

import pygame

from astro_blaster import config
from astro_blaster.scenes.base import Scene
from astro_blaster.scenes.play import PlayScene


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(config.TITLE)
        # SCALED : on dessine toujours en 540×720, pygame agrandit si la fenêtre est plus grande.
        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE
        )
        self.clock = pygame.time.Clock()
        self.show_fps = False
        self.fps_font = pygame.font.Font(None, config.FONT_SIZE_HUD)

    async def run(self) -> None:
        """Boucle de jeu.

        Elle est `async` pour la version navigateur (pygbag) : `await asyncio.sleep(0)`
        rend la main au navigateur à chaque image, sinon la page se figerait.
        """
        scene: Scene = PlayScene()
        while True:
            # tick() attend ce qu'il faut pour tenir 60 i/s et renvoie les millisecondes écoulées.
            dt = min(self.clock.tick(config.FPS) / 1000, config.MAX_DT)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                    self.show_fps = not self.show_fps
                scene.handle_event(event)

            scene = scene.update(dt) or scene
            scene.draw(self.screen)
            if self.show_fps:
                self._draw_fps()
            pygame.display.flip()
            await asyncio.sleep(0)

    def _draw_fps(self) -> None:
        text = self.fps_font.render(f"{self.clock.get_fps():.0f} i/s", True, config.ACCENT_COLOR)
        self.screen.blit(text, text.get_rect(bottomleft=(8, config.SCREEN_HEIGHT - 8)))
