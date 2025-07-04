"""
audio_lib パッケージの包括的テスト

このテストファイルは、ノートブック教材で使用される主要機能の動作を検証します。
音響プログラミング教育において重要な基本機能をテストします。
"""

import numpy as np
import pytest
import tempfile
import os
from audio_lib import (
    AudioConfig, SineWave, SquareWave, SawtoothWave, 
    ADSREnvelope, LinearEnvelope,
    save_audio, note_to_frequency, frequency_to_note, note_name_to_number
)
from audio_lib.synthesis.envelopes import apply_envelope
from audio_lib.effects.audio_effects import (
    apply_compression, Reverb, Delay, Chorus, Distortion
)
from audio_lib.effects.filters import LowPassFilter, HighPassFilter


class TestAudioConfig:
    """AudioConfig クラスのテスト"""
    
    def test_default_config(self):
        """デフォルト設定のテスト"""
        config = AudioConfig()
        assert config.sample_rate == 44100
        assert config.bit_depth == 16
        assert config.max_amplitude == 0.95
    
    def test_custom_config(self):
        """カスタム設定のテスト"""
        config = AudioConfig(sample_rate=48000, bit_depth=24)
        assert config.sample_rate == 48000
        assert config.bit_depth == 24
    
    def test_duration_to_samples(self):
        """時間からサンプル数への変換テスト"""
        config = AudioConfig()
        samples = config.duration_to_samples(1.0)  # 1秒
        assert samples == 44100


class TestBasicOscillators:
    """基本オシレーターのテスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される準備"""
        self.config = AudioConfig()
        self.frequency = 440.0
        self.duration = 1.0
    
    def test_sine_wave_basic(self):
        """サイン波の基本動作テスト"""
        sine = SineWave(self.config)
        signal = sine.generate(self.frequency, self.duration)
        
        # 基本的な検証
        expected_samples = int(self.config.sample_rate * self.duration)
        assert len(signal) == expected_samples
        assert -1.0 <= np.min(signal) <= 1.0
        assert -1.0 <= np.max(signal) <= 1.0
        
        # サイン波の特性確認
        assert np.abs(np.max(signal) - 1.0) < 0.1
        assert np.abs(np.min(signal) - (-1.0)) < 0.1
    
    def test_square_wave_basic(self):
        """矩形波の基本動作テスト"""
        square = SquareWave(self.config)
        signal = square.generate(self.frequency, self.duration)
        
        assert len(signal) == int(self.config.sample_rate * self.duration)
        assert -1.0 <= np.min(signal) <= 1.0
        assert -1.0 <= np.max(signal) <= 1.0
    
    def test_sawtooth_wave_basic(self):
        """ノコギリ波の基本動作テスト"""
        sawtooth = SawtoothWave(self.config)
        signal = sawtooth.generate(self.frequency, self.duration)
        
        assert len(signal) == int(self.config.sample_rate * self.duration)
        assert -1.0 <= np.min(signal) <= 1.0
        assert -1.0 <= np.max(signal) <= 1.0


class TestEnvelopes:
    """エンベロープのテスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される準備"""
        self.config = AudioConfig()
        self.duration = 2.0
    
    def test_linear_envelope(self):
        """リニアエンベロープのテスト"""
        envelope = LinearEnvelope(fade_in=0.1, fade_out=0.1, config=self.config)
        env_data = envelope.generate(self.duration)
        
        # 長さの確認
        expected_samples = int(self.config.sample_rate * self.duration)
        assert len(env_data) == expected_samples
        
        # エンベロープの特性確認
        assert env_data[0] == 0.0  # 開始は無音
        assert env_data[-1] == 0.0  # 終了は無音
        assert np.max(env_data) <= 1.0  # 最大振幅は1以下
    
    def test_adsr_envelope(self):
        """ADSRエンベロープのテスト"""
        adsr = ADSREnvelope(
            attack=0.1, decay=0.2, sustain=0.7, release=0.3, 
            config=self.config
        )
        env_data = adsr.generate(self.duration)
        
        # 基本的な検証
        expected_samples = int(self.config.sample_rate * self.duration)
        assert len(env_data) == expected_samples
        assert 0.0 <= np.min(env_data)
        assert np.max(env_data) <= 1.0
        
        # ADSR特性の確認
        assert env_data[0] == 0.0  # アタック開始は0
    
    def test_apply_envelope(self):
        """エンベロープ適用のテスト"""
        sine = SineWave(self.config)
        signal = sine.generate(440.0, self.duration)
        
        adsr = ADSREnvelope(
            attack=0.1, decay=0.2, sustain=0.5, release=0.3,
            config=self.config
        )
        env_data = adsr.generate(self.duration)
        
        # エンベロープを適用
        processed_signal = apply_envelope(signal, env_data)
        
        # 結果の検証
        assert len(processed_signal) == len(signal)
        assert np.max(np.abs(processed_signal)) <= np.max(np.abs(signal))


