# Contributing to Simple Audio Programming
# Simple Audio Programming への貢献

このプロジェクトへの貢献をご検討いただき、ありがとうございます！

## 🎯 プロジェクトの目標

このライブラリは**音響プログラミング初心者の教育**を目的としています：

- **理解しやすいコード**: 学生が読んで理解できる実装
- **教育的価値**: 理論と実装の橋渡し
- **段階的学習**: 基本から応用まで自然な学習曲線

## 🤝 貢献の方法

### 1. Issue の報告

バグ報告や機能要求は [Issues](https://github.com/ggszk/simple-audio-programming/issues) でお願いします。

**バグ報告時に含めてください：**
- 使用している Python バージョン
- 再現手順
- 期待される動作と実際の動作
- エラーメッセージ（もしあれば）

### 2. プルリクエスト

1. このリポジトリをフォーク
2. フィーチャーブランチを作成: `git checkout -b feature/amazing-feature`
3. 変更をコミット: `git commit -m 'Add some amazing feature'`
4. ブランチにプッシュ: `git push origin feature/amazing-feature`
5. プルリクエストを作成

## 📝 コーディング規約

### 基本原則
- **教育性を優先**: 高度な最適化よりも理解しやすさを重視
- **日本語コメント**: 教育目的のため、コメントは日本語で記述
- **型ヒント**: 関数の引数と戻り値には型ヒントを使用

### コードスタイル
```python
def generate_sine_wave(frequency: float, duration: float, sample_rate: int = 44100) -> np.ndarray:
    """
    サイン波を生成する関数
    
    Args:
        frequency: 周波数 (Hz)
        duration: 継続時間 (秒)
        sample_rate: サンプリングレート (Hz)
    
    Returns:
        生成されたサイン波のサンプル配列
    """
    # 時間軸の作成
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # サイン波の計算: y = A * sin(2π * f * t)
    wave = np.sin(2 * np.pi * frequency * t)
    
    return wave
```

### 命名規則
- **関数名**: 動詞から始める (`generate_`, `apply_`, `calculate_`)
- **クラス名**: 名詞で、わかりやすい名前 (`SineWave`, `ADSREnvelope`)
- **変数名**: 音響工学の慣例に従う (`sample_rate`, `frequency`, `amplitude`)

## 🧪 テスト

新しい機能を追加する際は、テストも併せて作成してください：

```bash
# テストの実行
pytest tests/

# カバレッジ付きテスト
pytest --cov=audio_lib tests/
```

### テストの例
```python
def test_sine_wave_generation():
    """サイン波生成のテスト"""
    oscillator = SineWave()
    signal = oscillator.generate(frequency=440.0, duration=1.0)
    
    # 期待される長さ
    expected_length = int(44100 * 1.0)
    assert len(signal) == expected_length
    
    # 振幅の範囲チェック
    assert -1.0 <= signal.min() <= signal.max() <= 1.0
```

## 📚 ドキュメント

### Docstring の書き方
```python
def apply_filter(signal: np.ndarray, cutoff_freq: float, filter_type: str = "lowpass") -> np.ndarray:
    """
    信号にフィルターを適用する
    
    Args:
        signal: 入力信号
        cutoff_freq: カットオフ周波数 (Hz)
        filter_type: フィルタータイプ ("lowpass", "highpass", "bandpass")
    
    Returns:
        フィルター適用後の信号
        
    Raises:
        ValueError: 不正なfilter_typeが指定された場合
        
    Example:
        >>> signal = generate_sine_wave(440, 1.0)
        >>> filtered = apply_filter(signal, 1000, "lowpass")
    """
```

## 🎓 教育的配慮

### コメントの書き方
```python
# フーリエ変換による周波数解析
# DFT: X[k] = Σ(n=0 to N-1) x[n] * e^(-j*2π*k*n/N)
fft_result = np.fft.fft(signal)

# パワースペクトラムの計算（振幅の二乗）
power_spectrum = np.abs(fft_result) ** 2
```

### 段階的実装
複雑な処理は段階的に実装し、各段階で何をしているかを明確にしてください：

```python
# ステップ1: 基本的なサイン波生成
basic_wave = np.sin(2 * np.pi * frequency * time)

# ステップ2: エンベロープの適用
envelope = self.adsr.generate(duration)
modulated_wave = basic_wave * envelope

# ステップ3: 最終的な音量調整
final_wave = modulated_wave * amplitude
```

## 🚀 リリースプロセス

1. バージョン番号の更新（`pyproject.toml`）
2. CHANGELOG.md の更新
3. タグの作成: `git tag v1.x.x`
4. GitHub Release の作成

## 📞 質問・相談

不明な点があれば、お気軽に Issue を作成するか、ディスカッションでお聞きください。

---

**あなたの貢献が音響プログラミング学習者の助けになります！** 🎵
