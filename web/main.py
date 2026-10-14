"""Point d'entrée de la version navigateur (pygbag).

pygbag cherche un fichier main.py qui lance une boucle `async` avec asyncio.run().
Ne pas lancer ce fichier directement : passer par `uv run python scripts/build_web.py`.
"""

# Dépendances de la version navigateur, au format standard PEP 723 : pygbag lit ce bloc
# pour savoir quels paquets installer dans le navigateur.
# /// script
# dependencies = ["pygame-ce"]
# ///

import asyncio

from astro_blaster.game import Game

asyncio.run(Game().run())
