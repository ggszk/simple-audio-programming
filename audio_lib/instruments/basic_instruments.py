"""
楽器クラス

様々な楽器の音色を合成するクラス群
"""

import numpy as np
from ..synthesis.oscillators import SineWave, SawtoothWave, SquareWave, NoiseGenerator
from ..synthesis.envelopes import ADSREnvelope, LinearEnvelope, apply_envelope
from ..synthesis.note_utils import note_to_frequency
from ..effects.filters import LowPassFilter, HighPassFilter
from ..core.audio_config import AudioConfig

class BaseInstrument:
    """楽器の基底クラス"""
    
    def __init__(self, config=None):
        self.config = config or AudioConfig()
    
    def play_note(self, note_number, velocity=100, duration=1.0):
        """
        音符を演奏（派生クラスで実装）
        
        Args:
            note_number (int): MIDIノート番号
            velocity (int): ベロシティ (0-127)
            duration (float): 音符の長さ (秒)
            
        Returns:
            np.ndarray: 生成された音声データ
        """
        raise NotImplementedError("派生クラスで実装してください")

class SimpleSynthesizer(BaseInstrument):
    """シンプルなシンセサイザー"""
    
    def __init__(self, oscillator_type='sine', attack=0.1, decay=0.1, sustain=0.7, release=0.2, config=None):
        """
        シンプルシンセサイザーを初期化
        
        Args:
            oscillator_type (str): オシレーター種類 ('sine', 'sawtooth', 'square')
            attack, decay, sustain, release: ADSRパラメータ
            config (AudioConfig): オーディオ設定
        """
        super().__init__(config)
        
        # オシレーターの選択
        if oscillator_type == 'sine':
            self.oscillator = SineWave(config)
        elif oscillator_type == 'sawtooth':
            self.oscillator = SawtoothWave(config)
        elif oscillator_type == 'square':
            self.oscillator = SquareWave(config)
        else:
            raise ValueError(f"未知のオシレータータイプ: {oscillator_type}")
        
        # エンベロープの設定
        self.envelope = ADSREnvelope(attack, decay, sustain, release, config)
    
    def play_note(self, note_number, velocity=100, duration=1.0):
        """
        音符を演奏
        
        Args:
            note_number (int): MIDIノート番号
            velocity (int): ベロシティ (0-127)
            duration (float): 音符の長さ (秒)
            
        Returns:
            np.ndarray: 生成された音声データ
        """
        # 周波数を計算
        frequency = note_to_frequency(note_number)
        
        # 基本波形を生成
        signal = self.oscillator.generate(frequency, duration)
        
        # ベロシティを音量に変換
        amplitude = velocity / 127.0
        signal *= amplitude
        
        # エンベロープを適用
        envelope_data = self.envelope.generate(duration)
        signal = apply_envelope(signal, envelope_data)
        
        return signal

class BasicPiano(BaseInstrument):
    """ピアノの音色をシミュレート"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.oscillator = SineWave(config)
        # ピアノらしいエンベロープ（短いアタック、長いリリース）
        self.envelope = ADSREnvelope(attack=0.01, decay=0.3, sustain=0.3, release=1.0, config=config)
    
    def play_note(self, note_number, velocity=100, duration=1.0):
        """ピアノの音を生成"""
        frequency = note_to_frequency(note_number)
        
        # 基音
        fundamental = self.oscillator.generate(frequency, duration)
        
        # 倍音を追加（ピアノらしい音色）
        harmonics = [
            (2.0, 0.5),    # 2倍音
            (3.0, 0.25),   # 3倍音
            (4.0, 0.125),  # 4倍音
            (5.0, 0.063),  # 5倍音
        ]
        
        signal = fundamental.copy()
        for harmonic_ratio, amplitude in harmonics:
            harmonic = self.oscillator.generate(frequency * harmonic_ratio, duration)
            signal += harmonic * amplitude
        
        # ベロシティを適用
        amplitude = velocity / 127.0
        signal *= amplitude
        
        # エンベロープを適用
        envelope_data = self.envelope.generate(duration)
        signal = apply_envelope(signal, envelope_data)
        
        # 正規化
        if np.max(np.abs(signal)) > 0:
            signal = signal / np.max(np.abs(signal)) * 0.8
        
        return signal

class BasicOrgan(BaseInstrument):
    """オルガンの音色をシミュレート"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.oscillator = SineWave(config)
        # オルガンらしいエンベロープ（速いアタック、サステイン重視）
        self.envelope = ADSREnvelope(attack=0.01, decay=0.0, sustain=1.0, release=0.1, config=config)
    
    def play_note(self, note_number, velocity=100, duration=1.0):
        """オルガンの音を生成"""
        frequency = note_to_frequency(note_number)
        
        # 複数の倍音を組み合わせ（オルガンの音色）
        harmonics = [
            (1.0, 1.0),    # 基音
            (2.0, 0.7),    # 2倍音
            (3.0, 0.5),    # 3倍音
            (4.0, 0.3),    # 4倍音
            (6.0, 0.2),    # 6倍音
        ]
        
        signal = np.zeros(self.config.duration_to_samples(duration))
        for harmonic_ratio, amplitude in harmonics:
            harmonic = self.oscillator.generate(frequency * harmonic_ratio, duration)
            signal += harmonic * amplitude
        
        # ベロシティを適用
        amplitude = velocity / 127.0
        signal *= amplitude
        
        # エンベロープを適用
        envelope_data = self.envelope.generate(duration)
        signal = apply_envelope(signal, envelope_data)
        
        # 正規化
        if np.max(np.abs(signal)) > 0:
            signal = signal / np.max(np.abs(signal)) * 0.8
        
        return signal

