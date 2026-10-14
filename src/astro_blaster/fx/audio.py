"""Lecture des sons et de la musique. Le jeu marche aussi sans carte son (tout est alors muet)."""

import random

import pygame

from astro_blaster import config
from astro_blaster.fx.synth import Synth, make_music_loop, make_sound_effects, to_pcm

MIXER_CHANNELS = 24  # sons jouables en même temps


class Audio:
    def __init__(self) -> None:
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.music: pygame.mixer.Sound | None = None
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
        self.music = pygame.mixer.Sound(
            buffer=to_pcm(make_music_loop(synth, config.MUSIC_BPM), channels)
        )
        self.music.set_volume(config.MUSIC_VOLUME)

    def play(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound is not None and not self.muted:
            sound.play()

    def start_music(self) -> None:
        if self.music is not None and self.music.get_num_channels() == 0:
            self.music.play(loops=-1)
            if self.muted:
                self.music.set_volume(0)

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        if self.music is not None:
            self.music.set_volume(0 if self.muted else config.MUSIC_VOLUME)
