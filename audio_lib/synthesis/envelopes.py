"""
エンベロープ（音量変化）処理

ADSR、リニア、コサイン型など、様々なエンベロープを提供
"""

import numpy as np
from ..core.audio_config import AudioConfig

class BaseEnvelope:
    """エンベロープの基底クラス"""
    
    def __init__(self, config=None):
        self.config = config or AudioConfig()
    
    def generate(self, duration):
        """
        エンベロープを生成（派生クラスで実装）
        
        Args:
            duration (float): 継続時間 (秒)
            
        Returns:
            np.ndarray: エンベロープデータ
        """
        raise NotImplementedError("派生クラスで実装してください")

class ADSREnvelope(BaseEnvelope):
    """ADSR（Attack, Decay, Sustain, Release）エンベロープ"""
    
    def __init__(self, attack=0.1, decay=0.1, sustain=0.7, release=0.2, config=None):
        """
        ADSRエンベロープを初期化
        
        Args:
            attack (float): アタック時間 (秒)
            decay (float): ディケイ時間 (秒)
            sustain (float): サステインレベル (0.0-1.0)
            release (float): リリース時間 (秒)
            config (AudioConfig): オーディオ設定
        """
        super().__init__(config)
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
    
    def generate(self, duration, gate_time=None):
        """
        ADSRエンベロープを生成
        
        Args:
            duration (float): 全体の継続時間 (秒)
            gate_time (float): ゲート時間 (秒)。Noneの場合はduration - release
            
        Returns:
            np.ndarray: ADSRエンベロープデータ
        """
        if gate_time is None:
            gate_time = max(0, duration - self.release)
        
        num_samples = self.config.duration_to_samples(duration)
        envelope = np.zeros(num_samples)
        
        # サンプル単位での時間計算
        attack_samples = self.config.duration_to_samples(self.attack)
        decay_samples = self.config.duration_to_samples(self.decay)
        gate_samples = self.config.duration_to_samples(gate_time)
        release_samples = self.config.duration_to_samples(self.release)
        
        # アタック段階
        attack_end = min(attack_samples, num_samples)
        if attack_samples > 0:
            for n in range(attack_end):
                # 指数的なアタックカーブ
                envelope[n] = (1 - np.exp(-5 * n / attack_samples)) / (1 - np.exp(-5))
        
        # ディケイ段階
        decay_start = attack_end
        decay_end = min(decay_start + decay_samples, gate_samples, num_samples)
        if decay_samples > 0 and decay_end > decay_start:
            for n in range(decay_start, decay_end):
                progress = (n - decay_start) / decay_samples
                envelope[n] = 1.0 + (self.sustain - 1.0) * (1 - np.exp(-5 * progress))
        
        # サステイン段階
        sustain_start = decay_end
        sustain_end = min(gate_samples, num_samples)
        if sustain_end > sustain_start:
            envelope[sustain_start:sustain_end] = self.sustain
        
        # リリース段階
        release_start = min(gate_samples, num_samples)
        release_end = min(release_start + release_samples, num_samples)
        if release_samples > 0 and release_end > release_start:
            initial_level = self.sustain if release_start < len(envelope) else envelope[release_start-1]
            for n in range(release_start, release_end):
                progress = (n - release_start) / release_samples
                envelope[n] = initial_level * np.exp(-5 * progress)
        
        return envelope

class LinearEnvelope(BaseEnvelope):
    """リニア（直線的）エンベロープ"""
    
    def __init__(self, fade_in=0.01, fade_out=0.01, config=None):
        """
        リニアエンベロープを初期化
        
        Args:
            fade_in (float): フェードイン時間 (秒)
            fade_out (float): フェードアウト時間 (秒)
            config (AudioConfig): オーディオ設定
        """
        super().__init__(config)
        self.fade_in = fade_in
        self.fade_out = fade_out
    
    def generate(self, duration):
        """
        リニアエンベロープを生成
        
        Args:
            duration (float): 継続時間 (秒)
            
        Returns:
            np.ndarray: リニアエンベロープデータ
        """
        num_samples = self.config.duration_to_samples(duration)
        envelope = np.ones(num_samples)
        
        fade_in_samples = self.config.duration_to_samples(self.fade_in)
        fade_out_samples = self.config.duration_to_samples(self.fade_out)
        
        # フェードイン
        fade_in_end = min(fade_in_samples, num_samples)
        if fade_in_samples > 0:
            envelope[:fade_in_end] = np.linspace(0, 1, fade_in_end)
        
        # フェードアウト
        fade_out_start = max(0, num_samples - fade_out_samples)
        if fade_out_samples > 0 and fade_out_start < num_samples:
            envelope[fade_out_start:] = np.linspace(1, 0, num_samples - fade_out_start)
        
        return envelope

class CosineEnvelope(BaseEnvelope):
    """コサイン型エンベロープ（滑らかな変化）"""
    
    def __init__(self, attack=0.1, release=0.1, config=None):
        """
        コサインエンベロープを初期化
        
        Args:
            attack (float): アタック時間 (秒)
            release (float): リリース時間 (秒)
            config (AudioConfig): オーディオ設定
        """
        super().__init__(config)
        self.attack = attack
        self.release = release
    
    def generate(self, duration, sustain_level=1.0):
        """
        コサインエンベロープを生成
        
        Args:
            duration (float): 継続時間 (秒)
            sustain_level (float): サステインレベル (0.0-1.0)
            
        Returns:
            np.ndarray: コサインエンベロープデータ
        """
        num_samples = self.config.duration_to_samples(duration)
        envelope = np.ones(num_samples) * sustain_level
        
        attack_samples = self.config.duration_to_samples(self.attack)
        release_samples = self.config.duration_to_samples(self.release)
        
        # アタック（コサインカーブ）
        attack_end = min(attack_samples, num_samples)
        if attack_samples > 0:
            for n in range(attack_end):
                progress = n / attack_samples
                envelope[n] = sustain_level * (0.5 - 0.5 * np.cos(np.pi * progress))
        
        # リリース（コサインカーブ）
        release_start = max(0, num_samples - release_samples)
        if release_samples > 0 and release_start < num_samples:
            for n in range(release_start, num_samples):
                progress = (n - release_start) / release_samples
                envelope[n] = sustain_level * (0.5 + 0.5 * np.cos(np.pi * progress))
        
        return envelope

def apply_envelope(signal, envelope):
    """
    信号にエンベロープを適用
    
    Args:
        signal (np.ndarray): 入力信号
        envelope (np.ndarray): エンベロープ
        
    Returns:
        np.ndarray: エンベロープが適用された信号
    """
    # 長さを合わせる
    min_length = min(len(signal), len(envelope))
    return signal[:min_length] * envelope[:min_length]
