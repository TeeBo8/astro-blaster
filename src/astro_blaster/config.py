"""Tous les réglages du jeu, au même endroit.

Équilibrage, vitesses, couleurs, son : tout se règle ici. Seuls quelques petits détails de
dessin (décalages, épaisseurs) restent à côté du code qui dessine.
Unités : pixels, secondes, pixels par seconde, degrés.
"""

# --- Écran -------------------------------------------------------------------------------------

TITLE = "Astro Blaster"
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 720
FPS = 60
# Un dt plus grand (fenêtre déplacée, machine qui rame) est ramené à cette valeur,
# sinon les objets « téléportent » à travers les collisions.
MAX_DT = 1 / 20

# --- Couleurs (R, V, B) ------------------------------------------------------------------------

Color = tuple[int, int, int]

BACKGROUND_COLOR: Color = (4, 3, 14)
SHIP_COLOR: Color = (0, 240, 255)
FLAME_COLOR: Color = (255, 140, 40)
BULLET_COLOR: Color = (255, 200, 70)
METEOR_COLORS: tuple[Color, Color, Color] = ((255, 90, 170), (255, 60, 220), (180, 90, 255))
METEOR_HIT_COLOR: Color = (255, 255, 255)
HUD_COLOR: Color = (220, 230, 255)
ACCENT_COLOR: Color = (255, 220, 60)
DANGER_COLOR: Color = (255, 50, 70)
TRIPLE_SHOT_COLOR: Color = (255, 220, 60)
SHIELD_COLOR: Color = (80, 255, 160)
BOMB_COLOR: Color = (255, 110, 40)
NEBULA_COLORS: tuple[Color, ...] = ((90, 20, 140), (20, 40, 130), (130, 20, 90))
OVERLAY_ALPHA = 160  # opacité du voile noir de la pause et du game over (0 à 255)

# --- Textes ------------------------------------------------------------------------------------

FONT_FILE = "Audiowide-Regular.ttf"  # police arcade, licence OFL (assets/fonts/OFL.txt)
FONT_SIZE_POPUP = 15
FONT_SIZE_HUD = 20
FONT_SIZE_TEXT = 22
FONT_SIZE_TITLE = 50
HUD_MARGIN = 14
POPUP_LIFE = 0.8  # durée d'affichage des « +100 »
POPUP_RISE_SPEED = 45.0

# --- Néon --------------------------------------------------------------------------------------

NEON_LINE_WIDTH = 3
NEON_CORE_LIGHTEN = 0.65  # le cœur du trait tire vers le blanc, comme un vrai tube néon
# Halo (bloom) : (réduction de l'image, rayon du flou, nombre de flous, intensité 0-255).
# Une petite réduction donne un halo serré, une grande un halo large et doux.
BLOOM_PASSES = ((2, 2, 1, 200), (4, 3, 2, 255))

# --- Fond étoilé -------------------------------------------------------------------------------

# Couches de parallaxe : (nombre d'étoiles, vitesse, taille, luminosité 0-255).
STAR_LAYERS = ((70, 18.0, 1, 90), (40, 45.0, 1, 170), (18, 95.0, 2, 255))
STAR_STREAK_FACTOR = 0.03  # longueur de la traînée des étoiles rapides, selon leur vitesse
STAR_DIFFICULTY_BOOST = 1.2  # le fond défile plus vite quand la difficulté monte
NEBULA_COUNT = 3
NEBULA_RADIUS = (130, 220)
NEBULA_SPEED = 7.0
NEBULA_BRIGHTNESS = 0.22  # les nébuleuses sont ajoutées à la lumière du fond, très atténuées

# --- Particules et impacts ---------------------------------------------------------------------

PARTICLE_MAX = 1500
PARTICLE_DRAG = 2.2  # freinage des particules (par seconde)
EXPLOSION_PARTICLES_PER_RADIUS = 0.9
EXPLOSION_SPEED = (60.0, 330.0)
EXPLOSION_LIFE = (0.35, 0.9)
SPARK_COUNT = 6  # étincelles quand un tir touche sans détruire
SPARK_SPEED = (80.0, 240.0)
SPARK_LIFE = (0.12, 0.3)
RING_DURATION = 0.4
ENGINE_PARTICLES_PER_SECOND = 70.0
ENGINE_SPEED = (90.0, 160.0)
ENGINE_LIFE = (0.12, 0.28)

