"""
教育用チュートリアル: 段階的な音の作り方

元のプログラムで何をしていたかを理解しやすい形で解説
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from audio_lib import (
    AudioConfig, save_audio,
    SineWave, SawtoothWave, SquareWave,
    ADSREnvelope, LinearEnvelope, apply_envelope,
    note_to_frequency, note_name_to_number
)
from audio_lib.effects import LowPassFilter, Reverb

def tutorial_01_what_is_sound():
    """チュートリアル1: 音とは何か？ - サイン波の基本"""
    print("=== チュートリアル1: 音とは何か？ ===")
    
    config = AudioConfig(sample_rate=44100)
    sine_osc = SineWave(config)
    
    # 異なる周波数のサイン波を生成
    frequencies = [220, 440, 880]  # A3, A4, A5
    duration = 1.0
    
    print("異なる周波数のサイン波を生成します:")
    for i, freq in enumerate(frequencies):
        print(f"  {freq} Hz の音を生成中...")
        
        # サイン波を生成
        signal = sine_osc.generate(freq, duration)
        
        # クリック音防止のエンベロープ
        envelope = LinearEnvelope(fade_in=0.01, fade_out=0.01, config=config)
        envelope_data = envelope.generate(duration)
        signal = apply_envelope(signal, envelope_data)
        
        # 保存
        save_audio(f"tutorial_01_sine_{freq}hz.wav", config.sample_rate, signal)
        
        # 波形をプロット（最初の0.01秒分）
        plt.figure(figsize=(10, 4))
        
        # 時間軸
        samples_to_show = int(0.01 * config.sample_rate)  # 0.01秒分
        t = np.linspace(0, 0.01, samples_to_show)
        
        plt.subplot(1, 2, 1)
        plt.plot(t, signal[:samples_to_show])
        plt.title(f'サイン波の波形 ({freq} Hz)')
        plt.xlabel('時間 (秒)')
        plt.ylabel('振幅')
        plt.grid(True)
        
        # 周波数スペクトラム
        plt.subplot(1, 2, 2)
        fft_data = np.fft.fft(signal[:1024])
        fft_freq = np.fft.fftfreq(1024, 1/config.sample_rate)
        plt.plot(fft_freq[:512], np.abs(fft_data[:512]))
        plt.title(f'周波数スペクトラム ({freq} Hz)')
        plt.xlabel('周波数 (Hz)')
        plt.ylabel('振幅')
        plt.xlim(0, 2000)
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(f'tutorial_01_sine_{freq}hz_analysis.png')
        plt.close()
    
    print("→ tutorial_01_sine_*.wav ファイルと分析グラフを保存しました")

def tutorial_02_envelope_importance():
    """チュートリアル2: エンベロープの重要性"""
    print("\n=== チュートリアル2: エンベロープの重要性 ===")
    
    config = AudioConfig()
    sine_osc = SineWave(config)
    frequency = 440.0
    duration = 2.0
    
    # 1. エンベロープなし（クリック音あり）
    print("1. エンベロープなしの音（クリック音が発生）")
    signal_raw = sine_osc.generate(frequency, duration)
    save_audio("tutorial_02_no_envelope.wav", config.sample_rate, signal_raw)
    
    # 2. 線形フェード
    print("2. 線形フェード付きの音")
    linear_env = LinearEnvelope(fade_in=0.1, fade_out=0.1, config=config)
    linear_data = linear_env.generate(duration)
    signal_linear = apply_envelope(signal_raw.copy(), linear_data)
    save_audio("tutorial_02_linear_envelope.wav", config.sample_rate, signal_linear)
    
    # 3. ADSRエンベロープ
    print("3. ADSRエンベロープ付きの音（楽器らしい音）")
    adsr = ADSREnvelope(attack=0.1, decay=0.3, sustain=0.6, release=0.5, config=config)
    adsr_data = adsr.generate(duration, gate_time=1.5)
    signal_adsr = apply_envelope(signal_raw.copy(), adsr_data)
    save_audio("tutorial_02_adsr_envelope.wav", config.sample_rate, signal_adsr)
    
    # エンベロープの形状をプロット
    plt.figure(figsize=(12, 8))
    
    time_axis = np.linspace(0, duration, len(linear_data))
    
    plt.subplot(2, 2, 1)
    plt.plot(time_axis, np.ones_like(time_axis))
    plt.title('エンベロープなし')
    plt.ylabel('振幅')
    plt.grid(True)
    
    plt.subplot(2, 2, 2) 
    plt.plot(time_axis, linear_data)
    plt.title('線形エンベロープ')
    plt.ylabel('振幅')
    plt.grid(True)
    
    plt.subplot(2, 2, 3)
    plt.plot(time_axis, adsr_data)
    plt.title('ADSRエンベロープ')
    plt.xlabel('時間 (秒)')
    plt.ylabel('振幅')
    plt.grid(True)
    
    plt.subplot(2, 2, 4)
    plt.plot(time_axis[:1000], signal_raw[:1000], label='エンベロープなし')
    plt.plot(time_axis[:1000], signal_adsr[:1000], label='ADSR付き')
    plt.title('波形の比較（最初の部分）')
    plt.xlabel('時間 (秒)')
    plt.ylabel('振幅')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('tutorial_02_envelope_comparison.png')
    plt.close()
    
    print("→ tutorial_02_*.wav ファイルと比較グラフを保存しました")

def tutorial_03_waveform_types():
    """チュートリアル3: 異なる波形の音色"""
    print("\n=== チュートリアル3: 異なる波形の音色 ===")
    
    config = AudioConfig()
    frequency = 440.0
    duration = 2.0
    
    # 異なる波形のオシレーター
    oscillators = {
        'sine': SineWave(config),
        'sawtooth': SawtoothWave(config),
        'square': SquareWave(config)
    }
    
    # ADSRエンベロープ
    adsr = ADSREnvelope(attack=0.05, decay=0.2, sustain=0.7, release=0.3, config=config)
    envelope_data = adsr.generate(duration)
    
    print("異なる波形の音色を生成します:")
    
    plt.figure(figsize=(15, 10))
    
    for i, (name, oscillator) in enumerate(oscillators.items()):
        print(f"  {name} 波を生成中...")
        
        # 波形を生成
        signal = oscillator.generate(frequency, duration)
        signal = apply_envelope(signal, envelope_data)
        
        # 保存
        save_audio(f"tutorial_03_{name}_wave.wav", config.sample_rate, signal)
        
        # 波形をプロット
        samples_to_show = int(0.01 * config.sample_rate)  # 0.01秒分
        t = np.linspace(0, 0.01, samples_to_show)
        
        plt.subplot(3, 3, i*3 + 1)
        plt.plot(t, signal[:samples_to_show])
        plt.title(f'{name.capitalize()} Wave - 時間波形')
        plt.ylabel('振幅')
        plt.grid(True)
        
        # 周波数スペクトラム
        plt.subplot(3, 3, i*3 + 2)
        fft_data = np.fft.fft(signal[:2048])
        fft_freq = np.fft.fftfreq(2048, 1/config.sample_rate)
        plt.plot(fft_freq[:1024], np.abs(fft_data[:1024]))
        plt.title(f'{name.capitalize()} Wave - 周波数スペクトラム')
        plt.xlabel('周波数 (Hz)')
        plt.xlim(0, 3000)
        plt.grid(True)
        
        # 倍音の表示
        plt.subplot(3, 3, i*3 + 3)
        harmonics = []
        for h in range(1, 11):  # 10倍音まで
            harmonic_freq = frequency * h
            if harmonic_freq < config.sample_rate / 2:
                # その周波数付近のスペクトラム強度を取得
                freq_index = int(harmonic_freq * 2048 / config.sample_rate)
                if freq_index < len(fft_data):
                    harmonics.append(np.abs(fft_data[freq_index]))
                else:
                    harmonics.append(0)
        
        plt.bar(range(1, len(harmonics) + 1), harmonics)
        plt.title(f'{name.capitalize()} Wave - 倍音構造')
        plt.xlabel('倍音番号')
        plt.ylabel('強度')
        plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('tutorial_03_waveform_analysis.png')
    plt.close()
    
    print("→ tutorial_03_*.wav ファイルと波形分析を保存しました")

def tutorial_04_filter_effects():
    """チュートリアル4: フィルターの効果"""
    print("\n=== チュートリアル4: フィルターの効果 ===")
    
    config = AudioConfig()
    sawtooth_osc = SawtoothWave(config)  # 倍音豊富なノコギリ波
    frequency = 220.0
    duration = 3.0
    
    # 基本の音を生成
    signal = sawtooth_osc.generate(frequency, duration)
    adsr = ADSREnvelope(attack=0.1, decay=0.2, sustain=0.8, release=0.5, config=config)
    envelope_data = adsr.generate(duration)
    signal = apply_envelope(signal, envelope_data)
    
    print("フィルターの効果を比較します:")
    
    # 1. 原音
    print("  1. 原音（フィルターなし）")
    save_audio("tutorial_04_original.wav", config.sample_rate, signal)
    
    # 2. ローパスフィルター（低音域のみ通す）
    print("  2. ローパスフィルター適用")
    lpf = LowPassFilter(cutoff_freq=800, config=config)
    signal_lpf = lpf.process(signal.copy())
    save_audio("tutorial_04_lowpass.wav", config.sample_rate, signal_lpf)
    
    # 3. さらに低いカットオフ周波数
    print("  3. より強いローパスフィルター")
    lpf_strong = LowPassFilter(cutoff_freq=400, config=config)
    signal_lpf_strong = lpf_strong.process(signal.copy())
    save_audio("tutorial_04_lowpass_strong.wav", config.sample_rate, signal_lpf_strong)
    
    # スペクトラム比較
    plt.figure(figsize=(15, 10))
    
    signals = {
        '原音': signal,
        'LPF 800Hz': signal_lpf,
        'LPF 400Hz': signal_lpf_strong
    }
    
    for i, (name, sig) in enumerate(signals.items()):
        # 時間波形
        plt.subplot(3, 2, i*2 + 1)
        samples_to_show = int(0.02 * config.sample_rate)
        t = np.linspace(0, 0.02, samples_to_show)
        plt.plot(t, sig[:samples_to_show])
        plt.title(f'{name} - 時間波形')
        plt.ylabel('振幅')
        plt.grid(True)
        
        # 周波数スペクトラム
        plt.subplot(3, 2, i*2 + 2)
        fft_data = np.fft.fft(sig[:4096])
        fft_freq = np.fft.fftfreq(4096, 1/config.sample_rate)
        plt.plot(fft_freq[:2048], 20 * np.log10(np.abs(fft_data[:2048]) + 1e-10))
        plt.title(f'{name} - 周波数スペクトラム')
        plt.xlabel('周波数 (Hz)')
        plt.ylabel('振幅 (dB)')
        plt.xlim(0, 2000)
        plt.ylim(-60, 20)
        plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('tutorial_04_filter_comparison.png')
    plt.close()
    
    print("→ tutorial_04_*.wav ファイルとフィルター比較を保存しました")

def tutorial_05_reverb_effect():
    """チュートリアル5: リバーブ（残響）の効果"""
    print("\n=== チュートリアル5: リバーブ（残響）の効果 ===")
    
    config = AudioConfig()
    sine_osc = SineWave(config)
    
    # 短い音を生成（リバーブの効果がわかりやすい）
    frequency = 880.0  # A5
    duration = 0.5
    
    signal = sine_osc.generate(frequency, duration)
    # 短いアタック・リリースのエンベロープ
    adsr = ADSREnvelope(attack=0.01, decay=0.1, sustain=0.3, release=0.1, config=config)
    envelope_data = adsr.generate(duration)
    signal = apply_envelope(signal, envelope_data)
    
    print("リバーブの効果を比較します:")
    
    # 1. ドライ音（リバーブなし）
    print("  1. ドライ音（残響なし）")
    # 無音部分を追加してリバーブテールを聞きやすくする
    signal_with_tail = np.concatenate([signal, np.zeros(int(config.sample_rate * 2))])
    save_audio("tutorial_05_dry.wav", config.sample_rate, signal_with_tail)
    
    # 2. 短いリバーブ
    print("  2. 短いリバーブ")
    reverb_short = Reverb(reverb_time=0.5, wet_level=0.3, config=config)
    signal_reverb_short = reverb_short.process(signal_with_tail.copy())
    save_audio("tutorial_05_reverb_short.wav", config.sample_rate, signal_reverb_short)
    
    # 3. 長いリバーブ
    print("  3. 長いリバーブ（ホールのような響き）")
    reverb_long = Reverb(reverb_time=2.0, wet_level=0.5, config=config)
    signal_reverb_long = reverb_long.process(signal_with_tail.copy())
    save_audio("tutorial_05_reverb_long.wav", config.sample_rate, signal_reverb_long)
    
    # 波形比較
    plt.figure(figsize=(15, 8))
    
    signals = {
        'ドライ音': signal_with_tail,
        '短いリバーブ': signal_reverb_short,
        '長いリバーブ': signal_reverb_long
    }
    
    for i, (name, sig) in enumerate(signals.items()):
        plt.subplot(3, 1, i + 1)
        t = np.linspace(0, len(sig) / config.sample_rate, len(sig))
        plt.plot(t, sig)
        plt.title(f'{name} - 時間波形')
        plt.ylabel('振幅')
        plt.xlim(0, 2.5)
        plt.grid(True)
    
    plt.xlabel('時間 (秒)')
    plt.tight_layout()
    plt.savefig('tutorial_05_reverb_comparison.png')
    plt.close()
    
    print("→ tutorial_05_*.wav ファイルとリバーブ比較を保存しました")

def main():
    """全てのチュートリアルを実行"""
    print("音のプログラミング - 教育用チュートリアル")
    print("=" * 60)
    print("このチュートリアルでは、音の基本から段階的に学習できます。")
    print("生成されるWAVファイルとグラフを確認しながら進めてください。")
    print()
    
    try:
        tutorial_01_what_is_sound()
        tutorial_02_envelope_importance()
        tutorial_03_waveform_types()
        tutorial_04_filter_effects()
        tutorial_05_reverb_effect()
        
        print("\n" + "=" * 60)
        print("全てのチュートリアルが完了しました！")
        print()
        print("学習のポイント:")
        print("1. 音は周波数の異なるサイン波で構成される")
        print("2. エンベロープはクリック音防止と楽器らしさに重要")
        print("3. 波形の違いが音色（倍音構造）の違いを生む")
        print("4. フィルターは特定の周波数を強調/減衰させる")
        print("5. リバーブは空間の響きをシミュレートする")
        print()
        print("次は examples/basic_examples.py で実際の楽曲制作を試してみましょう！")
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
