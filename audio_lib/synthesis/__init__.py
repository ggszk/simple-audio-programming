"""
synthesis モジュール - 音響合成機能
"""

from .oscillators import SineWave, SawtoothWave, SquareWave, TriangleWave, NoiseGenerator
from .envelopes import ADSREnvelope, LinearEnvelope, CosineEnvelope, apply_envelope
from .note_utils import note_to_frequency, frequency_to_note, note_name_to_number, number_to_note_name, create_scale

__all__ = [
    'SineWave', 'SawtoothWave', 'SquareWave', 'TriangleWave', 'NoiseGenerator',
    'ADSREnvelope', 'LinearEnvelope', 'CosineEnvelope', 'apply_envelope',
    'note_to_frequency', 'frequency_to_note', 'note_name_to_number', 'number_to_note_name', 'create_scale'
]
