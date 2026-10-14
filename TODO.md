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
- [x] Rendu néon avec halos lumineux
- [x] Fond étoilé en parallaxe, particules, tremblement d'écran, hit-stop
- [x] Météorites qui se fragmentent (fait en phase 1)
- [x] Bonus : tir triple, bouclier, bombe
- [x] Sons et musique synthétisés en code (aucun fichier audio)
- [x] Écran titre, record sauvegardé

## Phase 3 - Le boss (`feat/boss`)
- [x] Alerte « WARNING », boss en 3 phases, barre de vie
- [x] Mort spectaculaire, cycles plus durs après le boss (+1 vie offerte)

## Phase 4 - Publication
- [x] Version navigateur (pygbag), record dans le stockage du navigateur
- [x] README (GIF de démo, stack, commandes, crédits des assets)
- [ ] Licence du code (MIT ?) à choisir par Leture
- [ ] Revue à froid
- [ ] Repo GitHub public + description + sujets (Leture)
- [ ] Page sur teebostudio.fr
