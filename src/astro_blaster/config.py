"""Tous les réglages du jeu, au même endroit.

Changer une valeur ici suffit : aucun autre fichier ne contient de « nombre magique ».
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

BACKGROUND_COLOR: Color = (6, 6, 18)
SHIP_COLOR: Color = (0, 240, 255)
FLAME_COLOR: Color = (255, 140, 40)
BULLET_COLOR: Color = (255, 250, 180)
METEOR_COLOR: Color = (255, 60, 200)
METEOR_HIT_COLOR: Color = (255, 255, 255)
HUD_COLOR: Color = (220, 230, 255)
ACCENT_COLOR: Color = (255, 220, 60)
OVERLAY_ALPHA = 160  # opacité du voile noir de la pause et du game over (0 à 255)

# --- Textes ------------------------------------------------------------------------------------

FONT_SIZE_HUD = 26
FONT_SIZE_TEXT = 30
FONT_SIZE_TITLE = 72
HUD_MARGIN = 14

# --- Vaisseau ----------------------------------------------------------------------------------

SHIP_SPEED = 340.0
SHIP_RESPONSIVENESS = 14.0  # plus c'est haut, moins il y a d'inertie
SHIP_HITBOX_RADIUS = 9.0  # plus petit que le dessin : les frôlements ne tuent pas
SHIP_BOTTOM_MARGIN = 60.0
SHIP_TOP_LIMIT = SCREEN_HEIGHT * 0.45  # le vaisseau reste dans le bas de l'écran
SHIP_SIDE_MARGIN = 18.0
SHIP_MAX_TILT = 14.0  # inclinaison du dessin à pleine vitesse latérale
SHIP_START_LIVES = 3
SHIP_INVINCIBLE_TIME = 2.0  # après un choc
SHIP_BLINK_FREQUENCY = 12.0  # clignotements par seconde pendant l'invincibilité
SHIP_FIRE_COOLDOWN = 0.16  # secondes entre deux tirs, touche maintenue

# --- Tirs --------------------------------------------------------------------------------------

BULLET_SPEED = 760.0
BULLET_RADIUS = 3.0
BULLET_LENGTH = 12.0

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
DIFFICULTY_OVERDRIVE_SLOPE = 0.4  # au-delà, l'intensité continue de monter, plus lentement

SPAWN_FIRST_DELAY = 1.0
SPAWN_INTERVAL_START = 1.3
SPAWN_INTERVAL_END = 0.32
SPAWN_INTERVAL_MIN = 0.18

METEOR_SPEED_START = 85.0
METEOR_SPEED_END = 260.0
METEOR_SPEED_MAX = 380.0
METEOR_SPEED_SPREAD = 0.25  # ± 25 % autour de la vitesse du moment

# Apparition progressive des moyennes, des grosses, des zigzags et des rafales :
# chaque type passe de 0 à son maximum entre deux valeurs d'intensité.
MEDIUM_METEOR_RAMP = (0.03, 0.3)
LARGE_METEOR_RAMP = (0.2, 0.7)
LARGE_METEOR_MAX_WEIGHT = 0.9
ZIGZAG_RAMP = (0.5, 1.0)
ZIGZAG_MAX_CHANCE = 0.35
BURST_RAMP = (0.75, 1.2)
BURST_MAX_CHANCE = 0.25

# --- Score -------------------------------------------------------------------------------------

COMBO_STEP = 10  # destructions d'affilée pour gagner +1 au multiplicateur
COMBO_MAX_MULTIPLIER = 5

# --- Scènes ------------------------------------------------------------------------------------

GAME_OVER_INPUT_DELAY = 0.8  # évite de relancer par erreur en tenant encore Espace