class TestNoteUtils:
    """音名・周波数変換のテスト"""
    
    def test_note_to_frequency(self):
        """MIDI番号から周波数への変換テスト"""
        # A4 = 440Hz (MIDI番号69)
        freq = note_to_frequency(69)
        assert abs(freq - 440.0) < 0.1
        
        # C4 = 261.63Hz (MIDI番号60)
        freq = note_to_frequency(60)
        assert abs(freq - 261.63) < 0.1
    
    def test_frequency_to_note(self):
        """周波数からMIDI番号への変換テスト"""
        note = frequency_to_note(440.0)
        assert note == 69  # A4
        
        note = frequency_to_note(261.63)
        assert note == 60  # C4
    
    def test_note_name_to_number(self):
        """音名からMIDI番号への変換テスト"""
        assert note_name_to_number('A4') == 69
        assert note_name_to_number('C4') == 60
        assert note_name_to_number('C5') == 72


class TestAudioEffects:
    """オーディオエフェクトのテスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される準備"""
        self.config = AudioConfig()
        self.sine = SineWave(self.config)
        self.test_signal = self.sine.generate(440.0, 1.0)
    
    def test_compression(self):
        """コンプレッション効果のテスト"""
        compressed = apply_compression(
            self.test_signal, 
            threshold=0.5, 
            ratio=4.0, 
            attack=0.01, 
            release=0.1
        )
        
        # 基本的な検証
        assert len(compressed) == len(self.test_signal)
        
        # コンプレッション効果の確認（ピーク振幅の減少）
        original_peak = np.max(np.abs(self.test_signal))
        compressed_peak = np.max(np.abs(compressed))
        assert compressed_peak <= original_peak
    
    def test_low_pass_filter(self):
        """ローパスフィルターのテスト"""
        lpf = LowPassFilter(cutoff_freq=1000, config=self.config)
        filtered = lpf.process(self.test_signal)
        
        assert len(filtered) == len(self.test_signal)
    
    def test_high_pass_filter(self):
        """ハイパスフィルターのテスト"""
        hpf = HighPassFilter(cutoff_freq=1000, config=self.config)
        filtered = hpf.process(self.test_signal)
        
        assert len(filtered) == len(self.test_signal)
    
    def test_reverb_effect(self):
        """リバーブ効果のテスト"""
        reverb = Reverb(room_size=0.7, damping=0.5)
        processed = reverb.apply(self.test_signal)
        
        assert len(processed) == len(self.test_signal)
    
    def test_delay_effect(self):
        """ディレイ効果のテスト"""
        delay = Delay(delay_time=0.3, feedback=0.4, wet_level=0.3)
        processed = delay.apply(self.test_signal, self.config.sample_rate)
        
        assert len(processed) == len(self.test_signal)
    
    def test_chorus_effect(self):
        """コーラス効果のテスト"""
        chorus = Chorus(rate=1.5, depth=0.005, wet_level=0.5)
        processed = chorus.apply(self.test_signal, self.config.sample_rate)
        
        assert len(processed) == len(self.test_signal)
    
    def test_distortion_effect(self):
        """ディストーション効果のテスト"""
        distortion = Distortion(gain=10.0, output_level=0.7)
        processed = distortion.apply(self.test_signal)
        
        assert len(processed) == len(self.test_signal)


