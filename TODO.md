# TODO - Astro Blaster

> Consignes de Leture (2026-10-14) : shoot'em up vertical, flèches + Espace, difficulté qui monte
> nettement, boss spectaculaire, 3 bonus (tir triple, bouclier, bombe), score + record, style néon
> vectoriel dessiné en code.

## Phase 0 - Fondations
- [x] Initialiser le projet (uv, Python 3.13, pygame-ce, ruff, pytest)
- [x] Recevoir les consignes de Leture (style, commandes, contenu)
- [ ] Choisir le nom définitif
- [x] Organisation du code validée par Leture

## Phase 1 - Jeu jouable (`feat/jeu-jouable`)
- [x] Fenêtre, boucle de jeu async à 60 images/s
- [x] Vaisseau qui se déplace et tire
- [x] Météorites, collisions, score, vies, game over
- [x] Difficulté progressive (facile au début, de plus en plus dur)

## Phase 2 - « Gavé stylé » (`feat/neon`)
- [ ] Rendu néon avec halos lumineux
- [ ] Fond étoilé en parallaxe, particules, tremblement d'écran, hit-stop
- [x] Météorites qui se fragmentent (fait en phase 1)
- [ ] Bonus : tir triple, bouclier, bombe
- [ ] Sons, musique
- [ ] Écran titre, record sauvegardé

## Phase 3 - Le boss (`feat/boss`)
- [ ] Alerte « WARNING », boss en 3 phases, barre de vie
- [ ] Mort spectaculaire, cycles plus durs après le boss

## Phase 4 - Publication
- [ ] Version navigateur (pygbag), record dans le stockage du navigateur
- [ ] README (GIF de démo, stack, commandes, crédits des assets)
- [ ] Revue à froid
- [ ] Repo GitHub public + description + sujets (Leture)
- [ ] Page sur teebostudio.fr
