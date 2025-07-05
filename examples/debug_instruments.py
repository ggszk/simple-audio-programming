#!/usr/bin/env python3
"""
デバッグ用: 楽器とシーケンサーのテスト

Piano, Guitar, Drum, Sequencerの動作確認とデバッグ
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from audio_lib import AudioConfig, save_audio
from audio_lib.synthesis import note_name_to_number, note_to_frequency
from audio_lib.instruments import Piano, Guitar, Drum
from audio_lib.sequencer import Sequencer

def debug_piano():
    """Pianoインストゥルメントのデバッグ"""
    print("🔍 Pianoインストゥルメントのデバッグ開始...")
    
    config = AudioConfig(sample_rate=44100)
    piano = Piano(config)
    
    try:
        # C4の音を2秒間生成
        note = "C4"
        midi_number = note_name_to_number(note)
        duration = 2.0
        
        signal = piano.play_note(midi_number, duration)
        
        print(f"✅ Piano音生成成功: {note} (MIDI: {midi_number})")
        print(f"   長さ: {duration}秒")
        print(f"   サンプル数: {len(signal)}")
        print(f"   最大振幅: {np.max(np.abs(signal)):.3f}")
        
        save_audio("debug_piano_c4.wav", config.sample_rate, signal)
        print("✅ ファイル保存成功: debug_piano_c4.wav")
        
        return signal
        
    except Exception as e:
        print(f"❌ Pianoエラー: {e}")
        return None

def debug_guitar():
    """Guitarインストゥルメントのデバッグ"""
    print("\n🔍 Guitarインストゥルメントのデバッグ開始...")
    
    config = AudioConfig(sample_rate=44100)
    guitar = Guitar(config)
    
    try:
        # E2の音を2秒間生成（ギターの低いE弦）
        note = "E2"
        midi_number = note_name_to_number(note)
        duration = 2.0
        
        signal = guitar.play_note(midi_number, duration)
        
        print(f"✅ Guitar音生成成功: {note} (MIDI: {midi_number})")
        print(f"   長さ: {duration}秒")
        print(f"   サンプル数: {len(signal)}")
        print(f"   最大振幅: {np.max(np.abs(signal)):.3f}")
        
        save_audio("debug_guitar_e2.wav", config.sample_rate, signal)
        print("✅ ファイル保存成功: debug_guitar_e2.wav")
        
        return signal
        
    except Exception as e:
        print(f"❌ Guitarエラー: {e}")
        return None

def debug_drum():
    """Drumインストゥルメントのデバッグ"""
    print("\n🔍 Drumインストゥルメントのデバッグ開始...")
    
    config = AudioConfig(sample_rate=44100)
    drum = Drum(config)
    
    try:
        # キック、スネア、ハイハットをテスト
        drum_sounds = {
            "kick": 36,     # MIDI番号36はキックドラム
            "snare": 38,    # MIDI番号38はスネアドラム
            "hihat": 42     # MIDI番号42はクローズドハイハット
        }
        
        duration = 1.0
        
        for drum_name, midi_number in drum_sounds.items():
            signal = drum.play_note(midi_number, duration)
            
            print(f"✅ Drum音生成成功: {drum_name} (MIDI: {midi_number})")
            print(f"   長さ: {duration}秒")
            print(f"   サンプル数: {len(signal)}")
            print(f"   最大振幅: {np.max(np.abs(signal)):.3f}")
            
            filename = f"debug_drum_{drum_name}.wav"
            save_audio(filename, config.sample_rate, signal)
            print(f"✅ ファイル保存成功: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Drumエラー: {e}")
        return False

def debug_sequencer():
    """Sequencerのデバッグ"""
    print("\n🔍 Sequencerのデバッグ開始...")
    
    config = AudioConfig(sample_rate=44100)
    sequencer = Sequencer(config)
    
    try:
        # 楽器を追加
        piano = Piano(config)
        drum = Drum(config)
        
        sequencer.add_instrument("piano", piano)
        sequencer.add_instrument("drums", drum)
        
        print("✅ 楽器の追加成功: piano, drums")
        
        # 簡単なシーケンスを作成
        # ピアノでCメジャーコード
        piano_notes = [
            (0.0, "piano", "C4", 1.0),   # 0秒にC4を1秒
            (0.0, "piano", "E4", 1.0),   # 0秒にE4を1秒
            (0.0, "piano", "G4", 1.0),   # 0秒にG4を1秒
            (1.0, "piano", "F4", 1.0),   # 1秒にF4を1秒
            (1.0, "piano", "A4", 1.0),   # 1秒にA4を1秒
            (1.0, "piano", "C5", 1.0),   # 1秒にC5を1秒
        ]
        
        # ドラムパターン
        drum_notes = [
            (0.0, "drums", 36, 0.1),     # キック
            (0.5, "drums", 38, 0.1),     # スネア
            (1.0, "drums", 36, 0.1),     # キック
            (1.5, "drums", 38, 0.1),     # スネア
        ]
        
        # ノートを追加
        for time, instrument, note, duration in piano_notes + drum_notes:
            if isinstance(note, str):
                midi_number = note_name_to_number(note)
            else:
                midi_number = note
            
            sequencer.add_note(time, instrument, midi_number, duration)
        
        print("✅ ノートの追加成功")
        
        # シーケンスを再生（ミックス）
        sequence_length = 2.0
        mixed_audio = sequencer.render(sequence_length)
        
        print(f"✅ シーケンス生成成功")
        print(f"   長さ: {sequence_length}秒")
        print(f"   サンプル数: {len(mixed_audio)}")
        print(f"   最大振幅: {np.max(np.abs(mixed_audio)):.3f}")
        
        save_audio("debug_sequencer_demo.wav", config.sample_rate, mixed_audio)
        print("✅ ファイル保存成功: debug_sequencer_demo.wav")
        
        return mixed_audio
        
    except Exception as e:
        print(f"❌ Sequencerエラー: {e}")
        return None

def debug_note_utilities():
    """ノートユーティリティ関数のデバッグ"""
    print("\n🔍 ノートユーティリティのデバッグ開始...")
    
    try:
        # いくつかの音名をテスト
        test_notes = ["C4", "D#4", "F#5", "Bb3", "A4"]
        
        print("音名 -> MIDI番号 -> 周波数の変換テスト:")
        print("音名\tMIDI番号\t周波数(Hz)")
        print("-" * 30)
        
        for note in test_notes:
            midi_number = note_name_to_number(note)
            frequency = note_to_frequency(midi_number)
            print(f"{note}\t{midi_number}\t{frequency:.2f}")
        
        print("✅ ノートユーティリティテスト成功")
        return True
        
    except Exception as e:
        print(f"❌ ノートユーティリティエラー: {e}")
        return False

if __name__ == "__main__":
    print("🔧 楽器・シーケンサーデバッグスクリプト実行中...")
    print("=" * 50)
    
    # ノートユーティリティテスト
    debug_note_utilities()
    
    # 各楽器テスト
    piano_signal = debug_piano()
    guitar_signal = debug_guitar()
    drum_success = debug_drum()
    
    # シーケンサーテスト
    sequence_signal = debug_sequencer()
    
    print("\n🎉 楽器・シーケンサーデバッグ完了！生成されたファイルを確認してください。")
