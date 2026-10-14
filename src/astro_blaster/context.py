"""Ce que toutes les scènes partagent : son, polices, fond étoilé, record."""

import random
from dataclasses import dataclass
from pathlib import Path

import pygame

from astro_blaster import config
from astro_blaster.fx.audio import Audio
from astro_blaster.fx.starfield import Starfield
from astro_blaster.scoring import default_save_path, load_high_score, save_high_score

FONTS_DIR = Path(__file__).parent / "assets" / "fonts"


@dataclass
class Fonts:
    popup: pygame.Font
    hud: pygame.Font
    text: pygame.Font
    title: pygame.Font

    @classmethod
    def load(cls) -> "Fonts":
        """`@classmethod` : une autre façon de construire l'objet, ici en chargeant les polices."""
        path = FONTS_DIR / config.FONT_FILE
        return cls(
            popup=pygame.Font(path, config.FONT_SIZE_POPUP),
            hud=pygame.Font(path, config.FONT_SIZE_HUD),
            text=pygame.Font(path, config.FONT_SIZE_TEXT),
            title=pygame.Font(path, config.FONT_SIZE_TITLE),
        )


class GameContext:
    def __init__(self, save_path: Path | None = None) -> None:
        self.audio = Audio()
        self.fonts = Fonts.load()
        # Un seul fond étoilé pour tout le jeu : il continue de défiler entre les écrans.
        self.starfield = Starfield(random.Random())
        self.save_path = save_path or default_save_path()
        self.high_score = load_high_score(self.save_path)

    def submit_score(self, score: int) -> bool:
        """Enregistre le score s'il bat le record. Renvoie True si c'est un nouveau record."""
        if score <= self.high_score:
            return False
        self.high_score = score
        save_high_score(self.save_path, score)
        return True
