"""
音響合成用オシレーター（波形生成器）

可読性を重視し、元のC言語的な書き方を改善
"""

import numpy as np
from ..core.audio_config import AudioConfig

class BaseOscillator:
    """オシレーターの基底クラス"""
    
    def __init__(self, config=None):
        self.config = config or AudioConfig()
    
    def generate(self, frequency, duration, phase=0.0):
        """
        基本波形を生成する（派生クラスで実装）
        
        Args:
            frequency (float): 周波数 (Hz)
            duration (float): 継続時間 (秒)
            phase (float): 初期位相 (0.0-1.0)
            
        Returns:
            np.ndarray: 生成された波形データ
        """
        raise NotImplementedError("派生クラスで実装してください")
    
    def _create_time_array(self, duration):
        """時間軸配列を作成"""
        num_samples = self.config.duration_to_samples(duration)
        return np.linspace(0, duration, num_samples, endpoint=False)

class SineWave(BaseOscillator):
    """正弦波オシレーター"""
    
    def generate(self, frequency, duration, phase=0.0):
        """
        正弦波を生成
        
        Args:
            frequency (float): 周波数 (Hz)
            duration (float): 継続時間 (秒)
            phase (float): 初期位相 (0.0-1.0)
            
        Returns:
            np.ndarray: 正弦波データ
        """
        t = self._create_time_array(duration)
        return np.sin(2 * np.pi * frequency * t + 2 * np.pi * phase)

class SawtoothWave(BaseOscillator):
    """ノコギリ波オシレーター（バンドリミット処理付き）"""
    
    def generate(self, frequency, duration, phase=0.0):
        """
        ノコギリ波を生成
        
        Args:
            frequency (float): 周波数 (Hz)  
            duration (float): 継続時間 (秒)
            phase (float): 初期位相 (0.0-1.0)
            
        Returns:
            np.ndarray: ノコギリ波データ
        """
        t = self._create_time_array(duration)
        
        # 位相を考慮したノコギリ波
        signal = 2.0 * ((frequency * t + phase) % 1.0) - 1.0
        
        # エイリアシング対策: 簡単なバンドリミット処理
        # 高次の倍音をカットしてエイリアシングを軽減
        if frequency > self.config.sample_rate / 8:
            # 周波数が高い場合は正弦波で近似
            return np.sin(2 * np.pi * frequency * t + 2 * np.pi * phase)
        
        return signal

class SquareWave(BaseOscillator):
    """矩形波オシレーター"""
    
    def generate(self, frequency, duration, phase=0.0, duty_cycle=0.5):
        """
        矩形波を生成
        
        Args:
            frequency (float): 周波数 (Hz)
            duration (float): 継続時間 (秒)
            phase (float): 初期位相 (0.0-1.0)
            duty_cycle (float): デューティ比 (0.0-1.0)
            
        Returns:
            np.ndarray: 矩形波データ
        """
        t = self._create_time_array(duration)
        
        # 位相を考慮した矩形波
        phase_signal = (frequency * t + phase) % 1.0
        
        # デューティ比に基づいて矩形波を生成
        signal = np.where(phase_signal < duty_cycle, 1.0, -1.0)
        
        return signal

class TriangleWave(BaseOscillator):
    """三角波オシレーター"""
    
    def generate(self, frequency, duration, phase=0.0):
        """
        三角波を生成
        
        Args:
            frequency (float): 周波数 (Hz)
            duration (float): 継続時間 (秒)
            phase (float): 初期位相 (0.0-1.0)
            
        Returns:
            np.ndarray: 三角波データ
        """
        t = self._create_time_array(duration)
        
        # 位相を考慮した三角波
        phase_signal = (frequency * t + phase) % 1.0
        
        # 三角波の生成
        signal = np.where(phase_signal < 0.5, 
                         4.0 * phase_signal - 1.0,  # 上昇部
                         3.0 - 4.0 * phase_signal)  # 下降部
        
        return signal

class NoiseGenerator(BaseOscillator):
    """ノイズジェネレーター"""
    
    def generate_white_noise(self, duration, amplitude=1.0):
        """
        ホワイトノイズを生成
        
        Args:
            duration (float): 継続時間 (秒)
            amplitude (float): 振幅
            
        Returns:
            np.ndarray: ホワイトノイズデータ
        """
        num_samples = self.config.duration_to_samples(duration)
        return amplitude * (2.0 * np.random.random(num_samples) - 1.0)
    
    def generate_pink_noise(self, duration, amplitude=1.0):
        """
        ピンクノイズを生成（簡易版）
        
        Args:
            duration (float): 継続時間 (秒)
            amplitude (float): 振幅
            
        Returns:
            np.ndarray: ピンクノイズデータ
        """
        # 簡易的なピンクノイズ生成
        white_noise = self.generate_white_noise(duration, amplitude)
        
        # ローパスフィルターでピンクノイズ的な特性を作る
        # 実際のピンクノイズはより複雑な処理が必要
        filtered = np.zeros_like(white_noise)
        b0, b1, b2 = 0.99765, -1.99530, 0.99765
        a1, a2 = -1.99530, 0.99530
        
        for i in range(2, len(white_noise)):
            filtered[i] = b0 * white_noise[i] + b1 * white_noise[i-1] + b2 * white_noise[i-2] - a1 * filtered[i-1] - a2 * filtered[i-2]
        
        return filtered
