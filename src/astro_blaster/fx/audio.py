"""Lecture des sons et de la musique. Le jeu marche aussi sans carte son (tout est alors muet)."""

import random

import pygame

from astro_blaster import config
from astro_blaster.fx.synth import (
    BOSS_THEME,
    MAIN_THEME,
    Synth,
    make_music_loop,
    make_sound_effects,
    to_pcm,
)

MIXER_CHANNELS = 24  # sons jouables en même temps


class Audio:
    def __init__(self) -> None:
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.tracks: dict[str, pygame.mixer.Sound] = {}
        self.current_track: str | None = None
        self.muted = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(config.SAMPLE_RATE, -16, 1)
            init = pygame.mixer.get_init()
        except pygame.error:
            init = None
        if init is None:
            return  # pas de carte son : on joue en silence

        # On synthétise à la fréquence réellement obtenue, sinon les sons seraient faux.
        frequency, _, channels = init
        pygame.mixer.set_num_channels(MIXER_CHANNELS)
        synth = Synth(frequency, random.Random(2026))
        for name, samples in make_sound_effects(synth).items():
            sound = pygame.mixer.Sound(buffer=to_pcm(samples, channels))
            sound.set_volume(config.SFX_VOLUME)
            self.sounds[name] = sound
        themes = {
            "main": (config.MUSIC_BPM, MAIN_THEME),
            "boss": (config.BOSS_MUSIC_BPM, BOSS_THEME),
        }
        for name, (bpm, theme) in themes.items():
            samples = make_music_loop(synth, bpm, theme)
            self.tracks[name] = pygame.mixer.Sound(buffer=to_pcm(samples, channels))

    def play(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound is not None and not self.muted:
            sound.play()

    def play_music(self, name: str) -> None:
        """Lance une musique en boucle (ne fait rien si elle joue déjà)."""
        if name == self.current_track or name not in self.tracks:
            return
        if self.current_track is not None:
            self.tracks[self.current_track].fadeout(400)
        self.current_track = name
        track = self.tracks[name]
        track.set_volume(0 if self.muted else config.MUSIC_VOLUME)
        track.play(loops=-1, fade_ms=400)

    def stop_music(self) -> None:
        if self.current_track is not None:
            self.tracks[self.current_track].fadeout(600)
            self.current_track = None

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        for track in self.tracks.values():
            track.set_volume(0 if self.muted else config.MUSIC_VOLUME)
