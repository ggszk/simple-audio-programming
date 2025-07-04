# Simple Audio Programming
## シンプル音響プログラミング教育ライブラリ

[![CI](https://github.com/ggszk/simple-audio-programming/workflows/CI/badge.svg)](https://github.com/ggszk/simple-audio-programming/actions)
[![Python Version](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fggszk%2Fsimple-audio-programming%2Fmain%2Fpyproject.toml)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

音響プログラミング初心者のための教育的Pythonライブラリです。理解しやすいコードと段階的な学習アプローチで、デジタル信号処理と音響合成の基礎を学べます。

## 🎯 設計哲学

### **「理解できるブラックボックス」の排除**
既存の音楽ライブラリは高機能ですが、多くが「ブラックボックス」です。このライブラリでは：

- **全ての処理が追跡可能**: 学生がコードを読んで理解できる
- **数式とコードの一致**: 音響理論の式がそのままPythonコードに
- **段階的な複雑性**: 基本から応用まで自然な学習曲線

### **教育効果を最大化する設計**
- 実用性を保ちながら教育価値を優先
- ソースコードそのものが教材
- 理論と実装を橋渡し

## 主な特徴

### 1. **教育的な設計**
- 機能別にモジュールを分離
- 明確な命名規則
- 適切なクラス設計

### 2. **理解しやすさ重視**
- 日本語コメントの充実
- わかりやすい関数名・変数名
- 型ヒントの追加

### 3. **段階的学習支援**
- 基礎から応用まで段階的な学習が可能
- 理論的背景の説明
- 実用的な使用例

## ディレクトリ構造

```
simple-audio-programming/    # プロジェクト全体
├── README.md                    # このファイル
├── audio_lib/                   # メインライブラリ
│   ├── __init__.py             # メインモジュール
│   ├── core/                   # 基本機能
│   │   ├── audio_config.py     # オーディオ設定
│   │   └── wave_io.py          # WAVファイル入出力
│   ├── synthesis/              # 音響合成
│   │   ├── oscillators.py      # オシレーター（波形生成）
│   │   ├── envelopes.py        # エンベロープ（音量変化）
│   │   └── note_utils.py       # 音程・周波数変換
│   ├── effects/                # エフェクト
│   │   ├── filters.py          # フィルター
│   │   └── audio_effects.py    # リバーブ、ディストーション等
│   ├── instruments/            # 楽器クラス
│   │   └── basic_instruments.py # ピアノ、ギター、ドラム等
│   └── sequencer.py            # 楽曲制作用シーケンサー
└── examples/                   # 使用例とチュートリアル
    ├── basic_examples.py       # 基本的な使用例
    └── educational_tutorial.py # 教育用チュートリアル
```

## 主な機能

### 基本的な音響合成
```python
from audio_lib import SineWave, ADSREnvelope, save_audio

# サイン波生成
sine = SineWave()
signal = sine.generate(frequency=440, duration=1.0)

# エンベロープ適用
adsr = ADSREnvelope(attack=0.1, decay=0.2, sustain=0.7, release=0.3)
envelope = adsr.generate(duration=1.0)
signal_with_envelope = signal * envelope

# ファイル保存
save_audio("output.wav", 44100, signal_with_envelope)
```

### 楽器クラスの使用
```python
from audio_lib.instruments import Piano
from audio_lib.synthesis import note_name_to_number

piano = Piano()
note_number = note_name_to_number("C4")  # 中央のC
sound = piano.play_note(note_number, velocity=100, duration=2.0)
```

### シーケンサーで楽曲制作
```python
from audio_lib.sequencer import Sequencer
from audio_lib.instruments import Piano, Guitar, Drum

sequencer = Sequencer()
piano_track = sequencer.add_track(Piano(), "Piano")
guitar_track = sequencer.add_track(Guitar(), "Guitar")

# 音符を追加
piano_track.add_note("C4", velocity=100, start_time=0.0, duration=1.0)
guitar_track.add_note("E4", velocity=90, start_time=1.0, duration=0.5)

# レンダリング
sequencer.render("my_song.wav")
```

## 使用方法

### 1. チュートリアルから始める
```bash
cd simple-audio-programming/examples
python educational_tutorial.py
```

### 2. 基本例を試す
```bash
cd simple-audio-programming/examples
python basic_examples.py
```

### 3. 独自の楽曲を作成
ライブラリを使って自由に楽曲を作成できます。

## 教育的な利点

1. **段階的学習**: 基本概念から応用まで順序立てて学習
2. **理論と実践**: 音響理論と実装の両方を学習
3. **モジュラー設計**: 各機能を独立して理解・使用可能
4. **実用性**: 実際の楽曲制作に使用可能

## 既存ライブラリとの比較と教育的優位性

### 🎼 一般的な音楽ライブラリとの位置づけ

| 観点 | 既存ライブラリ | このライブラリ |
|------|----------------|----------------|
| **対象ユーザー** | プロ・上級者 | 初学者・教育 |
| **学習曲線** | 急峻 | 緩やか |
| **ソースコード** | 複雑・ブラックボックス | シンプル・透明 |
| **教育価値** | 実用性重視 | 理解重視 |

### 🔍 主要ライブラリとの比較

#### **PyDub** (音声処理)
```python
# PyDub: 高機能だが内部処理が見えない
from pydub import AudioSegment
sound = AudioSegment.from_wav("input.wav")
louder = sound + 6  # どうやって音量が変わる？
```

```python
# このライブラリ: 処理が明確
signal = load_audio("input.wav")
amplified = signal * 2.0  # 振幅を2倍にする（明確）
```

#### **librosa** (音楽分析)
```python
# librosa: 高度だが初学者には難解
import librosa
y, sr = librosa.load('audio.wav')
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
```

```python
# このライブラリ: 基本から理解
config = AudioConfig(sample_rate=44100)
signal = sine_osc.generate(frequency=440, duration=1.0)
# テンポ検出は将来の拡張として段階的に学習
```

#### **pretty_midi** (MIDI処理)
```python
# pretty_midi: 複雑なデータ構造
import pretty_midi
midi_data = pretty_midi.PrettyMIDI()
instrument = pretty_midi.Instrument(program=1)
```

```python
# このライブラリ: 直感的なノート表現
track.add_note("C4", velocity=100, start_time=0.0, duration=1.0)
# MIDIノート番号も音名も使える
```

### 🎯 教育的優位性

#### **1. ソースコードの透明性**
- **既存ライブラリ**: C++やCythonで最適化、内部処理が見えない
- **このライブラリ**: 純Python、全ての処理が追跡可能

```python
# 学生がエンベロープの中身を確認できる
def generate(self, duration):
    envelope = np.zeros(num_samples)
    for n in range(attack_samples):
        envelope[n] = (1 - np.exp(-5 * n / attack_samples)) / (1 - np.exp(-5))
    # ↑ 数式がそのまま見える！
```

#### **2. 段階的な複雑性**
- **Phase 1**: サイン波 → エンベロープ
- **Phase 2**: 楽器クラス → エフェクト  
- **Phase 3**: シーケンサー → 楽曲制作

#### **3. 理論と実装の一体化**
```python
# 音響理論がコードと直結
frequency = 440.0  # ラ音 = 440Hz
signal = np.sin(2 * np.pi * frequency * time_array)
# ↑ サイン波の数式そのもの
```

### 🎓 教育現場での活用利点

#### **音響工学の授業**
- フーリエ変換、フィルター設計の視覚化
- 理論式からコード実装への橋渡し

#### **プログラミング教育**
- オブジェクト指向設計の実践例
- モジュラープログラミングの体験

#### **音楽理論の学習**
- 音程、和音、スケールの数値的理解
- 楽器の物理的特性との対応

### 🎓 具体的な教育シナリオ

#### **シナリオ1: 「なぜサイン波なのか？」**
```python
# 学生の疑問: 「なぜ音がサイン波で表現できるの？」

# 1. まず基本のサイン波を生成
sine_wave = SineWave()
pure_tone = sine_wave.generate(440, 1.0)

# 2. 複数の周波数を重ね合わせ
tone1 = sine_wave.generate(440, 1.0)    # ラ音
tone2 = sine_wave.generate(880, 1.0)    # 1オクターブ上のラ音
complex_sound = tone1 + tone2

# 3. フーリエ変換で確認（将来の拡張）
# → 「複雑な音も単純な正弦波の組み合わせ」が体験的に理解
```

#### **シナリオ2: 「楽器の音色はなぜ違う？」**
```python
# 同じ音程でも楽器によって音色が違う理由を体験

piano = Piano()
guitar = Guitar()

# 同じC4でも全く違う音
piano_c4 = piano.play_note(60, 100, 2.0)
guitar_c4 = guitar.play_note(60, 100, 2.0)

# 学生が実際にコードを見て理解:
# → ピアノ: 複数の倍音の組み合わせ
# → ギター: ノコギリ波ベース + フィルター
```

#### **シナリオ3: 「エンベロープって何？」**
```python
# 「音量が時間とともに変わる」を体験

# エンベロープなし（クリック音が発生）
raw_sound = sine_wave.generate(440, 1.0)

# エンベロープあり（自然な音）
envelope = ADSREnvelope(attack=0.1, decay=0.2, sustain=0.7, release=0.5)
envelope_data = envelope.generate(1.0)
natural_sound = apply_envelope(raw_sound, envelope_data)

# 学生が聞き比べて実感: 「エンベロープの必要性」
```

### 🚀 実用性との両立

このライブラリは教育用でありながら実用的です：

```python
# 教育用途: 理解重視
sine_osc = SineWave(config)
signal = sine_osc.generate(440, 1.0)

# でも実際に使える楽曲も作れる
sequencer = Sequencer()
track = sequencer.add_track(Piano())
track.add_note("C4", 100, 0.0, 1.0)
sequencer.render("my_song.wav")  # 実際の音楽ファイル
```

### 📈 学習効果の検証可能性

```python
# 学生が実際に確認できる
print(f"440Hzの音程: {frequency_to_note(440)}")  # → 69 (A4)
print(f"C4の周波数: {note_to_frequency(60)}")    # → 261.6Hz

# エンベロープの形も可視化可能
import matplotlib.pyplot as plt
envelope_data = adsr.generate(1.0)
plt.plot(envelope_data)  # ADSR曲線が見える
```

## 📦 インストール

### 必要条件
- Python 3.8 以上
- NumPy, SciPy, Matplotlib

### pip からインストール
```bash
pip install simple-audio-programming
```

### 開発版のインストール
```bash
git clone https://github.com/ggszk/simple-audio-programming.git
cd simple-audio-programming
pip install -e .
```

### 開発用依存関係のインストール
```bash
pip install -r requirements-dev.txt
```

## 🚀 クイックスタート

### 基本的な使用方法
```python
import numpy as np
from audio_lib import SineWave, ADSREnvelope, save_audio

# 1. サイン波を生成
sine_osc = SineWave()
signal = sine_osc.generate(frequency=440, duration=1.0)

# 2. エンベロープを適用
adsr = ADSREnvelope(attack=0.1, decay=0.2, sustain=0.7, release=0.3)
envelope = adsr.generate(duration=1.0)
final_signal = signal * envelope

# 3. WAVファイルとして保存
save_audio("my_first_sound.wav", 44100, final_signal)
```

### Jupyter Notebook でのチュートリアル
```bash
# Jupyter Lab を起動
jupyter lab

# colab_lessons/ フォルダのノートブックを開く
# lesson_01_basics_and_sine_waves.ipynb から始めてください
```

## 🧪 テスト実行

```bash
# 全テストの実行
pytest

# カバレッジ付きテスト
pytest --cov=audio_lib

# 特定のテストファイルのみ
pytest tests/test_oscillators.py -v
```

## 🤝 貢献

プロジェクトへの貢献を歓迎します！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

### 開発環境のセットアップ
```bash
# リポジトリをクローン
git clone https://github.com/ggszk/simple-audio-programming.git
cd simple-audio-programming

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 開発モードでパッケージをインストール
pip install -e .
```

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) の下でライセンスされています。

## 📞 サポート

- 🐛 バグ報告: [Issues](https://github.com/ggszk/simple-audio-programming/issues)
- 💡 機能要求: [Feature Requests](https://github.com/ggszk/simple-audio-programming/issues/new?template=feature_request.md)
- 💬 質問・ディスカッション: [Discussions](https://github.com/ggszk/simple-audio-programming/discussions)

## 今後の拡張可能性

- より多くの楽器クラス
- 高度なエフェクト
- MIDI入力対応
- リアルタイム再生
- GUI インターフェース
- 教育用ビジュアライゼーション
- 段階的な課題システム

---

**音響プログラミングの学習を楽しんでください！** 🎵✨
