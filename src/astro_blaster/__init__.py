"""Astro Blaster : un shoot'em up néon en Python."""

import os

# Masque le message d'accueil que pygame affiche à l'import.
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")


def main() -> None:
    """Point d'entrée de la commande `astro-blaster` (voir pyproject.toml)."""
    import argparse
    import asyncio

    from astro_blaster import config
    from astro_blaster.game import Game

    # argparse lit les options de la ligne de commande et génère l'aide (--help) tout seul.
    parser = argparse.ArgumentParser(description="Shoot'em up néon en Python.")
    parser.add_argument(
        "--boss", action="store_true", help="commencer juste avant l'arrivée du boss"
    )
    options = parser.parse_args()
    start_time = config.BOSS_TRIGGER_TIME - 2 if options.boss else 0.0
    asyncio.run(Game(start_time=start_time).run())
