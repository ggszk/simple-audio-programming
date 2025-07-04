"""
デジタルフィルター

ローパス、ハイパス、バンドパスなどの基本的なフィルター
"""

import numpy as np
from ..core.audio_config import AudioConfig

class BaseFilter:
    """フィルターの基底クラス"""
    
    def __init__(self, config=None):
        self.config = config or AudioConfig()
        self.reset()
    
    def reset(self):
        """フィルターの状態をリセット"""
        self.x_history = [0.0, 0.0, 0.0]  # 入力履歴
        self.y_history = [0.0, 0.0, 0.0]  # 出力履歴
    
    def process(self, input_signal):
        """
        信号を処理（派生クラスで実装）
        
        Args:
            input_signal (np.ndarray): 入力信号
            
        Returns:
            np.ndarray: フィルター処理された信号
        """
        raise NotImplementedError("派生クラスで実装してください")

class BiquadFilter(BaseFilter):
    """2次IIRフィルター（バイクアッドフィルター）"""
    
    def __init__(self, b_coeffs, a_coeffs, config=None):
        """
        バイクアッドフィルターを初期化
        
        Args:
            b_coeffs (list): 分子係数 [b0, b1, b2]
            a_coeffs (list): 分母係数 [a0, a1, a2] (a0は通常1.0)
            config (AudioConfig): オーディオ設定
        """
        super().__init__(config)
        self.b = b_coeffs  # 分子係数
        self.a = a_coeffs  # 分母係数
    
    def process(self, input_signal):
        """
        バイクアッドフィルターで信号を処理
        
        Args:
            input_signal (np.ndarray): 入力信号
            
        Returns:
            np.ndarray: フィルター処理された信号
        """
        output = np.zeros_like(input_signal)
        
        for n, x_n in enumerate(input_signal):
            # 現在の出力を計算
            y_n = (self.b[0] * x_n + 
                   self.b[1] * self.x_history[0] + 
                   self.b[2] * self.x_history[1] - 
                   self.a[1] * self.y_history[0] - 
                   self.a[2] * self.y_history[1])
            
            output[n] = y_n
            
            # 履歴を更新
            self.x_history[1] = self.x_history[0]
            self.x_history[0] = x_n
            self.y_history[1] = self.y_history[0]
            self.y_history[0] = y_n
        
        return output

class LowPassFilter(BiquadFilter):
    """ローパスフィルター"""
    
    def __init__(self, cutoff_freq, q_factor=0.707, config=None):
        """
        ローパスフィルターを初期化
        
        Args:
            cutoff_freq (float): カットオフ周波数 (Hz)
            q_factor (float): Q値（品質係数）
            config (AudioConfig): オーディオ設定
        """
        if config is None:
            config = AudioConfig()
        
        # バイクアッド係数を計算
        omega = 2 * np.pi * cutoff_freq / config.sample_rate
        sin_omega = np.sin(omega)
        cos_omega = np.cos(omega)
        alpha = sin_omega / (2 * q_factor)
        
        # ローパスフィルターの係数
        b0 = (1 - cos_omega) / 2
        b1 = 1 - cos_omega
        b2 = (1 - cos_omega) / 2
        a0 = 1 + alpha
        a1 = -2 * cos_omega
        a2 = 1 - alpha
        
        # 正規化
        b_coeffs = [b0/a0, b1/a0, b2/a0]
        a_coeffs = [1.0, a1/a0, a2/a0]
        
        super().__init__(b_coeffs, a_coeffs, config)

class HighPassFilter(BiquadFilter):
    """ハイパスフィルター"""
    
    def __init__(self, cutoff_freq, q_factor=0.707, config=None):
        """
        ハイパスフィルターを初期化
        
        Args:
            cutoff_freq (float): カットオフ周波数 (Hz)
            q_factor (float): Q値（品質係数）
            config (AudioConfig): オーディオ設定
        """
        if config is None:
            config = AudioConfig()
        
        # バイクアッド係数を計算
        omega = 2 * np.pi * cutoff_freq / config.sample_rate
        sin_omega = np.sin(omega)
        cos_omega = np.cos(omega)
        alpha = sin_omega / (2 * q_factor)
        
        # ハイパスフィルターの係数
        b0 = (1 + cos_omega) / 2
        b1 = -(1 + cos_omega)
        b2 = (1 + cos_omega) / 2
        a0 = 1 + alpha
        a1 = -2 * cos_omega
        a2 = 1 - alpha
        
        # 正規化
        b_coeffs = [b0/a0, b1/a0, b2/a0]
        a_coeffs = [1.0, a1/a0, a2/a0]
        
        super().__init__(b_coeffs, a_coeffs, config)

class BandPassFilter(BiquadFilter):
    """バンドパスフィルター"""
    
    def __init__(self, center_freq, q_factor=1.0, config=None):
        """
        バンドパスフィルターを初期化
        
        Args:
            center_freq (float): 中心周波数 (Hz)
            q_factor (float): Q値（品質係数）
            config (AudioConfig): オーディオ設定
        """
        if config is None:
            config = AudioConfig()
        
        # バイクアッド係数を計算
        omega = 2 * np.pi * center_freq / config.sample_rate
        sin_omega = np.sin(omega)
        cos_omega = np.cos(omega)
        alpha = sin_omega / (2 * q_factor)
        
        # バンドパスフィルターの係数
        b0 = alpha
        b1 = 0
        b2 = -alpha
        a0 = 1 + alpha
        a1 = -2 * cos_omega
        a2 = 1 - alpha
        
        # 正規化
        b_coeffs = [b0/a0, b1/a0, b2/a0]
        a_coeffs = [1.0, a1/a0, a2/a0]
        
        super().__init__(b_coeffs, a_coeffs, config)

class SimpleMovingAverageFilter(BaseFilter):
    """移動平均フィルター（簡単なローパス効果）"""
    
    def __init__(self, window_size=3, config=None):
        """
        移動平均フィルターを初期化
        
        Args:
            window_size (int): 窓のサイズ
            config (AudioConfig): オーディオ設定
        """
        super().__init__(config)
        self.window_size = window_size
        self.buffer = np.zeros(window_size)
        self.index = 0
    
    def process(self, input_signal):
        """
        移動平均フィルターで信号を処理
        
        Args:
            input_signal (np.ndarray): 入力信号
            
        Returns:
            np.ndarray: フィルター処理された信号
        """
        output = np.zeros_like(input_signal)
        
        for n, x_n in enumerate(input_signal):
            # バッファに新しいサンプルを追加
            self.buffer[self.index] = x_n
            self.index = (self.index + 1) % self.window_size
            
            # 移動平均を計算
            output[n] = np.mean(self.buffer)
        
        return output
