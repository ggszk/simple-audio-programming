"""
ノートブック教材の動作確認テスト

このテストファイルは、各レッスンノートブックで使用される機能が
正しく動作することを確認します。教育現場での問題を事前に発見できます。
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


class TestLesson01BasicsAndSineWaves:
    """Lesson 1: サイン波と基礎 - ノートブック内容の動作確認"""
    
    def setup_method(self):
        """テスト準備"""
        self.config = AudioConfig()
        self.sine_osc = SineWave(self.config)
    
    def test_basic_sine_wave_generation(self):
        """基本的なサイン波生成（ノートブックセル再現）"""
        # ノートブックでの実行内容
        frequency = 440.0
        duration = 1.0
        signal = self.sine_osc.generate(frequency, duration)
        
        print(f"✅ 440.0Hzの音を1.0秒分生成しました")
        print(f"データの長さ: {len(signal)} サンプル")
        print(f"最大振幅: {np.max(signal):.3f}")
        print(f"最小振幅: {np.min(signal):.3f}")
        
        assert len(signal) == 44100
        assert abs(np.max(signal) - 1.0) < 0.1
        assert abs(np.min(signal) - (-1.0)) < 0.1
    
    def test_different_frequencies(self):
        """異なる周波数での音生成テスト"""
        frequencies = [220, 440, 880, 1760]  # ノートブックと同じ周波数
        
        for freq in frequencies:
            signal = self.sine_osc.generate(freq, 1.0)
            print(f"🎵 {freq}Hz の音を生成")
            
            assert len(signal) == 44100
            assert -1.0 <= np.min(signal) <= 1.0
            assert -1.0 <= np.max(signal) <= 1.0
    
    def test_volume_variations(self):
        """音量変化のテスト（ノートブック Volume Test再現）"""
        volumes = [0.1, 0.3, 1.0, 0.8]
        
        for volume in volumes:
            signal = self.sine_osc.generate(440.0, 1.0)
            signal_with_volume = signal * volume  # 振幅調整
            max_amplitude = np.max(np.abs(signal_with_volume))
            
            print(f"🔊 振幅{volume}倍の音 - 実際の最大振幅: {max_amplitude:.3f}")
            assert abs(max_amplitude - volume) < 0.1
    
    def test_note_frequency_conversion(self):
        """音名と周波数の変換テスト"""
        # ノートブックの音名テーブル
        note_table = {
            'C4': 60, 'D4': 62, 'E4': 64, 'F4': 65,
            'G4': 67, 'A4': 69, 'B4': 71, 'C5': 72
        }
        
        print("🎹 音名と周波数の対応確認:")
        for note_name, expected_midi in note_table.items():
            midi_number = note_name_to_number(note_name)
            frequency = note_to_frequency(midi_number)
            
            print(f"{note_name} -> MIDI:{midi_number} -> {frequency:.1f}Hz")
            assert midi_number == expected_midi
    
    def test_melody_generation(self):
        """ドレミファソラシド メロディー生成テスト"""
        melody_notes = [
            ('C4', 0.5), ('D4', 0.5), ('E4', 0.5), ('F4', 0.5),
            ('G4', 0.5), ('A4', 0.5), ('B4', 0.5), ('C5', 0.5)
        ]
        
        melody_data = []
        for note_name, note_duration in melody_notes:
            midi_number = note_name_to_number(note_name)
            frequency = note_to_frequency(midi_number)
            signal = self.sine_osc.generate(frequency, note_duration)
            melody_data.append(signal)
        
        full_melody = np.concatenate(melody_data)
        expected_length = int(self.config.sample_rate * 4.0)  # 8音 × 0.5秒
        
        print(f"🎵 ドレミファソラシド メロディー生成完了")
        print(f"総長: {len(full_melody)} サンプル (期待値: {expected_length})")
        assert len(full_melody) == expected_length
    
    def test_harmony_generation(self):
        """和音生成テスト"""
        freq1 = 440  # ラ
        freq2 = 554  # 約5度上
        duration = 2.0
        
        signal1 = self.sine_osc.generate(freq1, duration)
        signal2 = self.sine_osc.generate(freq2, duration)
        harmony = signal1 + signal2
        
        print(f"🎵 和音: {freq1}Hz + {freq2}Hz")
        assert len(harmony) == len(signal1)
        assert len(harmony) == len(signal2)


class TestLesson02EnvelopesAndADSR:
    """Lesson 2: エンベロープとADSR - ノートブック内容の動作確認"""
    
    def setup_method(self):
        """テスト準備"""
        self.config = AudioConfig()
        self.sine_osc = SineWave(self.config)
    
    def test_raw_signal_click_problem(self):
        """クリック音問題の確認"""
        frequency = 440
        duration = 1.0
        raw_signal = self.sine_osc.generate(frequency, duration)
        
        print("🚨 クリック音問題の確認:")
        print(f"📊 信号の急激な変化: 開始値={raw_signal[0]:.3f}, 終了値={raw_signal[-1]:.3f}")
        
        # 開始・終了が0でないことを確認（クリック音の原因）
        # サイン波の開始は常に0だが、終了時は0でない場合がある
        assert abs(raw_signal[0]) == 0.0  # サイン波は0から開始
        assert abs(raw_signal[-1]) > 0.01  # 終了時は0でないことが多い（クリック音の原因）
    
    def test_linear_envelope(self):
        """リニアエンベロープのテスト"""
        fade_envelope = LinearEnvelope(
            fade_in=0.1, fade_out=0.1, config=self.config
        )
        duration = 1.0
        envelope_data = fade_envelope.generate(duration)
        
        print("📊 リニアエンベロープ特性:")
        print(f"開始値: {envelope_data[0]:.3f}")
        print(f"最大値: {np.max(envelope_data):.3f}")
        print(f"終了値: {envelope_data[-1]:.3f}")
        
        assert envelope_data[0] == 0.0  # フェードイン開始
        assert envelope_data[-1] == 0.0  # フェードアウト終了
        assert np.max(envelope_data) <= 1.0
    
    def test_adsr_envelope_basic(self):
        """基本ADSRエンベロープのテスト"""
        adsr = ADSREnvelope(
            attack=0.1, decay=0.2, sustain=0.7, release=0.5,
            config=self.config
        )
        duration = 2.0
        adsr_data = adsr.generate(duration)
        
        print("📊 ADSR エンベロープ特性:")
        print(f"Attack: {adsr.attack}s, Decay: {adsr.decay}s")
        print(f"Sustain: {adsr.sustain}, Release: {adsr.release}s")
        print(f"最大値: {np.max(adsr_data):.3f}")
        
        assert len(adsr_data) == int(self.config.sample_rate * duration)
        assert adsr_data[0] == 0.0  # アタック開始
        assert np.max(adsr_data) <= 1.0
    
    def test_envelope_application(self):
        """エンベロープ適用のテスト"""
        # 音声信号生成
        frequency = 440
        duration = 2.0
        signal = self.sine_osc.generate(frequency, duration)
        
        # ADSRエンベロープ生成
        adsr = ADSREnvelope(
            attack=0.1, decay=0.2, sustain=0.7, release=0.5,
            config=self.config
        )
        adsr_data = adsr.generate(duration)
        
        # エンベロープ適用
        adsr_signal = apply_envelope(signal, adsr_data)
        
        print("🔊 エンベロープ適用結果:")
        print(f"元信号の最大振幅: {np.max(np.abs(signal)):.3f}")
        print(f"処理後の最大振幅: {np.max(np.abs(adsr_signal)):.3f}")
        
        assert len(adsr_signal) == len(signal)
        assert np.max(np.abs(adsr_signal)) <= np.max(np.abs(signal))
    
    def test_instrument_simulation(self):
        """楽器シミュレーションのテスト"""
        duration = 3.0
        signal = self.sine_osc.generate(440, duration)
        
        # ピアノらしい音
        piano_adsr = ADSREnvelope(
            attack=0.01, decay=0.3, sustain=0.3, release=1.5,
            config=self.config
        )
        piano_envelope = piano_adsr.generate(duration)
        piano_sound = apply_envelope(signal, piano_envelope)
        
        # オルガンらしい音
        organ_adsr = ADSREnvelope(
            attack=0.05, decay=0.0, sustain=1.0, release=0.1,
            config=self.config
        )
        organ_envelope = organ_adsr.generate(duration)
        organ_sound = apply_envelope(signal, organ_envelope)
        
        # 弦楽器らしい音
        string_adsr = ADSREnvelope(
            attack=0.3, decay=0.1, sustain=0.8, release=0.4,
            config=self.config
        )
        string_envelope = string_adsr.generate(duration)
        string_sound = apply_envelope(signal, string_envelope)
        
        print("🎹 楽器シミュレーション結果:")
        print(f"ピアノ音の最大振幅: {np.max(np.abs(piano_sound)):.3f}")
        print(f"オルガン音の最大振幅: {np.max(np.abs(organ_sound)):.3f}")
        print(f"弦楽器音の最大振幅: {np.max(np.abs(string_sound)):.3f}")
        
        # 各楽器音が異なることを確認
        assert not np.array_equal(piano_sound, organ_sound)
        assert not np.array_equal(piano_sound, string_sound)
    
    def test_twinkle_star_melody(self):
        """きらきら星メロディーのテスト（ノートブック再現）"""
        melody_notes = [
            ('C4', 0.5), ('C4', 0.5), ('G4', 0.5), ('G4', 0.5),
            ('A4', 0.5), ('A4', 0.5), ('G4', 1.0),
            ('F4', 0.5), ('F4', 0.5), ('E4', 0.5), ('E4', 0.5),
            ('D4', 0.5), ('D4', 0.5), ('C4', 1.0)
        ]
        
        melody_adsr = ADSREnvelope(
            attack=0.01, decay=0.2, sustain=0.4, release=0.3,
            config=self.config
        )
        
        melody_audio_data = []
        for note_name, note_duration in melody_notes:
            midi_number = note_name_to_number(note_name)
            frequency = note_to_frequency(midi_number)
            note_signal = self.sine_osc.generate(frequency, note_duration)
            envelope_data = melody_adsr.generate(note_duration)
            note_with_envelope = apply_envelope(note_signal, envelope_data)
            melody_audio_data.append(note_with_envelope)
        
        full_melody = np.concatenate(melody_audio_data)
        
        print("🌟 きらきら星メロディー生成完了")
        print(f"総音符数: {len(melody_notes)}")
        print(f"メロディー長: {len(full_melody)} サンプル")
        
        # 期待される長さの計算
        total_duration = sum(duration for _, duration in melody_notes)
        expected_samples = int(self.config.sample_rate * total_duration)
        
        assert len(full_melody) == expected_samples


class TestLesson03FiltersAndSoundDesign:
    """Lesson 3: フィルターと音響設計 - 主要機能テスト"""
    
    def setup_method(self):
        """テスト準備"""
        self.config = AudioConfig()
        self.sawtooth = SawtoothWave(self.config)
    
    def test_low_pass_filter(self):
        """ローパスフィルターのテスト"""
        signal = self.sawtooth.generate(440, 1.0)
        lpf = LowPassFilter(cutoff_freq=1000, config=self.config)
        filtered = lpf.process(signal)
        
        print("🔽 ローパスフィルター適用")
        print(f"元信号RMS: {np.sqrt(np.mean(signal**2)):.3f}")
        print(f"フィルター後RMS: {np.sqrt(np.mean(filtered**2)):.3f}")
        
        assert len(filtered) == len(signal)
    
    def test_high_pass_filter(self):
        """ハイパスフィルターのテスト"""
        signal = self.sawtooth.generate(440, 1.0)
        hpf = HighPassFilter(cutoff_freq=1000, config=self.config)
        filtered = hpf.process(signal)
        
        print("🔼 ハイパスフィルター適用")
        print(f"元信号RMS: {np.sqrt(np.mean(signal**2)):.3f}")
        print(f"フィルター後RMS: {np.sqrt(np.mean(filtered**2)):.3f}")
        
        assert len(filtered) == len(signal)


class TestLesson04AudioEffectsAndDynamics:
    """Lesson 4: オーディオエフェクトとダイナミクス - 主要機能テスト"""
    
    def setup_method(self):
        """テスト準備"""
        self.config = AudioConfig()
        self.sine = SineWave(self.config)
        self.test_signal = self.sine.generate(440, 1.0)
    
    def test_compression_effect(self):
        """コンプレッション効果のテスト"""
        compressed = apply_compression(
            self.test_signal,
            threshold=0.5,
            ratio=4.0,
            attack=0.01,
            release=0.1
        )
        
        print("🗜️ コンプレッション適用")
        print(f"元信号ピーク: {np.max(np.abs(self.test_signal)):.3f}")
        print(f"圧縮後ピーク: {np.max(np.abs(compressed)):.3f}")
        
        assert len(compressed) == len(self.test_signal)
    
    def test_reverb_effect(self):
        """リバーブ効果のテスト"""
        reverb = Reverb(room_size=0.7, damping=0.5)
        processed = reverb.apply(self.test_signal)
        
        print("🏛️ リバーブ適用")
        print(f"元信号長: {len(self.test_signal)}")
        print(f"処理後長: {len(processed)}")
        
        assert len(processed) == len(self.test_signal)
    
    def test_delay_effect(self):
        """ディレイ効果のテスト"""
        delay = Delay(delay_time=0.3, feedback=0.4, wet_level=0.3)
        processed = delay.apply(self.test_signal, self.config.sample_rate)
        
        print("🔄 ディレイ適用")
        print(f"ディレイタイム: 0.3秒")
        print(f"フィードバック: 0.4")
        
        assert len(processed) == len(self.test_signal)
    
    def test_chorus_effect(self):
        """コーラス効果のテスト"""
        chorus = Chorus(rate=1.5, depth=0.005, wet_level=0.5)
        processed = chorus.apply(self.test_signal, self.config.sample_rate)
        
        print("🎭 コーラス適用")
        print(f"レート: 1.5Hz, デプス: 0.005")
        
        assert len(processed) == len(self.test_signal)
    
    def test_distortion_effect(self):
        """ディストーション効果のテスト"""
        distortion = Distortion(gain=10.0, output_level=0.7)
        processed = distortion.apply(self.test_signal)
        
        print("🔥 ディストーション適用")
        print(f"ゲイン: 10.0, 出力レベル: 0.7")
        
        assert len(processed) == len(self.test_signal)


def test_complete_educational_workflow():
    """完全な教育ワークフローのテスト"""
    print("\n🎓 完全な教育ワークフロー統合テスト")
    
    config = AudioConfig()
    
    # 1. 基本音声生成 (Lesson 1)
    sine = SineWave(config)
    base_signal = sine.generate(440.0, 2.0)
    print("1️⃣ 基本サイン波生成完了")
    
    # 2. エンベロープ適用 (Lesson 2)
    adsr = ADSREnvelope(attack=0.1, decay=0.2, sustain=0.6, release=0.4, config=config)
    envelope = adsr.generate(2.0)
    signal_with_envelope = apply_envelope(base_signal, envelope)
    print("2️⃣ ADSRエンベロープ適用完了")
    
    # 3. フィルター適用 (Lesson 3)
    lpf = LowPassFilter(cutoff_freq=2000, config=config)
    filtered_signal = lpf.process(signal_with_envelope)
    print("3️⃣ ローパスフィルター適用完了")
    
    # 4. エフェクト適用 (Lesson 4)
    reverb = Reverb(room_size=0.5, damping=0.4)
    final_signal = reverb.apply(filtered_signal)
    print("4️⃣ リバーブエフェクト適用完了")
    
    # 5. ファイル保存テスト
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        save_audio(temp_filename, config.sample_rate, final_signal)
        print("5️⃣ WAVファイル保存完了")
        
        # 保存成功確認
        assert os.path.exists(temp_filename)
        assert os.path.getsize(temp_filename) > 0
        
        print(f"✅ 教育ワークフロー完了! 最終信号長: {len(final_signal)} サンプル")
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


if __name__ == "__main__":
    # 詳細出力でテスト実行
    pytest.main([__file__, "-v", "-s", "--tb=short"])
