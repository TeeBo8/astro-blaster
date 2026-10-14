"""Construit la version navigateur du jeu avec pygbag.

pygbag emballe tout le contenu d'un dossier. On prépare donc un dossier propre,
build/web-src, avec seulement web/main.py et le paquet du jeu (sans .venv ni tests).

    uv run python scripts/build_web.py           # construit et lance http://localhost:8000
    uv run python scripts/build_web.py --build   # construit seulement (build/web-src/build/web)
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "build" / "web-src"


def main() -> None:
    shutil.rmtree(SOURCE, ignore_errors=True)
    shutil.copytree(
        ROOT / "src" / "astro_blaster",
        SOURCE / "astro_blaster",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy(ROOT / "web" / "main.py", SOURCE / "main.py")
    command = [sys.executable, "-m", "pygbag", "--title", "Astro Blaster", *sys.argv[1:], SOURCE]
    subprocess.run([str(part) for part in command], check=True)


if __name__ == "__main__":
    main()
