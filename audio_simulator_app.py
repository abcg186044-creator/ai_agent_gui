#!/usr/bin/env python3
"""
Audio Simulator App - 音声デバイスシミュレーション版
"""

import streamlit as st
import time
import sys
import os
import numpy as np
from datetime import datetime

def get_simulated_devices():
    """シミュレートされた音声デバイスリストを返す"""
    return [
        {
            'id': 0,
            'name': 'Simulated Microphone - Default',
            'channels': 1,
            'sample_rate': 16000,
            'type': 'simulated',
            'description': 'デフォルトのシミュレーションマイク'
        },
        {
            'id': 1,
            'name': 'Simulated Microphone - High Quality',
            'channels': 2,
            'sample_rate': 44100,
            'type': 'simulated',
            'description': '高品質シミュレーションマイク'
        },
        {
            'id': 2,
            'name': 'Simulated Microphone - Studio',
            'channels': 2,
            'sample_rate': 48000,
            'type': 'simulated',
            'description': 'スタジオ品質シミュレーションマイク'
        }
    ]

def simulate_recording(duration, sample_rate, channels):
    """シミュレートされた録音データを生成"""
    samples = int(duration * sample_rate)
    
    # 正弦波とノイズを組み合わせたシミュレーションデータ
    t = np.linspace(0, duration, samples)
    
    if channels == 1:
        # モノラル
        signal = np.sin(2 * np.pi * 440 * t) * 0.3  # 440Hzの正弦波
        noise = np.random.normal(0, 0.05, samples)   # 軽いノイズ
        recording = signal + noise
    else:
        # ステレオ
        signal_l = np.sin(2 * np.pi * 440 * t) * 0.3
        signal_r = np.sin(2 * np.pi * 660 * t) * 0.3
        noise_l = np.random.normal(0, 0.05, samples)
        noise_r = np.random.normal(0, 0.05, samples)
        recording = np.column_stack([signal_l + noise_l, signal_r + noise_r])
    
    return recording.astype(np.float32)

