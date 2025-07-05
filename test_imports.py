#!/usr/bin/env python3
"""
audio_libのインポートテスト
"""

try:
    from audio_lib import Note, Track, BasicPiano
    print("✅ 全てのクラスのimportに成功しました")
    
    # Noteクラスのテスト
    note1 = Note(60, 100, 0.0, 1.0)
    print(f"✅ Note作成成功: {note1}")
    
    # Trackクラスのテスト
    track = Track(name="Test Track")
    print(f"✅ Track作成成功: {track.name}")
    
    # BasicPianoクラスのテスト
    piano = BasicPiano()
    print(f"✅ BasicPiano作成成功: {type(piano)}")
    
except ImportError as e:
    print(f"❌ importエラー: {e}")
except Exception as e:
    print(f"❌ 実行エラー: {e}")
