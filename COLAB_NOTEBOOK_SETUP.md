# Colab用セットアップセル - 全ノートブック共通
# このセルを各ノートブックの最初に追加

## セットアップセル（全ノートブック共通）

```python
# Google Colab環境の確認とセットアップ
import sys

# Colab環境かどうかを確認
IN_COLAB = 'google.colab' in sys.modules

if IN_COLAB:
    print("🔧 Google Colab環境を設定中...")
    
    # 必要なパッケージをインストール
    !pip install numpy scipy matplotlib ipython
    
    # GitHubからライブラリをクローン
    !git clone https://github.com/ggszk/simple-audio-programming.git
    
    # パスを追加
    sys.path.append('/content/simple-audio-programming')
    
    print("✅ セットアップ完了！")
    print("📝 このノートブックを自分用にコピーするには:")
    print("   ファイル → ドライブにコピーを保存")
    
else:
    print("🏠 ローカル環境で実行中")
    print("📝 audio_libがインストールされていることを確認してください")

# 共通インポート
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Audio, display
import warnings
warnings.filterwarnings('ignore')

print("\n🎵 Simple Audio Programming へようこそ！")
```

## 音声再生用ヘルパー関数

```python
def play_sound(signal, sample_rate=44100, title="Audio"):
    """
    Colab/Jupyter環境で音声を再生するヘルパー関数
    
    Args:
        signal: 音声信号（numpy array）
        sample_rate: サンプリングレート
        title: 表示用タイトル
    """
    # 信号を正規化（クリッピング防止）
    if np.max(np.abs(signal)) > 0:
        signal = signal / np.max(np.abs(signal)) * 0.8
    
    print(f"🔊 {title}")
    display(Audio(signal, rate=sample_rate))
    
def plot_waveform(signal, sample_rate=44100, title="Waveform", max_points=1000):
    """
    波形をプロットするヘルパー関数
    
    Args:
        signal: 音声信号
        sample_rate: サンプリングレート  
        title: グラフタイトル
        max_points: 表示する最大点数（パフォーマンス用）
    """
    # 長い信号の場合はダウンサンプリング
    if len(signal) > max_points:
        step = len(signal) // max_points
        signal_plot = signal[::step]
        time_plot = np.arange(0, len(signal_plot)) * step / sample_rate
    else:
        signal_plot = signal
        time_plot = np.arange(len(signal)) / sample_rate
    
    plt.figure(figsize=(12, 4))
    plt.plot(time_plot, signal_plot)
    plt.title(title)
    plt.xlabel('時間 (秒)')
    plt.ylabel('振幅')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

print("🛠️ ヘルパー関数が読み込まれました")
```

## 学習進捗確認

```python
# このセルは各レッスンで更新
lesson_number = 1  # 各ノートブックで変更
lesson_title = "基礎とサイン波"  # 各ノートブックで変更

print(f"📚 Lesson {lesson_number:02d}: {lesson_title}")
print("=" * 50)
print()
print("🎯 学習目標:")
print("- サイン波の生成方法を理解する")
print("- 周波数と音程の関係を学ぶ") 
print("- Pythonでの音響プログラミング基礎を身につける")
print()
print("⏱️ 推定学習時間: 30-45分")
print()
print("📋 準備完了チェックリスト:")
print("☑️ セットアップセルが正常に実行された")
print("☐ 音声再生テストが成功した")
print("☐ 波形表示テストが成功した")
```

## 音声再生テスト

```python
# 音声再生のテスト
print("🧪 音声再生テスト")

# 簡単なテスト音を生成
test_freq = 440  # A4
test_duration = 1.0
test_sample_rate = 44100

# サイン波生成
t = np.linspace(0, test_duration, int(test_sample_rate * test_duration), False)
test_signal = 0.3 * np.sin(2 * np.pi * test_freq * t)

# 再生テスト
play_sound(test_signal, test_sample_rate, f"{test_freq}Hz テスト音")

# 波形表示テスト  
plot_waveform(test_signal[:1000], test_sample_rate, "テスト音波形（最初の1000サンプル）")

print("✅ 音声と波形が正常に表示されれば準備完了です！")
```
