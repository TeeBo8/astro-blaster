"""Synthétiseur : fabrique tous les sons du jeu à partir de formules, sans fichier audio.

Un son numérique n'est qu'une liste de nombres entre -1 et 1 (les « échantillons »),
SAMPLE_RATE nombres par seconde. On les calcule avec des ondes simples (sinus, carré,
dent de scie), du bruit, et une enveloppe qui fait décroître le volume.
"""

import array
import math
import random
from collections.abc import Callable

Samples = list[float]
Wave = Callable[[float], float]  # phase en nombre de cycles → amplitude entre -1 et 1


def sine(phase: float) -> float:
    return math.sin(2 * math.pi * phase)


def square(phase: float) -> float:
    return 1.0 if phase % 1 < 0.5 else -1.0


def saw(phase: float) -> float:
    return 2 * (phase % 1) - 1


def triangle(phase: float) -> float:
    return 4 * abs(phase % 1 - 0.5) - 1


class Synth:
    def __init__(self, sample_rate: int, rng: random.Random) -> None:
        self.rate = sample_rate
        self.rng = rng

    def length(self, duration: float) -> int:
        return int(duration * self.rate)

    def tone(
        self,
        wave: Wave,
        start_hz: float,
        end_hz: float,
        duration: float,
        decay: float,
        volume: float = 1.0,
    ) -> Samples:
        """Note dont la hauteur glisse de start_hz à end_hz, et dont le volume décroît.

        decay : vitesse d'extinction (0 = son tenu, 30 = claquement très bref).
        """
        count = self.length(duration)
        attack = max(1, self.length(0.004))  # 4 ms de montée, évite un « clic » au départ
        ratio = end_hz / start_hz
        phase = 0.0
        out: Samples = []
        for index in range(count):
            progress = index / count
            phase += start_hz * ratio**progress / self.rate  # glissement exponentiel
            envelope = min(1.0, index / attack) * math.exp(-decay * index / self.rate)
            out.append(wave(phase) * envelope * volume)
        return out

    def noise(
        self, duration: float, decay: float, smoothing: float, volume: float = 1.0
    ) -> Samples:
        """Bruit blanc filtré : smoothing proche de 1 = aigu (cymbale), proche de 0 = sourd."""
        count = self.length(duration)
        level = 0.0
        out: Samples = []
        for index in range(count):
            level += (self.rng.uniform(-1, 1) - level) * smoothing
            out.append(level * math.exp(-decay * index / self.rate) * volume)
        return out

    def low_pass(self, samples: Samples, smoothing: float) -> Samples:
        """Adoucit un son en atténuant ses aigus."""
        level = 0.0
        out: Samples = []
        for sample in samples:
            level += (sample - level) * smoothing
            out.append(level)
        return out

    def sequence(self, notes: list[Samples], step: float) -> Samples:
        """Joue des notes l'une après l'autre, espacées de `step` secondes."""
        out: Samples = []
        stride = self.length(step)
        for index, note in enumerate(notes):
            add_at(out, note, index * stride)
        return out


def add_at(target: Samples, sound: Samples, start: int) -> None:
    """Mixe `sound` dans `target` à partir de l'échantillon `start` (agrandit si besoin)."""
    end = start + len(sound)
    if len(target) < end:
        target.extend([0.0] * (end - len(target)))
    target[start:end] = [a + b for a, b in zip(target[start:end], sound, strict=True)]


def mix(*sounds: Samples) -> Samples:
    out: Samples = []
    for sound in sounds:
        add_at(out, sound, 0)
    return out


def normalize(samples: Samples, peak: float = 1.0) -> Samples:
    """Remet le son à un volume maximal donné (évite la saturation après un mixage)."""
    loudest = max((abs(s) for s in samples), default=0.0)
    if loudest == 0:
        return samples
    return [s * peak / loudest for s in samples]


def to_pcm(samples: Samples, channels: int) -> bytes:
    """Convertit en entiers 16 bits, le format attendu par la carte son."""
    pcm = array.array("h")
    for sample in samples:
        value = round(max(-1.0, min(1.0, sample)) * 32767)
        pcm.extend([value] * channels)
    return pcm.tobytes()


def midi_to_hz(note: int) -> float:
    """Numéro de note MIDI → fréquence (69 = La 440 Hz, +12 = une octave au-dessus)."""
    return 440.0 * 2 ** ((note - 69) / 12)


# --- Les sons du jeu ---------------------------------------------------------------------------


