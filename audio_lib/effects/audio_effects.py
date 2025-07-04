"""
音響エフェクト

リバーブ、ディストーション、ディレイなどの効果処理
"""

import numpy as np
from ..core.audio_config import AudioConfig

# エクスポート対象を明示
__all__ = [
    'Reverb',
    'Distortion', 
    'Delay',
    'Chorus',
    'Compressor',
    'apply_compression'
]

class Reverb:
    """リバーブ（残響）エフェクト"""
    
    def __init__(self, room_size=0.5, damping=0.5, wet_level=0.3, reverb_time=None, config=None):
        """
        リバーブエフェクトを初期化
        
        Args:
            room_size (float): 部屋のサイズ (0.0-1.0)
            damping (float): ダンピング量 (0.0-1.0) 
            wet_level (float): エフェクト音のレベル (0.0-1.0)
            reverb_time (float): 残響時間 (秒) - 後方互換性のため
            config (AudioConfig): オーディオ設定
        """
        self.config = config or AudioConfig()
        self.room_size = room_size
        self.damping = damping
        self.wet_level = wet_level
        self.dry_level = 1.0 - wet_level
        
        # room_sizeとdampingからreverb_timeを計算
        if reverb_time is not None:
            self.reverb_time = reverb_time
        else:
            self.reverb_time = room_size * 2.0  # room_sizeから残響時間を推定
        
        # 遅延ラインの設定
        self.delay_times = [0.03, 0.05, 0.07, 0.09]  # 複数の遅延時間
        self.delays = []
        self.feedbacks = []
        
        for delay_time in self.delay_times:
            delay_samples = int(delay_time * self.config.sample_rate)
            self.delays.append(np.zeros(delay_samples))
            # フィードバック量を残響時間に基づいて設定（安定性のため上限を設定）
            feedback = np.exp(-3 * delay_time / self.reverb_time)
            # フィードバックの上限を0.9に制限（安定性とノイズ防止）
            feedback = min(feedback, 0.9)
            self.feedbacks.append(feedback)
        
        self.delay_indices = [0] * len(self.delays)
    
    def process(self, input_signal):
        """
        リバーブエフェクトを適用
        
        Args:
            input_signal (np.ndarray): 入力信号
            
        Returns:
            np.ndarray: リバーブが適用された信号
        """
        output = np.zeros_like(input_signal)
        
        for n, x_n in enumerate(input_signal):
            reverb_sum = 0.0
            
            # 各遅延ラインの処理
            for i, (delay_line, feedback) in enumerate(zip(self.delays, self.feedbacks)):
                # 遅延した信号を取得
                delayed_sample = delay_line[self.delay_indices[i]]
                reverb_sum += delayed_sample
                
                # ダンピングを適用したフィードバック
                damped_feedback = feedback * self.damping
                
                # 新しい値を遅延ラインに書き込み
                delay_line[self.delay_indices[i]] = x_n + damped_feedback * delayed_sample
                
                # インデックスを更新
                self.delay_indices[i] = (self.delay_indices[i] + 1) % len(delay_line)
            
            # ドライ音とウェット音をミックス
            wet_signal = reverb_sum / len(self.delays)
            output[n] = self.dry_level * x_n + self.wet_level * wet_signal
        
        # 出力の正規化（クリッピング防止）
        max_amplitude = np.max(np.abs(output))
        if max_amplitude > 1.0:
            output = output / max_amplitude
        
        return output
    
    def apply(self, input_signal, sample_rate=None):
        """
        リバーブエフェクトを適用（教育用便利メソッド）
        
        Args:
            input_signal (np.ndarray): 入力信号
            sample_rate (int): サンプリングレート（未使用、互換性のため）
            
        Returns:
            np.ndarray: リバーブが適用された信号
        """
        return self.process(input_signal)