SHAKE_MAX_OFFSET = 14.0
SHAKE_DECAY = 1.8  # « traumatisme » perdu par seconde
METEOR_SHAKE = (0.12, 0.25, 0.45)  # par taille de météorite détruite
SHIP_HIT_SHAKE = 0.8
BOMB_SHAKE = 1.0
HITSTOP_DURATION = 0.05  # micro-pause sur les gros impacts : on « sent » le choc
FLASH_DECAY = 3.5  # vitesse à laquelle le flash blanc s'efface
BOMB_FLASH = 0.35
SHIP_HIT_FLASH = 0.25
SHIP_DEATH_FLASH = 0.4

# --- Bonus -------------------------------------------------------------------------------------

POWERUP_DROP_CHANCE = (0.03, 0.09, 0.2)  # par taille de météorite détruite
POWERUP_WEIGHTS = (0.45, 0.35, 0.2)  # tir triple, bouclier, bombe
POWERUP_FALL_SPEED = 85.0
POWERUP_RADIUS = 14.0
POWERUP_SPIN = 70.0
POWERUP_BOB = (6.0, 4.0)  # oscillation latérale : (amplitude, radians par seconde)
TRIPLE_SHOT_DURATION = 10.0
TRIPLE_SHOT_SPREAD = 11.0  # angle des tirs latéraux
SHIELD_RADIUS = 27.0
SHIELD_BREAK_INVINCIBLE_TIME = 1.0
BOMB_RING_RADIUS = 700.0

# --- Mort du vaisseau --------------------------------------------------------------------------

DEATH_DURATION = 1.8  # ralenti avant l'écran de fin
DEATH_TIME_SCALE = 0.35

# --- Son ---------------------------------------------------------------------------------------
# Tous les sons sont synthétisés au lancement (fx/synth.py) : aucun fichier audio.

SAMPLE_RATE = 22050
SFX_VOLUME = 0.55
MUSIC_VOLUME = 0.32
MUSIC_BPM = 118
BOSS_MUSIC_BPM = 138

# --- Vaisseau ----------------------------------------------------------------------------------

SHIP_SPEED = 340.0
SHIP_RESPONSIVENESS = 14.0  # plus c'est haut, moins il y a d'inertie
SHIP_HITBOX_RADIUS = 9.0  # plus petit que le dessin : les frôlements ne tuent pas
SHIP_BOTTOM_MARGIN = 60.0
SHIP_TOP_LIMIT = SCREEN_HEIGHT * 0.45  # le vaisseau reste dans le bas de l'écran
SHIP_SIDE_MARGIN = 18.0
SHIP_MAX_TILT = 14.0  # inclinaison du dessin à pleine vitesse latérale
SHIP_START_LIVES = 3
SHIP_MAX_LIVES = 5  # une vie est offerte à chaque boss vaincu, jusqu'à ce maximum
SHIP_INVINCIBLE_TIME = 2.0  # après un choc
SHIP_BLINK_FREQUENCY = 12.0  # clignotements par seconde pendant l'invincibilité
SHIP_FIRE_COOLDOWN = 0.16  # secondes entre deux tirs, touche maintenue

# --- Tirs --------------------------------------------------------------------------------------

BULLET_SPEED = 760.0
BULLET_RADIUS = 3.0
BULLET_LENGTH = 16.0

# --- Météorites --------------------------------------------------------------------------------
# Les tuples sont indexés par la taille : 0 = petite, 1 = moyenne, 2 = grosse.

METEOR_RADII = (14.0, 26.0, 42.0)
METEOR_HIT_POINTS = (1, 3, 6)
METEOR_SCORES = (100, 50, 20)
METEOR_SIZE_SPEED_FACTOR = (1.15, 1.0, 0.8)  # les grosses tombent un peu moins vite
METEOR_HITBOX_SCALE = 0.85
METEOR_VERTEX_COUNT = 11
METEOR_JAGGEDNESS = 0.3  # 0 = cercle parfait, 1 = très déchiqueté
METEOR_MAX_SPIN = 90.0  # degrés par seconde
METEOR_MAX_DRIFT = 40.0  # vitesse latérale maximale à l'apparition
METEOR_HIT_FLASH_TIME = 0.08
METEOR_FRAGMENT_ANGLE = (20.0, 45.0)  # écart des morceaux par rapport à la trajectoire
METEOR_FRAGMENT_SPEED_BOOST = 1.2
METEOR_ZIGZAG_SPEED = 140.0
METEOR_ZIGZAG_FREQUENCY = 3.0  # radians par seconde
METEOR_BURST_SIZE = (3, 5)  # nombre de petites météorites dans une rafale
METEOR_BURST_SPEED_BOOST = 1.45
METEOR_BURST_SPACING = 40.0  # décalage vertical entre les météorites d'une rafale

