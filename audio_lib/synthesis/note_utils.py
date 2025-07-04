"""
音程と周波数の変換ユーティリティ

MIDIノート番号と周波数の相互変換、音名の処理など
"""

import numpy as np

def note_to_frequency(note_number):
    """
    MIDIノート番号を周波数(Hz)に変換
    
    Args:
        note_number (int): MIDIノート番号 (0-127, 60=中央のC)
        
    Returns:
        float: 周波数 (Hz)
    """
    # A4 (ラ音, ノート番号69) = 440Hz を基準とする
    return 440.0 * (2.0 ** ((note_number - 69) / 12.0))

def frequency_to_note(frequency):
    """
    周波数(Hz)をMIDIノート番号に変換
    
    Args:
        frequency (float): 周波数 (Hz)
        
    Returns:
        int: MIDIノート番号
    """
    return int(12 * np.log2(frequency / 440.0) + 69 + 0.5)

def note_name_to_number(note_name):
    """
    音名をMIDIノート番号に変換
    
    Args:
        note_name (str): 音名 (例: "C4", "A#3", "Bb5")
        
    Returns:
        int: MIDIノート番号
    """
    note_mapping = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }
    
    # 音名と オクターブ番号を分離
    if len(note_name) >= 2 and note_name[-1].isdigit():
        octave = int(note_name[-1])
        note = note_name[:-1]
    else:
        raise ValueError(f"無効な音名形式: {note_name}")
    
    if note not in note_mapping:
        raise ValueError(f"未知の音名: {note}")
    
    # MIDIノート番号 = オクターブ * 12 + 音程番号
    # 中央C (C4) = ノート番号60
    return (octave + 1) * 12 + note_mapping[note]

def number_to_note_name(note_number):
    """
    MIDIノート番号を音名に変換
    
    Args:
        note_number (int): MIDIノート番号
        
    Returns:
        str: 音名 (例: "C4", "A#3")
    """
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                  'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    octave = (note_number // 12) - 1
    note_index = note_number % 12
    
    return f"{note_names[note_index]}{octave}"

def create_scale(root_note, scale_type='major'):
    """
    指定したルート音からスケールを生成
    
    Args:
        root_note (int or str): ルート音 (MIDIノート番号または音名)
        scale_type (str): スケールタイプ ('major', 'minor', 'pentatonic')
        
    Returns:
        list: スケールのMIDIノート番号リスト
    """
    if isinstance(root_note, str):
        root_note = note_name_to_number(root_note)
    
    scale_intervals = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'pentatonic': [0, 2, 4, 7, 9],
        'blues': [0, 3, 5, 6, 7, 10]
    }
    
    if scale_type not in scale_intervals:
        raise ValueError(f"未知のスケールタイプ: {scale_type}")
    
    intervals = scale_intervals[scale_type]
    return [root_note + interval for interval in intervals]
