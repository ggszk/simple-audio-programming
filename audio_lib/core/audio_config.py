"""
オーディオ処理の基本設定クラス

標準的なサンプリング周波数や音量設定を管理します
"""

class AudioConfig:
    """音響処理の基本設定を管理するクラス"""
    
    def __init__(self, sample_rate=44100, bit_depth=16):
        """
        オーディオ設定を初期化
        
        Args:
            sample_rate (int): サンプリング周波数 (Hz)
            bit_depth (int): ビット深度 (bits)
        """
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.max_amplitude = 0.95  # クリッピング防止のため最大振幅を制限
        
    def samples_per_second(self):
        """1秒あたりのサンプル数を返す"""
        return self.sample_rate
    
    def duration_to_samples(self, duration_seconds):
        """
        時間(秒)をサンプル数に変換
        
        Args:
            duration_seconds (float): 時間(秒)
            
        Returns:
            int: サンプル数
        """
        return int(self.sample_rate * duration_seconds)
    
    def samples_to_duration(self, num_samples):
        """
        サンプル数を時間(秒)に変換
        
        Args:
            num_samples (int): サンプル数
            
        Returns:
            float: 時間(秒)
        """
        return num_samples / self.sample_rate
