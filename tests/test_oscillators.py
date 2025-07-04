"""
オシレーター（波形生成器）のテスト

このテストファイルは、基本的なオシレーターの動作を検証します。
音響プログラミングにおいて、波形生成は最も基本的な要素です。
"""

import numpy as np
import pytest
from audio_lib.synthesis.oscillators import SineWave, SquareWave, SawtoothWave, TriangleWave


class TestSineWave:
    """サイン波オシレーターのテスト"""
    
    def test_sine_wave_generation(self):
        """基本的なサイン波生成のテスト"""
        oscillator = SineWave()
        frequency = 440.0  # A4 音程
        duration = 1.0     # 1秒
        sample_rate = 44100
        
        # サイン波を生成
        signal = oscillator.generate(frequency, duration, sample_rate)
        
        # 期待される長さの確認
        expected_length = int(sample_rate * duration)
        assert len(signal) == expected_length
        
        # 振幅範囲の確認（正規化されたサイン波は -1 から 1 の範囲）
        assert -1.0 <= signal.min()
        assert signal.max() <= 1.0
        
        # サイン波の性質確認（最大値と最小値が存在する）
        assert np.abs(signal.max() - 1.0) < 0.1  # 最大値がほぼ1
        assert np.abs(signal.min() - (-1.0)) < 0.1  # 最小値がほぼ-1
    
    def test_frequency_accuracy(self):
        """周波数の正確性をテスト"""
        oscillator = SineWave()
        frequency = 1000.0  # 1kHz
        duration = 1.0
        sample_rate = 44100
        
        signal = oscillator.generate(frequency, duration, sample_rate)
        
        # FFT で周波数成分を分析
        fft_result = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/sample_rate)
        
        # 正の周波数のみを取得
        positive_freqs = freqs[:len(freqs)//2]
        magnitude = np.abs(fft_result[:len(fft_result)//2])
        
        # 最大振幅を持つ周波数を特定
        peak_freq_index = np.argmax(magnitude)
        detected_frequency = positive_freqs[peak_freq_index]
        
        # 検出された周波数が期待値と近いかチェック（許容誤差: ±5Hz）
        assert abs(detected_frequency - frequency) < 5.0
    
    def test_amplitude_parameter(self):
        """振幅パラメータのテスト"""
        oscillator = SineWave()
        frequency = 440.0
        duration = 0.1
        amplitude = 0.5
        
        signal = oscillator.generate(frequency, duration)
        signal_with_amplitude = signal * amplitude  # 振幅調整
        
        # 振幅が指定値に近いかチェック
        max_amplitude = np.max(np.abs(signal_with_amplitude))
        assert abs(max_amplitude - amplitude) < 0.1


class TestSquareWave:
    """矩形波オシレーターのテスト"""
    
    def test_square_wave_generation(self):
        """基本的な矩形波生成のテスト"""
        oscillator = SquareWave()
        signal = oscillator.generate(frequency=440.0, duration=0.1)
        
        # 矩形波の特徴：値が二つの極値付近に集中
        unique_values = np.unique(np.round(signal, 1))
        assert len(unique_values) <= 10  # 矩形波は離散的な値を持つ
    
    def test_duty_cycle(self):
        """デューティサイクルのテスト"""
        oscillator = SquareWave()
        duty_cycle = 0.25  # 25%
        
        signal = oscillator.generate(
            frequency=100.0, 
            duration=0.1, 
            duty_cycle=duty_cycle
        )
        
        # デューティサイクルの近似確認
        positive_samples = np.sum(signal > 0)
        total_samples = len(signal)
        actual_duty_cycle = positive_samples / total_samples
        
        # 許容誤差範囲内かチェック
        assert abs(actual_duty_cycle - duty_cycle) < 0.1


class TestWaveformComparison:
    """波形間の比較テスト"""
    
    def test_different_waveforms(self):
        """異なる波形の特性比較"""
        frequency = 440.0
        duration = 0.1
        
        sine = SineWave().generate(frequency, duration)
        square = SquareWave().generate(frequency, duration)
        sawtooth = SawtoothWave().generate(frequency, duration)
        triangle = TriangleWave().generate(frequency, duration)
        
        # すべての波形が同じ長さであることを確認
        length = len(sine)
        assert len(square) == length
        assert len(sawtooth) == length
        assert len(triangle) == length
        
        # 波形間で違いがあることを確認（完全に同じではない）
        assert not np.array_equal(sine, square)
        assert not np.array_equal(sine, sawtooth)
        assert not np.array_equal(square, triangle)
    
    def test_harmonic_content(self):
        """高調波成分の比較テスト"""
        frequency = 440.0
        duration = 1.0
        sample_rate = 44100
        
        sine = SineWave().generate(frequency, duration, sample_rate)
        square = SquareWave().generate(frequency, duration, sample_rate)
        
        # FFT による周波数解析
        sine_fft = np.abs(np.fft.fft(sine))
        square_fft = np.abs(np.fft.fft(square))
        
        # 矩形波はサイン波よりも高調波成分が豊富
        # 基本波以外の成分の総和を比較
        fundamental_bin = int(frequency * len(sine) / sample_rate)
        
        sine_harmonics = np.sum(sine_fft[fundamental_bin*2:fundamental_bin*10])
        square_harmonics = np.sum(square_fft[fundamental_bin*2:fundamental_bin*10])
        
        # 矩形波の高調波成分がサイン波より多いことを確認
        assert square_harmonics > sine_harmonics


if __name__ == "__main__":
    # 単体でテストを実行する場合
    pytest.main([__file__, "-v"])
