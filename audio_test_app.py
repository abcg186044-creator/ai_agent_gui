#!/usr/bin/env python3
"""
Audio Test App - 音声機能テスト用
"""

import streamlit as st
import time
import sys
import os

def main():
    st.set_page_config(
        page_title="Audio Test App",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎤 Audio Test App")
    st.markdown("### 音声機能テスト")
    
    # 基本情報表示
    st.success("✅ Streamlit is running!")
    
    # 音声ライブラリのインポートテスト
    st.markdown("### 🎵 音声ライブラリテスト")
    
    try:
        import sounddevice as sd
        st.success("✅ sounddevice: 正常にインポートされました")
        
        # デバイス情報取得
        try:
            devices = sd.query_devices()
            st.info(f"🎧 検出された音声デバイス数: {len(devices)}")
            
            # デバイスリスト表示
            with st.expander("音声デバイス詳細"):
                for i, device in enumerate(devices):
                    st.write(f"**デバイス {i}**: {device['name']}")
                    st.write(f"  - 入力チャンネル: {device['max_input_channels']}")
                    st.write(f"  - 出力チャンネル: {device['max_output_channels']}")
                    st.write(f"  - サンプルレート: {device['default_samplerate']}")
                    st.write("---")
        except Exception as e:
            st.error(f"❌ デバイス情報取得エラー: {str(e)}")
            
    except ImportError as e:
        st.error(f"❌ sounddeviceインポートエラー: {str(e)}")
    
    try:
        import pyttsx3
        st.success("✅ pyttsx3: 正常にインポートされました")
        
        # TTSエンジン情報
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            st.info(f"🗣️ 検出されたTTS音声数: {len(voices)}")
            
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
    
    # 音声録音テスト
    st.markdown("### 🎙️ 音声録音テスト")
    
    if st.button("音声録音テスト"):
        try:
            import sounddevice as sd
            import numpy as np
            
            st.write("🎙️ 3秒間録音します...")
            
            # 録音
            sample_rate = 16000
            duration = 3
            recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
            sd.wait()
            
            st.success("✅ 録音完了！")
            st.write(f"📊 録音データ: {len(recording)} サンプル")
            st.write(f"📊 サンプルレート: {sample_rate} Hz")
            st.write(f"📊 最大振幅: {np.max(np.abs(recording)):.4f}")
            
            # 波形表示
            st.line_chart(recording.flatten())
            
        except Exception as e:
            st.error(f"❌ 録音エラー: {str(e)}")
    
    # TTSテスト
    st.markdown("### 🗣️ TTSテスト")
    
    tts_text = st.text_input("読み上げるテキスト:", "こんにちは、これはテストです")
    
    if st.button("TTSテスト"):
        try:
            import pyttsx3
            import threading
            
            def speak_text():
                engine = pyttsx3.init()
                engine.say(tts_text)
                engine.runAndWait()
            
            st.write(f"🗣️ 読み上げ中: {tts_text}")
            
            # 別スレッドで実行
            thread = threading.Thread(target=speak_text)
            thread.start()
            
            st.success("✅ TTS開始！")
            
        except Exception as e:
            st.error(f"❌ TTSエラー: {str(e)}")
    
    # システム情報
    st.markdown("### 📊 システム情報")
    st.write(f"Pythonバージョン: {sys.version}")
    st.write(f"Streamlitバージョン: {st.__version__}")
    
    # 環境変数
    st.markdown("### 🔧 環境変数")
    env_vars = {
        'DISPLAY': os.environ.get('DISPLAY', 'Not set'),
        'ALSA_DEVICE': os.environ.get('ALSA_DEVICE', 'Not set'),
        'PULSE_SERVER': os.environ.get('PULSE_SERVER', 'Not set'),
    }
    
    for key, value in env_vars.items():
        st.write(f"{key}: {value}")

if __name__ == "__main__":
    main()