class Distortion:
    """ディストーション（歪み）エフェクト"""
    
    def __init__(self, gain=10.0, output_level=0.5, config=None):
        """
        ディストーションエフェクトを初期化
        
        Args:
            gain (float): ゲイン（歪みの強さ）
            output_level (float): 出力レベル (0.0-1.0)
            config (AudioConfig): オーディオ設定
        """
        self.config = config or AudioConfig()
        self.gain = gain
        self.output_level = output_level
    
    def process(self, input_signal):
        """
        ディストーションエフェクトを適用
        
        Args:
            input_signal (np.ndarray): 入力信号
            
        Returns:
            np.ndarray: ディストーションが適用された信号
        """
        # ゲインを適用
        amplified = input_signal * self.gain
        
        # ソフトクリッピング（tanh関数を使用）
        distorted = np.tanh(amplified)
        
        # 出力レベルを調整
        return distorted * self.output_level

    def apply(self, input_signal, sample_rate=None):
        """
        ディストーションエフェクトを適用（教育用便利メソッド）
        
        Args:
            input_signal (np.ndarray): 入力信号
            sample_rate (int): サンプリングレート（未使用、互換性のため）
            
        Returns:
            np.ndarray: ディストーションが適用された信号
        """
        return self.process(input_signal)

class Delay:
    """ディレイ（遅延）エフェクト"""
    
    def __init__(self, delay_time=0.3, feedback=0.3, wet_level=0.3, config=None):
        """
        ディレイエフェクトを初期化
        
        Args:
            delay_time (float): 遅延時間 (秒)
            feedback (float): フィードバック量 (0.0-1.0)
            wet_level (float): エフェクト音のレベル (0.0-1.0)
            config (AudioConfig): オーディオ設定
        """
        self.config = config or AudioConfig()
        self.feedback = feedback
        self.wet_level = wet_level
        self.dry_level = 1.0 - wet_level
        
        # 遅延バッファ
        delay_samples = int(delay_time * self.config.sample_rate)
        self.delay_buffer = np.zeros(delay_samples)
        self.delay_index = 0
    
    def process(self, input_signal):
        """
        ディレイエフェクトを適用
        
        Args:
            input_signal (np.ndarray): 入力信号
            
        Returns:
            np.ndarray: ディレイが適用された信号
        """
        output = np.zeros_like(input_signal)
        
        for n, x_n in enumerate(input_signal):
            # 遅延した信号を取得
            delayed_sample = self.delay_buffer[self.delay_index]
            
            # フィードバックを含む新しい値をバッファに書き込み
            self.delay_buffer[self.delay_index] = x_n + self.feedback * delayed_sample
            
            # 出力を計算（ドライ音 + ウェット音）
            output[n] = self.dry_level * x_n + self.wet_level * delayed_sample
            
            # インデックスを更新
            self.delay_index = (self.delay_index + 1) % len(self.delay_buffer)
        
        return output

    def apply(self, input_signal, sample_rate=None):
        """
        ディレイエフェクトを適用（教育用便利メソッド）
        
        Args:
            input_signal (np.ndarray): 入力信号
            sample_rate (int): サンプリングレート（未使用、互換性のため）
            
        Returns:
            np.ndarray: ディレイが適用された信号
        """
        return self.process(input_signal)