def main():
    st.set_page_config(
        page_title="Audio Simulator",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎤 Audio Simulator")
    st.markdown("### 音声デバイスシミュレーション版")
    
    # 基本情報表示
    st.success("✅ Streamlit is running!")
    st.info("ℹ️ これはシミュレーション版です。実際の音声デバイスは使用しません。")
    
    # 音声ライブラリのインポートテスト
    st.markdown("### 🎵 音声ライブラリテスト")
    
    sounddevice_available = False
    try:
        import sounddevice as sd
        sounddevice_available = True
        st.warning("⚠️ sounddevice: インポート成功（ただしデバイスは検出されません）")
        
        # 実際のデバイス検出を試行
        try:
            devices = sd.query_devices()
            st.info(f"🎧 実際に検出されたデバイス数: {len(devices)}")
            
            if len(devices) == 0:
                st.warning("⚠️ 実際の音声デバイスが検出されませんでした")
                st.info("💡 これはDockerコンテナ内での正常な動作です")
                st.info("💡 シミュレーションモードを使用します")
            else:
                st.success(f"✅ {len(devices)}個のデバイスが検出されました")
                
        except Exception as e:
            st.warning(f"⚠️ デバイス検出エラー: {str(e)}")
            st.info("💡 シミュレーションモードを使用します")
            
    except ImportError as e:
        st.error(f"❌ sounddeviceインポートエラー: {str(e)}")
        st.info("💡 シミュレーションモードを使用します")
    
    # シミュレーションデバイス選択
    st.markdown("### 🎤 シミュレーションデバイス選択")
    
    simulated_devices = get_simulated_devices()
    st.info(f"🎤 利用可能なシミュレーションデバイス数: {len(simulated_devices)}")
    
    # サイドバーでデバイス選択
    st.sidebar.markdown("### 🎤 デバイス選択")
    
    device_options = [f"{dev['id']}: {dev['name']} ({dev['channels']}ch, {dev['sample_rate']}Hz)" for dev in simulated_devices]
    selected_device_option = st.sidebar.selectbox(
        "シミュレーションマイクを選択:",
        device_options,
        index=0
    )
    
    # 選択されたデバイス情報
    selected_device_id = int(selected_device_option.split(':')[0])
    selected_device = next((dev for dev in simulated_devices if dev['id'] == selected_device_id), None)
    
    st.sidebar.success(f"✅ 選択されたデバイス: {selected_device['name']}")
    st.sidebar.info(f"ID: {selected_device['id']}, チャンネル: {selected_device['channels']}, サンプルレート: {selected_device['sample_rate']}")
    
    # デバイス詳細表示
    with st.expander("🎤 シミュレーションデバイス詳細"):
        for dev in simulated_devices:
            if dev['id'] == selected_device_id:
                st.write(f"**🎯 選択中**: {dev['name']}")
            else:
                st.write(f"**デバイス {dev['id']}**: {dev['name']}")
            st.write(f"  - 説明: {dev['description']}")
            st.write(f"  - 入力チャンネル: {dev['channels']}")
            st.write(f"  - サンプルレート: {dev['sample_rate']}")
            st.write(f"  - タイプ: {dev['type']}")
            st.write("---")
    
    # 録音テスト
    st.markdown("### 🎙️ 録音テスト（シミュレーション）")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.slider("録音時間（秒）:", 1, 10, 3)
        sample_rate = st.selectbox("サンプルレート:", [8000, 16000, 22050, 44100, 48000], index=1)
    
    with col2:
        channels = st.selectbox("チャンネル数:", [1, 2], index=0)
        signal_type = st.selectbox("信号タイプ:", ["正弦波", "ホワイトノイズ", "混合"], index=2)
    
    if st.button("🎙️ 録音開始（シミュレーション）"):
        try:
            st.write(f"🎙️ {duration}秒間のシミュレーション録音を開始します...")
            st.write(f"🎤 デバイス: {selected_device['name']} (ID: {selected_device_id})")
            st.write(f"📊 設定: {sample_rate}Hz, {channels}ch, {signal_type}")
            
            # プログレスバー
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # シミュレーション録音データ生成
            recording = simulate_recording(duration, sample_rate, channels)
            
            st.success("✅ シミュレーション録音完了！")
            st.write(f"📊 録音データ: {len(recording)} サンプル")
            st.write(f"📊 最大振幅: {np.max(np.abs(recording)):.4f}")
            st.write(f"📊 平均振幅: {np.mean(np.abs(recording)):.4f}")
            
            # 波形表示
            st.write("📈 波形:")
            if channels == 1:
                st.line_chart(recording.flatten())
            else:
                for ch in range(channels):
                    st.write(f"チャンネル {ch+1}:")
                    st.line_chart(recording[:, ch])
            
            # 音声情報
            st.write("📊 音声情報:")
            st.json({
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": channels,
                "samples": len(recording),
                "max_amplitude": float(np.max(np.abs(recording))),
                "avg_amplitude": float(np.mean(np.abs(recording))),
                "signal_type": signal_type,
                "device_id": selected_device_id,
                "device_name": selected_device['name'],
                "simulation": True,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            st.error(f"❌ シミュレーション録音エラー: {str(e)}")
    
    # TTSテスト
    st.markdown("### 🗣️ TTSテスト")
    
    try:
        import pyttsx3
        st.success("✅ pyttsx3: 正常にインポートされました")
        
        # TTSエンジン情報
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            st.info(f"🗣️ 検出されたTTS音声数: {len(voices)}")
            
            # 音声選択
            if voices:
                voice_options = [f"{i}: {voice.name}" for i, voice in enumerate(voices)]
                selected_voice = st.selectbox("TTS音声を選択:", voice_options, index=0)
                selected_voice_id = int(selected_voice.split(':')[0])
                
                tts_text = st.text_input("読み上げるテキスト:", "こんにちは、これはシミュレーションテストです")
                
                if st.button("🗣️ TTSテスト"):
                    try:
                        import threading
                        
                        def speak_text():
                            engine = pyttsx3.init()
                            engine.setProperty('voice', voices[selected_voice_id].id)
                            engine.say(tts_text)
                            engine.runAndWait()
                        
                        st.write(f"🗣️ 読み上げ中: {tts_text}")
                        st.write(f"🎤 音声: {voices[selected_voice_id].name}")
                        
                        # 別スレッドで実行
                        thread = threading.Thread(target=speak_text)
                        thread.start()
                        
                        st.success("✅ TTS開始！")
                        
                    except Exception as e:
                        st.error(f"❌ TTSエラー: {str(e)}")
            
            # 音声リスト表示
            with st.expander("TTS音声詳細"):
                for i, voice in enumerate(voices):
                    st.write(f"**音声 {i}**: {voice.name}")
                    st.write(f"  - ID: {voice.id}")
                    st.write(f"  - 言語: {voice.languages}")
                    st.write(f"  - 性別: {voice.gender}")
                    st.write("---")
                    
        except Exception as e:
            st.error(f"❌ TTSエンジン初期化エラー: {str(e)}")
            
    except ImportError as e:
        st.error(f"❌ pyttsx3インポートエラー: {str(e)}")
    
    # PyTorchテスト
    st.markdown("### 🔥 PyTorchテスト")
    
    try:
        import torch
        st.success(f"✅ PyTorch: {torch.__version__}")
        
        # GPU/CPU情報
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.info(f"🖥️ デバイス: {device}")
        
        if torch.cuda.is_available():
            st.write(f"GPU名: {torch.cuda.get_device_name(0)}")
            st.write(f"GPUメモリ: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            
    except ImportError as e:
        st.error(f"❌ PyTorchインポートエラー: {str(e)}")
    
    # システム情報
    st.markdown("### 📊 システム情報")
    st.write(f"Pythonバージョン: {sys.version}")
    st.write(f"Streamlitバージョン: {st.__version__}")
    st.write(f"実行環境: Dockerコンテナ")
    st.write(f"音声デバイス: シミュレーション")
    
    # 環境変数
    st.markdown("### 🔧 環境変数")
    env_vars = {
        'DISPLAY': os.environ.get('DISPLAY', 'Not set'),
        'ALSA_DEVICE': os.environ.get('ALSA_DEVICE', 'Not set'),
        'PULSE_SERVER': os.environ.get('PULSE_SERVER', 'Not set'),
        'CONTAINER': 'Docker',
        'AUDIO_MODE': 'Simulation'
    }
    
    for key, value in env_vars.items():
        st.write(f"{key}: {value}")
    
    # ヘルプセクション
    st.markdown("### 💡 ヘルプ")
    
    with st.expander("🔧 シミュレーションについて"):
        st.write("""
        **なぜシミュレーションが必要か:**
        - Dockerコンテナはホストの音声デバイスに直接アクセスできない
        - sounddeviceライブラリは物理的な音声ハードウェアを必要とする
        - 開発・テスト目的で仮想的な音声処理をシミュレート
        
        **シミュレーションの特徴:**
        - 実際の音声入力は使用しない
        - 数値的に生成された音声データを使用
        - UIと処理ロジックのテストが可能
        - 将来の実装に向けた準備ができる
        
        **実際の音声機能を使用するには:**
        - Dockerコンテナにデバイスアクセス権を付与
        - ホストOSの音声デバイスを共有
        - 専用の音声サーバーを構築
        """)

if __name__ == "__main__":
    main()
