"""
音楽シーケンサー

複数の楽器と音符を組み合わせて楽曲を作成
"""

import numpy as np
from .core.audio_config import AudioConfig
from .core.wave_io import WaveFileIO
from .synthesis.note_utils import note_name_to_number

class Note:
    """音符を表すクラス"""
    
    def __init__(self, note_number=60, velocity=100, start_time=0.0, duration=1.0):
        """
        音符を初期化
        
        Args:
            note_number (int or str): MIDIノート番号または音名
            velocity (int): ベロシティ (0-127)
            start_time (float): 開始時間 (秒)
            duration (float): 音符の長さ (秒)
        """
        if isinstance(note_number, str):
            self.note_number = note_name_to_number(note_number)
        else:
            self.note_number = note_number
            
        self.velocity = velocity
        self.start_time = start_time
        self.duration = duration
    
    def get_frequency(self):
        """ノートの周波数を取得"""
        from .synthesis.note_utils import note_to_frequency
        return note_to_frequency(self.note_number)
    
    def __repr__(self):
        return f"Note(note={self.note_number}, vel={self.velocity}, start={self.start_time}, dur={self.duration})"

class Track:
    """楽器トラッククラス"""
    
    def __init__(self, name="Track", instrument=None):
        """
        トラックを初期化
        
        Args:
            name (str): トラック名
            instrument: 楽器インスタンス（後で設定可能）
        """
        self.name = name
        self.instrument = instrument
        self.notes = []
        self.volume = 1.0
        self.pan = 0.0  # -1.0 (左) to 1.0 (右)
    
    def add_note(self, note_number, velocity=100, start_time=0.0, duration=1.0):
        """
        音符を追加
        
        Args:
            note_number (int or str): MIDIノート番号または音名
            velocity (int): ベロシティ
            start_time (float): 開始時間 (秒)
            duration (float): 音符の長さ (秒)
        """
        note = Note(note_number, velocity, start_time, duration)
        self.notes.append(note)
        return note
    
    def add_note_instance(self, note):
        """
        Noteインスタンスを直接追加
        
        Args:
            note (Note): Noteインスタンス
        """
        self.notes.append(note)
        return note
    
    def add_notes(self, note_sequence):
        """
        複数の音符を一度に追加
        
        Args:
            note_sequence (list): 音符のリスト [(note, velocity, start, duration), ...]
        """
        for note_data in note_sequence:
            if len(note_data) == 4:
                self.add_note(*note_data)
            elif len(note_data) == 3:
                note, start, duration = note_data
                self.add_note(note, 100, start, duration)
            elif len(note_data) == 2:
                note, duration = note_data
                start_time = max([n.start_time + n.duration for n in self.notes] + [0])
                self.add_note(note, 100, start_time, duration)
    
    def clear(self):
        """全ての音符をクリア"""
        self.notes = []
    
    def get_total_duration(self):
        """トラックの総演奏時間を取得"""
        if not self.notes:
            return 0.0
        return max(note.start_time + note.duration for note in self.notes)
    
    def render(self, total_duration=None, config=None):
        """
        トラックを音声データとしてレンダリング
        
        Args:
            total_duration (float): 総時間。Noneの場合は自動計算
            config (AudioConfig): オーディオ設定
            
        Returns:
            np.ndarray: レンダリングされた音声データ
        """
        if config is None:
            config = AudioConfig()
        
        if total_duration is None:
            total_duration = self.get_total_duration()
        
        if total_duration <= 0:
            return np.array([])
        
        # 出力バッファを初期化
        total_samples = config.duration_to_samples(total_duration)
        output = np.zeros(total_samples)
        
        # 各音符をレンダリング
        for note in self.notes:
            # 音符の音声を生成
            note_audio = self.instrument.play_note(
                note.note_number, note.velocity, note.duration
            )
            
            # 開始位置を計算
            start_sample = config.duration_to_samples(note.start_time)
            end_sample = start_sample + len(note_audio)
            
            # 出力バッファに追加
            if start_sample < total_samples:
                actual_end = min(end_sample, total_samples)
                audio_end = actual_end - start_sample
                output[start_sample:actual_end] += note_audio[:audio_end] * self.volume
        
        return output

    def set_instrument(self, instrument):
        """
        楽器を設定
        
        Args:
            instrument: 楽器インスタンス
        """
        self.instrument = instrument