def make_sound_effects(synth: Synth) -> dict[str, Samples]:
    s = synth
    effects = {
        "laser": mix(
            s.tone(square, 1500, 380, 0.11, 25, 0.3),
            s.tone(sine, 3000, 900, 0.05, 40, 0.2),
        ),
        "hit": mix(s.noise(0.05, 60, 0.6, 0.5), s.tone(square, 420, 200, 0.04, 50, 0.3)),
        "explosion": mix(s.noise(0.4, 9, 0.25), s.tone(sine, 170, 40, 0.3, 8, 0.8)),
        "big_explosion": mix(s.noise(1.0, 4, 0.12), s.tone(sine, 120, 30, 0.8, 4)),
        "ship_hit": mix(s.noise(0.7, 5, 0.2), s.tone(saw, 600, 50, 0.6, 5, 0.6)),
        "powerup": s.sequence(
            [s.tone(square, midi_to_hz(n), midi_to_hz(n), 0.09, 18, 0.5) for n in (72, 76, 79, 84)],
            0.055,
        ),
        "shield_break": mix(s.tone(triangle, 2200, 300, 0.3, 10), s.noise(0.1, 30, 0.9, 0.4)),
        "bomb": mix(
            s.noise(1.6, 2.5, 0.1),
            s.tone(sine, 90, 25, 1.4, 2.5),
            s.tone(saw, 400, 40, 0.5, 6, 0.3),
        ),
        "combo": s.sequence([s.tone(square, f, f, 0.06, 25, 0.4) for f in (880, 1320)], 0.05),
        "enemy_shot": s.tone(triangle, 900, 500, 0.08, 30, 0.35),
        "armor": mix(s.tone(square, 2400, 1800, 0.05, 50, 0.35), s.noise(0.03, 80, 0.9, 0.3)),
        "boss_hit": mix(s.tone(square, 300, 180, 0.06, 40, 0.4), s.noise(0.05, 50, 0.4, 0.4)),
        "warning": s.sequence(
            [s.tone(square, f, f, 0.32, 1.5, 0.45) for f in (880, 660) * 3],
            0.35,
        ),
        "roar": mix(
            s.low_pass(s.tone(saw, 60, 140, 1.2, 1.5), 0.15),
            s.noise(1.2, 2, 0.08, 0.7),
            s.tone(square, 70, 50, 1.0, 2, 0.4),
        ),
        "laser_charge": s.tone(sine, 200, 1600, 1.1, 0.5, 0.6),
        "laser_beam": mix(
            s.low_pass(s.tone(saw, 110, 90, 1.7, 0.8), 0.3),
            s.noise(1.7, 1, 0.3, 0.5),
        ),
        "game_over": s.sequence(
            [s.tone(triangle, midi_to_hz(n), midi_to_hz(n), 0.35, 4) for n in (64, 60, 57, 52)],
            0.22,
        ),
    }
    return {name: normalize(sound, 0.9) for name, sound in effects.items()}


# Arpège joué au-dessus de chaque accord : intervalles depuis la note de basse.
MINOR_ARPEGGIO = (12, 15, 19, 24, 19, 15, 12, 19)
MAJOR_ARPEGGIO = (12, 16, 19, 24, 19, 16, 12, 19)
# Grilles d'accords : (note MIDI de la basse, arpège). 4 accords de 2 mesures.
MAIN_THEME = (
    (45, MINOR_ARPEGGIO),
    (41, MAJOR_ARPEGGIO),
    (48, MAJOR_ARPEGGIO),
    (43, MAJOR_ARPEGGIO),
)
# Thème du boss : surtout en mineur, avec un demi-ton qui grince (Mi, Fa) : plus menaçant.
BOSS_THEME = (
    (40, MINOR_ARPEGGIO),
    (41, MAJOR_ARPEGGIO),
    (40, MINOR_ARPEGGIO),
    (38, MINOR_ARPEGGIO),
)
BARS_PER_CHORD = 2

Theme = tuple[tuple[int, tuple[int, ...]], ...]


def make_music_loop(synth: Synth, bpm: float, theme: Theme = MAIN_THEME) -> Samples:
    """Boucle synthwave de 8 mesures : basse, arpège, grosse caisse, caisse claire, charleston.

    Chaque son différent n'est calculé qu'une fois (dictionnaire `cache`), puis recopié
    à chaque endroit où il est joué : c'est ce qui rend la génération rapide.
    """
    s = synth
    beat = 60 / bpm
    eighth, sixteenth = beat / 2, beat / 4
    cache: dict[tuple[str, int], Samples] = {}

    def bass(note: int) -> Samples:
        key = ("bass", note)
        if key not in cache:
            hz = midi_to_hz(note)
            cache[key] = s.low_pass(s.tone(saw, hz, hz, eighth, 6, 0.55), 0.25)
        return cache[key]

    def lead(note: int) -> Samples:
        key = ("lead", note)
        if key not in cache:
            hz = midi_to_hz(note)
            cache[key] = s.tone(square, hz, hz, sixteenth * 1.5, 14, 0.12)
        return cache[key]

    kick = s.tone(sine, 150, 45, 0.28, 9, 1.0)
    snare = s.noise(0.18, 18, 0.5, 0.45)
    hat = s.noise(0.04, 70, 0.95, 0.18)

    out: Samples = []
    bar_length = 4 * beat
    for chord_index, (root, arpeggio) in enumerate(theme):
        for bar in range(BARS_PER_CHORD):
            bar_start = (chord_index * BARS_PER_CHORD + bar) * bar_length
            for step in range(8):  # croches : basse et charleston
                at = s.length(bar_start + step * eighth)
                add_at(out, bass(root + (12 if step % 2 else 0)), at)
                if step % 2:
                    add_at(out, hat, at)
            for step in range(16):  # doubles croches : arpège
                note = root + arpeggio[step % len(arpeggio)]
                add_at(out, lead(note), s.length(bar_start + step * sixteenth))
            for step in range(4):  # temps : grosse caisse, caisse claire sur 2 et 4
                at = s.length(bar_start + step * beat)
                add_at(out, kick, at)
                if step % 2:
                    add_at(out, snare, at)

    # Longueur exacte de 8 mesures, pour que la boucle retombe pile sur le temps.
    total = s.length(len(theme) * BARS_PER_CHORD * bar_length)
    out = out[:total] + [0.0] * (total - len(out))
    return normalize(out, 0.9)