class Chorus:
    """コーラスエフェクト（簡易版）"""
    
    def __init__(self, rate=2.0, depth=0.002, wet_level=0.5, config=None):
        """
        コーラスエフェクトを初期化
        
        Args:
            rate (float): モジュレーション周波数 (Hz)
            depth (float): モジュレーションの深さ (秒)
            wet_level (float): エフェクト音のレベル (0.0-1.0)
            config (AudioConfig): オーディオ設定
        """
        self.config = config or AudioConfig()
        self.rate = rate
        self.depth = depth
        self.wet_level = wet_level
        self.dry_level = 1.0 - wet_level
        
        # モジュレーション用のカウンター
        self.phase = 0.0
        
        # 遅延バッファ
        max_delay_samples = int((depth * 2) * self.config.sample_rate) + 1
        self.delay_buffer = np.zeros(max_delay_samples)
        self.buffer_index = 0
    
    def process(self, input_signal):
        """
        コーラスエフェクトを適用
        
        Args:
            input_signal (np.ndarray): 入力信号
            
        Returns:
            np.ndarray: コーラスが適用された信号
        """
        output = np.zeros_like(input_signal)
        
        for n, x_n in enumerate(input_signal):
            # バッファに現在のサンプルを書き込み
            self.delay_buffer[self.buffer_index] = x_n
            
            # モジュレーションを計算
            lfo = np.sin(2 * np.pi * self.phase)
            delay_time = self.depth * (1 + lfo)
            delay_samples = delay_time * self.config.sample_rate
            
            # 遅延したサンプルを取得（線形補間）
            delay_index = (self.buffer_index - int(delay_samples)) % len(self.delay_buffer)
            delayed_sample = self.delay_buffer[delay_index]
            
            # 出力を計算
            output[n] = self.dry_level * x_n + self.wet_level * delayed_sample
            
            # インデックスとフェーズを更新
            self.buffer_index = (self.buffer_index + 1) % len(self.delay_buffer)
            self.phase += self.rate / self.config.sample_rate
            if self.phase >= 1.0:
                self.phase -= 1.0
        
        return output

    def apply(self, input_signal, sample_rate=None):
        """
        コーラスエフェクトを適用（教育用便利メソッド）
        
        Args:
            input_signal (np.ndarray): 入力信号
            sample_rate (int): サンプリングレート（未使用、互換性のため）
            
        Returns:
            np.ndarray: コーラスが適用された信号
        """
        return self.process(input_signal)

class Compressor:
    """コンプレッサー"""
    
    def __init__(self, threshold=0.7, ratio=4.0, attack=0.01, release=0.1, config=None):
        """
        コンプレッサーを初期化
        
        Args:
            threshold (float): 閾値 (0.0-1.0)
            ratio (float): 圧縮比
            attack (float): アタック時間 (秒)
            release (float): リリース時間 (秒)
            config (AudioConfig): オーディオ設定
        """
        self.config = config or AudioConfig()
        self.threshold = threshold
        self.ratio = ratio
        self.attack = attack
        self.release = release
        
        # エンベロープフォロワー用の状態
        self.envelope = 0.0
        
        # 時定数の計算
        self.attack_coeff = np.exp(-1.0 / (attack * self.config.sample_rate))
        self.release_coeff = np.exp(-1.0 / (release * self.config.sample_rate))
    
    def process(self, input_signal):
        """
        コンプレッサーを適用
        
        Args:
            input_signal (np.ndarray): 入力信号
            
        Returns:
            np.ndarray: 圧縮された信号
        """
        output = np.zeros_like(input_signal)
        
        for n, x_n in enumerate(input_signal):
            # 現在のレベルを計算
            current_level = abs(x_n)
            
            # エンベロープフォロワー
            if current_level > self.envelope:
                self.envelope += (current_level - self.envelope) * (1 - self.attack_coeff)
            else:
                self.envelope += (current_level - self.envelope) * (1 - self.release_coeff)
            
            # ゲインリダクションを計算
            if self.envelope > self.threshold:
                excess = self.envelope - self.threshold
                gain_reduction = 1.0 - (excess / self.ratio) / self.envelope
            else:
                gain_reduction = 1.0
            
            # 出力を計算
            output[n] = x_n * gain_reduction
        
        return output

    def apply(self, input_signal, sample_rate=None):
        """
        コンプレッサーを適用（教育用便利メソッド）
        
        Args:
            input_signal (np.ndarray): 入力信号
            sample_rate (int): サンプリングレート（未使用、互換性のため）
            
        Returns:
            np.ndarray: 圧縮された信号
        """
        return self.process(input_signal)

# 便利関数
def apply_compression(signal, threshold=0.7, ratio=4.0, attack=0.01, release=0.1, config=None):
    """
    コンプレッサーを信号に適用する便利関数
    
    Args:
        signal (np.ndarray): 入力信号
        threshold (float): 閾値 (0.0-1.0)
        ratio (float): 圧縮比
        attack (float): アタック時間 (秒)
        release (float): リリース時間 (秒)
        config (AudioConfig): オーディオ設定
        
    Returns:
        np.ndarray: 圧縮された信号
    """
    compressor = Compressor(threshold, ratio, attack, release, config)
    return compressor.process(signal)
