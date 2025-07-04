#!/usr/bin/env python3
"""
pytest実行用スクリプト

このスクリプトは音響プログラミング教育ライブラリのテストを
簡単に実行するためのものです。
"""

import sys
import subprocess
import argparse


def run_tests(test_type="all", verbose=True):
    """テストを実行する"""
    
    base_cmd = ["python", "-m", "pytest"]
    
    if verbose:
        base_cmd.extend(["-v", "-s"])
    
    if test_type == "all":
        print("🧪 全テストを実行します...")
        cmd = base_cmd + ["tests/"]
        
    elif test_type == "comprehensive":
        print("🔍 包括的テストを実行します...")
        cmd = base_cmd + ["tests/test_audio_lib_comprehensive.py"]
        
    elif test_type == "notebook":
        print("📓 ノートブック関連テストを実行します...")
        cmd = base_cmd + ["tests/test_notebook_scenarios.py"]
        
    elif test_type == "oscillators":
        print("🌊 オシレーターテストを実行します...")
        cmd = base_cmd + ["tests/test_oscillators.py"]
        
    elif test_type == "lesson1":
        print("📚 Lesson 1関連テストを実行します...")
        cmd = base_cmd + ["tests/test_notebook_scenarios.py::TestLesson01BasicsAndSineWaves"]
        
    elif test_type == "lesson2":
        print("📚 Lesson 2関連テストを実行します...")
        cmd = base_cmd + ["tests/test_notebook_scenarios.py::TestLesson02EnvelopesAndADSR"]
        
    elif test_type == "integration":
        print("🔗 統合テストを実行します...")
        cmd = base_cmd + ["-k", "integration", "tests/"]
        
    elif test_type == "quick":
        print("⚡ クイックテストを実行します...")
        cmd = base_cmd + ["--tb=line", "-x", "tests/test_audio_lib_comprehensive.py::TestAudioConfig"]
        
    else:
        print(f"❌ 不明なテストタイプ: {test_type}")
        return False
    
    print(f"実行コマンド: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n⚠️  テスト実行が中断されました")
        return False
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="audio_lib テスト実行スクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
利用可能なテストタイプ:
  all           - 全テスト実行 (デフォルト)
  comprehensive - 包括的機能テスト
  notebook      - ノートブック関連テスト
  oscillators   - オシレーターテスト
  lesson1       - Lesson 1関連テスト
  lesson2       - Lesson 2関連テスト  
  integration   - 統合テスト
  quick         - クイックテスト

使用例:
  python run_tests.py                    # 全テスト実行
  python run_tests.py comprehensive     # 包括的テスト
  python run_tests.py lesson1           # Lesson 1テスト
  python run_tests.py --quiet notebook  # ノートブックテスト（簡潔出力）
        """
    )
    
    parser.add_argument(
        "test_type", 
        nargs="?", 
        default="all",
        help="実行するテストの種類"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="簡潔な出力"
    )
    
    args = parser.parse_args()
    
    print("🎵 Simple Audio Programming Library - テスト実行")
    print("=" * 60)
    
    success = run_tests(args.test_type, verbose=not args.quiet)
    
    if success:
        print("\n✅ テスト完了!")
        sys.exit(0)
    else:
        print("\n❌ テストに失敗しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
