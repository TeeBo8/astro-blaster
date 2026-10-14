"""Astro Blaster : un shoot'em up néon en Python."""

import os

# Masque le message d'accueil que pygame affiche à l'import.
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")


def main() -> None:
    """Point d'entrée de la commande `astro-blaster` (voir pyproject.toml)."""
    import asyncio

    from astro_blaster.game import Game

    asyncio.run(Game().run())
