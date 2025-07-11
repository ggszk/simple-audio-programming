"""
音のプログラミング - リファクタリング版

可読性と教育性を重視した音楽合成ライブラリ
"""

from .core.audio_config import AudioConfig
from .core.wave_io import WaveFileIO
from .synthesis.oscillators import SineWave, SawtoothWave, SquareWave, TriangleWave, NoiseGenerator
from .synthesis.envelopes import ADSREnvelope, LinearEnvelope
from .effects.filters import LowPassFilter, HighPassFilter
from .effects.audio_effects import Reverb, Distortion
from .synthesis.note_utils import note_to_frequency, frequency_to_note, note_name_to_number
from .sequencer import Sequencer, Note, Track
from .instruments.basic_instruments import (
    BaseInstrument, SimpleSynthesizer,
    BasicPiano, BasicOrgan, BasicGuitar, BasicDrum,
    # 後方互換性のためのエイリアス
    Piano, Organ, Guitar, Drum
)

__version__ = "1.0.0"
__author__ = "音のプログラミング教育チーム"

# デフォルトのオーディオ設定
default_config = AudioConfig()

# よく使う関数のエイリアス
save_audio = WaveFileIO.save_mono
load_audio = WaveFileIO.load_mono