class Sequencer:
    """音楽シーケンサー"""
    
    def __init__(self, config=None):
        """
        シーケンサーを初期化
        
        Args:
            config (AudioConfig): オーディオ設定
        """
        self.config = config or AudioConfig()
        self.tracks = {}  # name -> Track の辞書
        self.tempo = 120  # BPM
        self.master_volume = 1.0
    
    def add_track(self, track):
        """
        トラックを追加
        
        Args:
            track (Track): Trackインスタンス
        """
        self.tracks[track.name] = track
    
    def set_instrument(self, track_name, instrument):
        """
        指定されたトラックに楽器を設定
        
        Args:
            track_name (str): トラック名
            instrument: 楽器インスタンス
        """
        if track_name in self.tracks:
            self.tracks[track_name].set_instrument(instrument)
        else:
            raise ValueError(f"トラック '{track_name}' が見つかりません")
    
    def remove_track(self, track_name):
        """
        トラックを削除
        
        Args:
            track_name (str): トラック名
        """
        if track_name in self.tracks:
            del self.tracks[track_name]
    
    def clear_all_tracks(self):
        """全てのトラックをクリア"""
        self.tracks = {}
    
    def get_total_duration(self):
        """全トラックの総演奏時間を取得"""
        if not self.tracks:
            return 0.0
        return max(track.get_total_duration() for track in self.tracks.values())
    
    def render(self, duration=None, output_filename=None):
        """
        全トラックをレンダリングしてミックス
        
        Args:
            duration (float): レンダリング時間（秒）。Noneの場合は自動計算
            output_filename (str): 出力ファイル名。Noneの場合はファイル保存しない
            
        Returns:
            np.ndarray: ミックスされた音声データ
        """
        total_duration = duration or self.get_total_duration()
        
        if total_duration <= 0:
            return np.array([])
        
        # 各トラックをレンダリング
        track_audio = []
        for track in self.tracks.values():
            if track.instrument is not None:  # 楽器が設定されている場合のみ
                audio = track.render(total_duration, self.config)
                track_audio.append(audio)
        
        # 全トラックをミックス
        if track_audio:
            # 全て同じ長さにする
            max_length = max(len(audio) for audio in track_audio)
            padded_audio = []
            for audio in track_audio:
                if len(audio) < max_length:
                    padded = np.zeros(max_length)
                    padded[:len(audio)] = audio
                    padded_audio.append(padded)
                else:
                    padded_audio.append(audio)
            
            mixed_audio = sum(padded_audio)
        else:
            mixed_audio = np.zeros(self.config.duration_to_samples(total_duration))
        
        # マスターボリュームを適用
        mixed_audio *= self.master_volume
        
        # クリッピング防止
        if np.max(np.abs(mixed_audio)) > 0:
            mixed_audio = mixed_audio / np.max(np.abs(mixed_audio)) * 0.95
        
        # ファイル保存
        if output_filename:
            WaveFileIO.save_mono(output_filename, self.config.sample_rate, mixed_audio)
        
        return mixed_audio
    
    def beats_to_seconds(self, beats):
        """
        拍数を秒数に変換
        
        Args:
            beats (float): 拍数
            
        Returns:
            float: 秒数
        """
        return beats * 60.0 / self.tempo
    
    def seconds_to_beats(self, seconds):
        """
        秒数を拍数に変換
        
        Args:
            seconds (float): 秒数
            
        Returns:
            float: 拍数
        """
        return seconds * self.tempo / 60.0

def create_simple_melody(track, notes, note_duration=0.5, start_time=0.0):
    """
    シンプルなメロディーをトラックに追加するヘルパー関数
    
    Args:
        track (Track): 対象トラック
        notes (list): 音符のリスト（音名またはMIDIノート番号）
        note_duration (float): 各音符の長さ
        start_time (float): 開始時間
    """
    current_time = start_time
    for note in notes:
        if note is not None:  # None は休符
            track.add_note(note, 100, current_time, note_duration)
        current_time += note_duration

def create_chord(track, chord_notes, start_time=0.0, duration=1.0, velocity=100):
    """
    和音をトラックに追加するヘルパー関数
    
    Args:
        track (Track): 対象トラック
        chord_notes (list): 和音の構成音
        start_time (float): 開始時間
        duration (float): 和音の長さ
        velocity (int): ベロシティ
    """
    for note in chord_notes:
        track.add_note(note, velocity, start_time, duration)
