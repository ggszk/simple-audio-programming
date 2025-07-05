#!/usr/bin/env python3
"""
デバッグ用: メイン実行スクリプト

全てのデバッグスクリプトを順番に実行して、ライブラリの動作を確認
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback
from examples.debug_oscillators import debug_sine_wave, debug_sawtooth_wave, debug_square_wave, compare_waveforms
from examples.debug_envelopes import debug_adsr_envelope, debug_linear_envelope, debug_envelope_application, visualize_envelopes
from examples.debug_instruments import debug_piano, debug_guitar, debug_drum, debug_sequencer, debug_note_utilities

def run_all_tests():
    """全てのデバッグテストを実行"""
    print("🔧 Simple Audio Programming ライブラリ全体デバッグ")
    print("=" * 60)
    
    test_results = {}
    
    # 1. オシレーターテスト
    print("\n1️⃣  オシレーターテスト")
    print("-" * 30)
    try:
        sine_result = debug_sine_wave()
        saw_result = debug_sawtooth_wave()
        square_result = debug_square_wave()
        
        if sine_result is not None and saw_result is not None and square_result is not None:
            compare_waveforms()
            test_results["oscillators"] = "✅ 成功"
        else:
            test_results["oscillators"] = "❌ 一部失敗"
    except Exception as e:
        test_results["oscillators"] = f"❌ エラー: {str(e)}"
        print(f"❌ オシレーターテストエラー: {e}")
        traceback.print_exc()
    
    # 2. エンベロープテスト
    print("\n2️⃣  エンベロープテスト")
    print("-" * 30)
    try:
        adsr_result = debug_adsr_envelope()
        linear_result = debug_linear_envelope()
        original, enveloped = debug_envelope_application()
        
        if adsr_result is not None and linear_result is not None and enveloped is not None:
            visualize_envelopes()
            test_results["envelopes"] = "✅ 成功"
        else:
            test_results["envelopes"] = "❌ 一部失敗"
    except Exception as e:
        test_results["envelopes"] = f"❌ エラー: {str(e)}"
        print(f"❌ エンベロープテストエラー: {e}")
        traceback.print_exc()
    
    # 3. ノートユーティリティテスト
    print("\n3️⃣  ノートユーティリティテスト")
    print("-" * 30)
    try:
        note_result = debug_note_utilities()
        test_results["note_utils"] = "✅ 成功" if note_result else "❌ 失敗"
    except Exception as e:
        test_results["note_utils"] = f"❌ エラー: {str(e)}"
        print(f"❌ ノートユーティリティテストエラー: {e}")
        traceback.print_exc()
    
    # 4. 楽器テスト
    print("\n4️⃣  楽器テスト")
    print("-" * 30)
    try:
        piano_result = debug_piano()
        guitar_result = debug_guitar()
        drum_result = debug_drum()
        
        if piano_result is not None and guitar_result is not None and drum_result:
            test_results["instruments"] = "✅ 成功"
        else:
            test_results["instruments"] = "❌ 一部失敗"
    except Exception as e:
        test_results["instruments"] = f"❌ エラー: {str(e)}"
        print(f"❌ 楽器テストエラー: {e}")
        traceback.print_exc()
    
    # 5. シーケンサーテスト
    print("\n5️⃣  シーケンサーテスト")
    print("-" * 30)
    try:
        sequencer_result = debug_sequencer()
        test_results["sequencer"] = "✅ 成功" if sequencer_result is not None else "❌ 失敗"
    except Exception as e:
        test_results["sequencer"] = f"❌ エラー: {str(e)}"
        print(f"❌ シーケンサーテストエラー: {e}")
        traceback.print_exc()
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("🏁 デバッグ結果サマリー")
    print("=" * 60)
    
    for test_name, result in test_results.items():
        print(f"{test_name:15} : {result}")
    
    # 成功/失敗の統計
    success_count = sum(1 for result in test_results.values() if result.startswith("✅"))
    total_count = len(test_results)
    
    print(f"\n📊 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 全てのテストが成功しました！")
    else:
        print("⚠️  一部のテストが失敗しました。詳細は上記ログを確認してください。")
    
    print("\n📁 生成されたファイル:")
    generated_files = [
        "debug_sine_440hz.wav",
        "debug_sawtooth_440hz.wav", 
        "debug_square_440hz.wav",
        "debug_waveforms_comparison.png",
        "debug_sine_no_envelope.wav",
        "debug_sine_with_adsr.wav",
        "debug_envelopes_comparison.png",
        "debug_piano_c4.wav",
        "debug_guitar_e2.wav",
        "debug_drum_kick.wav",
        "debug_drum_snare.wav",
        "debug_drum_hihat.wav",
        "debug_sequencer_demo.wav"
    ]
    
    for filename in generated_files:
        if os.path.exists(filename):
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} (未生成)")

if __name__ == "__main__":
    run_all_tests()