# --- Difficulté --------------------------------------------------------------------------------
# L'intensité vaut 0 au début et 1 au bout de DIFFICULTY_RAMP_DURATION secondes.
# L'exposant > 1 rend la courbe douce au début et raide ensuite.

DIFFICULTY_RAMP_DURATION = 150.0
DIFFICULTY_CURVE_EXPONENT = 1.8

SPAWN_FIRST_DELAY = 1.0
SPAWN_INTERVAL_START = 1.3
SPAWN_INTERVAL_END = 0.32

METEOR_SPEED_START = 85.0
METEOR_SPEED_END = 260.0
METEOR_SPEED_SPREAD = 0.25  # ± 25 % autour de la vitesse du moment

# Apparition progressive des moyennes, des grosses, des zigzags et des rafales :
# chaque type passe de 0 à son maximum entre deux valeurs d'intensité.
MEDIUM_METEOR_RAMP = (0.03, 0.3)
LARGE_METEOR_RAMP = (0.2, 0.7)
LARGE_METEOR_MAX_WEIGHT = 0.9
ZIGZAG_RAMP = (0.5, 1.0)
ZIGZAG_MAX_CHANCE = 0.35
BURST_RAMP = (0.75, 1.0)
BURST_MAX_CHANCE = 0.25

# --- Score -------------------------------------------------------------------------------------

COMBO_STEP = 10  # destructions d'affilée pour gagner +1 au multiplicateur
COMBO_MAX_MULTIPLIER = 5

# --- Scènes ------------------------------------------------------------------------------------

GAME_OVER_INPUT_DELAY = 0.8  # évite de relancer par erreur en tenant encore Espace

# --- Cycles et boss ----------------------------------------------------------------------------
# Un cycle = une montée de difficulté puis un boss. Chaque nouveau cycle repart plus dur.

BOSS_TRIGGER_TIME = 150.0  # secondes de météorites avant l'alerte
WARNING_DURATION = 3.5
CYCLE_START_INTENSITY = 0.3  # intensité de départ ajoutée à chaque cycle
CYCLE_START_INTENSITY_MAX = 0.7
BOSS_CYCLE_SCALING = 0.35  # +35 % de vie et d'agressivité par cycle

BOSS_COLOR: Color = (0, 240, 255)
BOSS_RAGE_COLOR: Color = (255, 50, 70)
BOSS_CORE_COLOR: Color = (255, 220, 60)
ENEMY_BULLET_COLOR: Color = (255, 80, 200)
BOSS_MAX_HEALTH = 140
BOSS_PHASE_THRESHOLDS = (2 / 3, 1 / 3)  # part de vie restante où commencent les phases 2 et 3
BOSS_ENTRY_TIME = 3.0
BOSS_HOVER_Y = 135.0
BOSS_SWAY = (130.0, 0.5)  # balancement latéral : (amplitude, radians par seconde)
BOSS_RAGE_SWAY_SPEEDUP = 1.5
BOSS_PHASE_TRANSITION_TIME = 1.6  # invulnérable et silencieux pendant qu'il change de phase
BOSS_HIT_FLASH_TIME = 0.06
BOSS_SCORE = 10_000
BOSS_HIT_SCORE = 10
BOSS_DEATH_DURATION = 3.2
BOSS_DEATH_EXPLOSION_INTERVAL = 0.11
BOSS_DEATH_TIME_SCALE = 0.5
BOMB_BOSS_DAMAGE = 25

ENEMY_BULLET_RADIUS = 6.0
ENEMY_BULLET_SPEED = 230.0
ENEMY_BULLET_MAX = 260

# Phase 1 : éventails et tirs visés
FAN_INTERVAL = 1.5
FAN_COUNT = 7
FAN_SPREAD = 70.0
AIMED_INTERVAL = 2.2
AIMED_COUNT = 3
AIMED_SPREAD = 12.0
# Phase 2 : spirales et tourelles
SPIRAL_INTERVAL = 0.1
SPIRAL_ARMS = 3
SPIRAL_ROTATION = 95.0  # degrés par seconde
SPIRAL_SPEED_FACTOR = 0.75
TURRET_HEALTH = 22
TURRET_INTERVAL = 1.7
TURRET_SCORE = 1_000
# Phase 3 : rage, rayon laser balayant
LASER_COOLDOWN = 3.2
LASER_CHARGE_TIME = 1.1  # le trait d'avertissement : le joueur a le temps de s'écarter
LASER_FIRE_TIME = 1.7
LASER_SWEEP = 38.0  # le rayon balaie de -SWEEP à +SWEEP degrés autour de la verticale
LASER_WIDTH = 22.0
LASER_LENGTH = 1000.0
RAGE_FAN_INTERVAL = 1.1