class BasicGuitar(BaseInstrument):
    """ギターの音色をシミュレート"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.oscillator = SawtoothWave(config)  # ギターはノコギリ波ベース
        # ギターらしいエンベロープ
        self.envelope = ADSREnvelope(attack=0.01, decay=0.2, sustain=0.6, release=0.5, config=config)
        # フィルターを追加
        self.filter = LowPassFilter(cutoff_freq=3000, config=config)
    
    def play_note(self, note_number, velocity=100, duration=1.0):
        """ギターの音を生成"""
        frequency = note_to_frequency(note_number)
        
        # ノコギリ波ベースの音を生成
        signal = self.oscillator.generate(frequency, duration)
        
        # フィルターを適用
        signal = self.filter.process(signal)
        
        # ベロシティを適用
        amplitude = velocity / 127.0
        signal *= amplitude
        
        # エンベロープを適用
        envelope_data = self.envelope.generate(duration)
        signal = apply_envelope(signal, envelope_data)
        
        # 正規化
        if np.max(np.abs(signal)) > 0:
            signal = signal / np.max(np.abs(signal)) * 0.8
        
        return signal

class BasicDrum(BaseInstrument):
    """ドラムの音色をシミュレート"""
    
    def __init__(self, drum_type='kick', config=None):
        super().__init__(config)
        self.drum_type = drum_type
        self.noise_gen = NoiseGenerator(config)
        self.oscillator = SineWave(config)
        
        # ドラムの種類に応じたパラメータ
        if drum_type == 'kick':
            self.base_freq = 60  # キックドラムの基本周波数
            self.envelope = ADSREnvelope(attack=0.001, decay=0.1, sustain=0.0, release=0.3, config=config)
        elif drum_type == 'snare':
            self.base_freq = 200
            self.envelope = ADSREnvelope(attack=0.001, decay=0.05, sustain=0.0, release=0.1, config=config)
        elif drum_type == 'hihat':
            self.base_freq = 8000
            self.envelope = ADSREnvelope(attack=0.001, decay=0.02, sustain=0.0, release=0.05, config=config)
    
    def play_note(self, note_number=60, velocity=100, duration=0.5):
        """ドラム音を生成
        
        MIDIノート番号に基づいてドラムの種類を決定:
        - 36: キックドラム
        - 38: スネアドラム  
        - 42: ハイハット
        - その他: ノイズ
        """
        # MIDIノート番号に基づいてドラムの種類を決定
        if note_number == 36:  # キックドラム
            drum_type = 'kick'
            base_freq = 50  # より低い周波数でよりパンチのある音
            envelope = ADSREnvelope(attack=0.001, decay=0.15, sustain=0.0, release=0.4, config=self.config)
        elif note_number == 38:  # スネアドラム
            drum_type = 'snare'
            base_freq = 200
            envelope = ADSREnvelope(attack=0.001, decay=0.05, sustain=0.0, release=0.1, config=self.config)
        elif note_number == 42:  # ハイハット
            drum_type = 'hihat'
            base_freq = 8000
            envelope = ADSREnvelope(attack=0.001, decay=0.02, sustain=0.0, release=0.05, config=self.config)
        else:
            drum_type = 'generic'
            base_freq = 200
            envelope = ADSREnvelope(attack=0.001, decay=0.1, sustain=0.0, release=0.2, config=self.config)
        
        if drum_type == 'kick':
            # キックドラム: 低周波のサイン波 + ピッチベンド + 音量強調
            signal = self.oscillator.generate(base_freq, duration)
            # ピッチベンドエフェクト（より緩やかに）
            pitch_bend = np.exp(-np.linspace(0, 3, len(signal)))
            signal *= pitch_bend
            
            # キック音を強調するため、低周波成分を追加
            sub_bass = self.oscillator.generate(base_freq * 0.5, duration)
            sub_bass *= np.exp(-np.linspace(0, 4, len(sub_bass)))
            signal += 0.5 * sub_bass
            
            # キック音をより聞こえやすくするために音量を増強
            signal *= 2.0
            
        elif drum_type == 'snare':
            # スネアドラム: トーン + ノイズ
            tone = self.oscillator.generate(base_freq, duration)
            noise = self.noise_gen.generate_white_noise(duration)
            signal = 0.3 * tone + 0.7 * noise
            
        elif drum_type == 'hihat':
            # ハイハット: 高周波ノイズ + フィルター
            noise = self.noise_gen.generate_white_noise(duration)
            # 簡易ハイパスフィルター効果
            signal = noise
            
        else:
            # 汎用ドラム音
            signal = self.noise_gen.generate_white_noise(duration)
        
        # ベロシティを適用
        amplitude = velocity / 127.0
        signal *= amplitude
        
        # エンベロープを適用
        envelope_data = envelope.generate(duration)
        signal = apply_envelope(signal, envelope_data)
        
        # 正規化
        if np.max(np.abs(signal)) > 0:
            signal = signal / np.max(np.abs(signal)) * 0.8
        
        return signal

# 後方互換性のためのエイリアス
Piano = BasicPiano
Organ = BasicOrgan
Guitar = BasicGuitar
Drum = BasicDrum
