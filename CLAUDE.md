# CLAUDE.md - Astro Blaster (nom provisoire)

> Lu automatiquement par Claude Code à chaque session dans ce dossier.

## Le projet

Jeu de tir spatial en Python : un vaisseau qui tire sur des météorites. Simple à jouer, mais **très soigné visuellement** (« gavé stylé »).

- **But** : premier projet Python de Leture, pour s'entraîner avant l'API FastAPI + LLM (projet suivant). Un joli repo 100 % Python que d'autres devs ont envie de cloner pour s'amuser, et qui étoffe le GitHub TeeBo8.
- **Diffusion** : repo **public** sur GitHub (TeeBo8/astro-blaster), et jouable dans le navigateur sur teebostudio.fr (export WebAssembly avec **pygbag**, à prévoir dès l'architecture : boucle principale `async`).
- **Historique** : Leture avait déjà fait un jeu de ce type à l'époque, il marchait bien, repo supprimé depuis.
- **Nom** : « astro-blaster » est provisoire. Pour renommer avant la publication : `name` et `[project.scripts]` dans `pyproject.toml`, le dossier `src/astro_blaster/`, puis `uv sync`.

## État au 2026-10-14

- Consignes de Leture et étapes : voir `TODO.md` (shoot'em up vertical, flèches + Espace, style néon vectoriel dessiné en code, difficulté progressive, boss en 3 phases, 3 bonus)
- Phases 1 à 3 (jeu, néon, boss) validées par Leture ; PR #1, #2, #3 empilées à fusionner dans l'ordre. Repo GitHub TeeBo8/astro-blaster créé en **privé** (Leture le passera en public)
- Phase 4 (version navigateur, README) sur `feat/web`
- Dépendances : `pygame-ce` ; dev : `ruff`, `pytest`
- Organisation : réglages dans `config.py`, logique pure testée (`geometry`, `difficulty`, `scoring`), `entities/`, `scenes/` (Protocol `Scene`, `update` renvoie la scène suivante), `fx/` (néon, particules, son synthétisé), `director.py` (cycles et boss)

## Pièges de la version navigateur (pygbag)

- Importer `from pygame import Vector2`, jamais `from pygame.math import …` : pygbag croit que `pygame.math` est un paquet PyPI
- Les dépendances se déclarent dans le bloc PEP 723 de `web/main.py`
- Le navigateur impose son mixeur (48 kHz) : la synthèse des sons prend quelques secondes, d'où l'écran « CHARGEMENT »
- Tester avec le mode debug : `http://localhost:8000/#debug` affiche le terminal Python

## Stack

| Rôle | Outil |
|---|---|
| Langage | Python 3.13 (`.python-version`) |
| Gestion du projet | uv (équivalent de pnpm) |
| Moteur de jeu | pygame-ce (version communautaire de pygame, plus active ; s'importe avec `import pygame`) |
| Lint + formatage | Ruff (config dans `pyproject.toml`) |
| Tests | pytest (logique pure : collisions, score, vagues — pas l'affichage) |
| Version navigateur | pygbag 0.9 (Python 3.12 + pygame-ce 2.5.7 en WebAssembly) |

## Commandes

```powershell
uv run astro-blaster      # lancer le jeu (--boss : commencer juste avant le boss)
uv run ruff check         # lint (équivalent pnpm lint)
uv run ruff format        # formatage
uv run pytest             # tests
uv add <paquet>           # ajouter une dépendance (--dev pour l'outillage)
uv run python scripts/build_web.py          # version navigateur sur http://localhost:8000
uv run python scripts/build_web.py --build  # construit seulement : build/web-src/build/web
```

## Checklist avant de pousser

1. `uv run ruff check` : 0 erreur
2. `uv run ruff format --check` : rien à reformater
3. `uv run pytest` : tout vert
4. Le jeu se lance et Leture l'a testé sur sa machine

## Règles du projet

- **Leture apprend Python** : expliquer les notions propres à Python au fil de l'eau (dataclasses, typage, `async`, organisation en paquet `src/`…) et dans la fiche du journal `D:\_journal\astro-blaster\`.
- Code lisible et typé (annotations partout), noms en anglais dans le code, commentaires en français.
- Un fichier par responsabilité (vaisseau, météorites, tirs, particules, scènes…), pas de fichier fourre-tout.
- Pas de « nombres magiques » éparpillés : réglages (vitesses, couleurs, tailles) dans un module de configuration.
- Visuel : priorité au ressenti (particules, tremblement d'écran, fond étoilé en parallaxe, météorites qui se fragmentent, sons). Assets libres de droits uniquement (CC0, ex. Kenney.nl), crédités dans le README.
- 60 images/seconde stables : mouvements multipliés par le temps écoulé (`dt`), pas par image.
- Branches + PR comme sur les autres projets ; standard des repos du CLAUDE.md global (README français avec GIF de démo, description, sujets GitHub).
- C'est Leture qui crée le repo public et le bascule en public.

## Utilisateur cible

- Profil : développeurs curieux qui découvrent le repo sur GitHub, visiteurs de teebostudio.fr (prospects de l'agence)
- Niveau technique : de débutant (joue dans le navigateur) à intermédiaire (clone et lit le code)
- Contexte d'usage : desktop (clavier) en priorité ; mobile seulement si la version navigateur le permet simplement
- Douleur principale : s'amuser 2 minutes ; pour les devs, trouver un exemple de jeu Python propre et lisible