class TestAudioFileIO:
    """音声ファイル入出力のテスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される準備"""
        self.config = AudioConfig()
        self.sine = SineWave(self.config)
        self.test_signal = self.sine.generate(440.0, 1.0)
    
    def test_save_audio(self):
        """音声ファイル保存のテスト"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            temp_filename = tmp_file.name
        
        try:
            # ファイル保存
            save_audio(temp_filename, self.config.sample_rate, self.test_signal)
            
            # ファイルが作成されたことを確認
            assert os.path.exists(temp_filename)
            assert os.path.getsize(temp_filename) > 0
            
        finally:
            # テスト後にファイルを削除
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


class TestEducationalScenarios:
    """教育シナリオのテスト（ノートブック内容の再現）"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される準備"""
        self.config = AudioConfig()
    
    def test_lesson01_basic_sine_wave(self):
        """Lesson 1: 基本サイン波生成の再現テスト"""
        sine_osc = SineWave(self.config)
        
        # 440Hz、1秒のサイン波
        frequency = 440.0
        duration = 1.0
        signal = sine_osc.generate(frequency, duration)
        
        # 期待される結果
        expected_samples = 44100
        assert len(signal) == expected_samples
        assert np.abs(np.max(signal) - 1.0) < 0.1
        assert np.abs(np.min(signal) - (-1.0)) < 0.1
    
    def test_lesson02_envelope_application(self):
        """Lesson 2: エンベロープ適用の再現テスト"""
        sine_osc = SineWave(self.config)
        
        # 音声信号生成
        frequency = 440.0
        duration = 2.0
        signal = sine_osc.generate(frequency, duration)
        
        # ADSRエンベロープ生成
        adsr = ADSREnvelope(
            attack=0.1, decay=0.2, sustain=0.7, release=0.3,
            config=self.config
        )
        envelope = adsr.generate(duration)
        
        # エンベロープ適用
        processed_signal = apply_envelope(signal, envelope)
        
        # 結果検証
        assert len(processed_signal) == len(signal)
        
        # エンベロープによる音量変化の確認
        assert processed_signal[0] == 0.0  # 開始は無音
        assert np.abs(processed_signal[-1]) < 0.1  # 終了は小音量
    
    def test_melody_generation(self):
        """メロディー生成のテスト（きらきら星）"""
        sine_osc = SineWave(self.config)
        adsr = ADSREnvelope(
            attack=0.01, decay=0.2, sustain=0.4, release=0.3,
            config=self.config
        )
        
        # きらきら星の最初の部分
        melody_notes = [
            ('C4', 0.5), ('C4', 0.5), ('G4', 0.5), ('G4', 0.5)
        ]
        
        melody_data = []
        
        for note_name, note_duration in melody_notes:
            # 音名からMIDI番号、周波数への変換
            midi_number = note_name_to_number(note_name)
            frequency = note_to_frequency(midi_number)
            
            # 音声生成
            signal = sine_osc.generate(frequency, note_duration)
            envelope = adsr.generate(note_duration)
            note_with_envelope = apply_envelope(signal, envelope)
            
            melody_data.append(note_with_envelope)
        
        # メロディー結合
        full_melody = np.concatenate(melody_data)
        
        # 結果検証
        assert len(full_melody) > 0
        expected_total_duration = sum(duration for _, duration in melody_notes)
        expected_samples = int(self.config.sample_rate * expected_total_duration)
        assert len(full_melody) == expected_samples


def test_integration_all_components():
    """全コンポーネントの統合テスト"""
    config = AudioConfig()
    
    # 1. オシレーター
    sine = SineWave(config)
    signal = sine.generate(440.0, 1.0)
    
    # 2. エンベロープ
    adsr = ADSREnvelope(attack=0.1, decay=0.2, sustain=0.5, release=0.3, config=config)
    envelope = adsr.generate(1.0)
    signal_with_envelope = apply_envelope(signal, envelope)
    
    # 3. エフェクト
    reverb = Reverb(room_size=0.7, damping=0.5)
    final_signal = reverb.apply(signal_with_envelope)
    
    # 4. ファイル保存
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        save_audio(temp_filename, config.sample_rate, final_signal)
        assert os.path.exists(temp_filename)
        assert os.path.getsize(temp_filename) > 0
        
        print(f"✅ 統合テスト成功: {len(final_signal)} サンプルの音声データを生成・保存")
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


if __name__ == "__main__":
    # 詳細な出力でテストを実行
    pytest.main([__file__, "-v", "--tb=short"])
