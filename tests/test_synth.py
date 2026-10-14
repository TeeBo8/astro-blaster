import random

import pytest

from astro_blaster.fx.synth import (
    Synth,
    add_at,
    make_music_loop,
    make_sound_effects,
    midi_to_hz,
    normalize,
    square,
    to_pcm,
)

RATE = 8000  # fréquence basse : les tests restent rapides


@pytest.fixture
def synth() -> Synth:
    return Synth(RATE, random.Random(0))


def test_tone_has_requested_length_and_stays_in_range(synth: Synth) -> None:
    samples = synth.tone(square, 440, 220, 0.5, 5)
    assert len(samples) == RATE // 2
    assert max(abs(s) for s in samples) <= 1.0


def test_add_at_mixes_and_extends() -> None:
    target = [1.0, 1.0]
    add_at(target, [0.5, 0.5, 0.5], 1)
    assert target == [1.0, 1.5, 0.5, 0.5]


def test_normalize_sets_peak() -> None:
    assert max(abs(s) for s in normalize([0.1, -0.4, 0.2], 0.8)) == pytest.approx(0.8)
    assert normalize([0.0, 0.0]) == [0.0, 0.0]


def test_pcm_is_16_bits_per_channel() -> None:
    assert len(to_pcm([0.0, 1.0, -1.0], channels=1)) == 6
    assert len(to_pcm([0.0, 1.0, -1.0], channels=2)) == 12


def test_midi_notes() -> None:
    assert midi_to_hz(69) == pytest.approx(440)
    assert midi_to_hz(81) == pytest.approx(880)


def test_every_sound_effect_is_audible_and_not_saturated(synth: Synth) -> None:
    for name, samples in make_sound_effects(synth).items():
        assert samples, name
        assert 0.5 < max(abs(s) for s in samples) <= 1.0, name


def test_music_loop_lasts_exactly_eight_bars(synth: Synth) -> None:
    bpm = 120
    samples = make_music_loop(synth, bpm)
    assert len(samples) == int(8 * 4 * 60 / bpm * RATE)
