"""La boucle principale : lire le clavier, faire avancer la scène, dessiner, recommencer."""

import asyncio

import pygame

from astro_blaster import config
from astro_blaster.context import FONTS_DIR, GameContext
from astro_blaster.fx.neon import Bloom
from astro_blaster.scenes.base import Scene
from astro_blaster.scenes.title import TitleScene


class Game:
    def __init__(self, start_time: float = 0.0) -> None:
        # Réglages du son à donner AVANT pygame.init() : mono, 16 bits, petit tampon
        # (un petit tampon = moins de délai entre l'action et le son).
        pygame.mixer.pre_init(config.SAMPLE_RATE, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption(config.TITLE)
        # SCALED : on dessine toujours en 540×720, pygame agrandit si la fenêtre est plus grande.
        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE
        )
        self.clock = pygame.time.Clock()
        self.start_time = start_time
        self.bloom = Bloom(self.screen.get_size())
        self.small_font = pygame.Font(FONTS_DIR / config.FONT_FILE, config.FONT_SIZE_POPUP)
        self.show_fps = False

    async def load(self) -> GameContext:
        """Affiche « CHARGEMENT » pendant la synthèse des sons (plusieurs secondes en ligne)."""
        font = pygame.Font(FONTS_DIR / config.FONT_FILE, config.FONT_SIZE_TEXT)
        self.screen.fill(config.BACKGROUND_COLOR)
        text = font.render("CHARGEMENT...", True, config.SHIP_COLOR)
        self.screen.blit(text, text.get_rect(center=self.screen.get_rect().center))
        self.bloom.apply(self.screen)
        pygame.display.flip()
        # Dans le navigateur, l'image n'apparaît que lorsqu'on rend la main : on la rend ici.
        await asyncio.sleep(0)
        return GameContext(start_time=self.start_time)

    async def run(self) -> None:
        """Boucle de jeu.

        Elle est `async` pour la version navigateur (pygbag) : `await asyncio.sleep(0)`
        rend la main au navigateur à chaque image, sinon la page se figerait.
        """
        context = await self.load()
        scene: Scene = TitleScene(context)
        while True:
            # tick() attend ce qu'il faut pour tenir 60 i/s et renvoie les millisecondes écoulées.
            dt = min(self.clock.tick(config.FPS) / 1000, config.MAX_DT)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    self._handle_global_key(event.key, context)
                scene.handle_event(event)

            scene = scene.update(dt) or scene
            scene.draw(self.screen)
            self.bloom.apply(self.screen)
            if self.show_fps:
                self._draw_fps()
            pygame.display.flip()
            await asyncio.sleep(0)

    def _handle_global_key(self, key: int, context: GameContext) -> None:
        """Touches valables sur tous les écrans."""
        if key == pygame.K_m:
            context.audio.toggle_mute()
        elif key == pygame.K_F3:
            self.show_fps = not self.show_fps
        elif key == pygame.K_F11:
            pygame.display.toggle_fullscreen()

    def _draw_fps(self) -> None:
        text = self.small_font.render(f"{self.clock.get_fps():.0f} i/s", True, config.ACCENT_COLOR)
        self.screen.blit(text, text.get_rect(bottomleft=(8, config.SCREEN_HEIGHT - 8)))
