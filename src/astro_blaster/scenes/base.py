"""Ce qu'une scène doit savoir faire pour que la boucle de jeu puisse l'utiliser."""

from __future__ import annotations

from typing import Protocol

import pygame


class Scene(Protocol):
    """Un Protocol décrit une « forme » : toute classe qui a ces méthodes est une Scene,
    sans avoir besoin d'en hériter."""

    def handle_event(self, event: pygame.event.Event) -> None: ...

    def update(self, dt: float) -> Scene | None:
        """Avance d'une image. Renvoie la scène suivante pour en changer, sinon None."""
        ...

    def draw(self, surface: pygame.Surface) -> None: ...
