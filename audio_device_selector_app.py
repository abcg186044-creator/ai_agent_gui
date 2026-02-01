#!/usr/bin/env python3
"""
Audio Device Selector App - マイクデバイス選択機能付き
"""

import streamlit as st
import time
import sys
import os

def main():
    st.set_page_config(
        page_title="Audio Device Selector",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎤 Audio Device Selector")
    st.markdown("### マイクデバイス選択機能")
    
    # 基本情報表示
    st.success("✅ Streamlit is running!")
    
    # 音声ライブラリのインポートテスト
    st.markdown("### 🎵 音声ライブラリテスト")
    
    sounddevice_available = False
    try:
        import sounddevice as sd
        sounddevice_available = True
        st.success("✅ sounddevice: 正常にインポートされました")
        
        # デバイス情報取得
        try:
            devices = sd.query_devices()
            st.info(f"🎧 検出された音声デバイス数: {len(devices)}")
            
            # 入力デバイスのみ抽出
            input_devices = []
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': device['default_samplerate']
                    })
            
            st.info(f"🎤 入力デバイス数: {len(input_devices)}")
            
            # サイドバーでデバイス選択
            st.sidebar.markdown("### 🎤 デバイス選択")
            
            if input_devices:
                device_options = [f"{dev['id']}: {dev['name']} ({dev['channels']}ch)" for dev in input_devices]
                selected_device_option = st.sidebar.selectbox(
                    "マイクデバイスを選択:",
                    device_options,
                    index=0
                )
                
                # 選択されたデバイスIDを取得
                selected_device_id = int(selected_device_option.split(':')[0])
                selected_device = next((dev for dev in input_devices if dev['id'] == selected_device_id), None)
                
                st.sidebar.success(f"✅ 選択されたデバイス: {selected_device['name']}")
                st.sidebar.info(f"ID: {selected_device['id']}, チャンネル: {selected_device['channels']}, サンプルレート: {selected_device['sample_rate']}")
                
                # デバイス詳細表示
                with st.expander("🎤 入力デバイス詳細"):
                    for dev in input_devices:
                        if dev['id'] == selected_device_id:
                            st.write(f"**🎯 選択中**: {dev['name']}")
                        else:
                            st.write(f"**デバイス {dev['id']}**: {dev['name']}")
                        st.write(f"  - 入力チャンネル: {dev['channels']}")
                        st.write(f"  - サンプルレート: {dev['sample_rate']}")
                        st.write("---")
                
                # 録音テスト
                st.markdown("### 🎙️ 録音テスト")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    duration = st.slider("録音時間（秒）:", 1, 10, 3)
                    sample_rate = st.selectbox("サンプルレート:", [8000, 16000, 22050, 44100, 48000], index=1)
                
                with col2:
                    channels = st.selectbox("チャンネル数:", [1, 2], index=0)
                
                if st.button("🎙️ 録音開始"):
                    try:
                        import numpy as np
                        
                        st.write(f"🎙️ {duration}秒間録音します...")
                        st.write(f"🎤 デバイス: {selected_device['name']} (ID: {selected_device_id})")
                        st.write(f"📊 設定: {sample_rate}Hz, {channels}ch")
                        
                        # 録音
                        recording = sd.rec(
                            int(duration * sample_rate), 
                            samplerate=sample_rate, 
                            channels=channels, 
                            dtype='float32',
                            device=selected_device_id
                        )
                        sd.wait()
                        
                        st.success("✅ 録音完了！")
                        st.write(f"📊 録音データ: {len(recording)} サンプル")
                        st.write(f"📊 最大振幅: {np.max(np.abs(recording)):.4f}")
                        
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
                            "device_id": selected_device_id,
                            "device_name": selected_device['name']
                        })
                        
                    except Exception as e:
                        st.error(f"❌ 録音エラー: {str(e)}")
                        st.info("💡 ヒント: デバイスの権限設定や、他のアプリケーションがマイクを使用していないか確認してください")
                
            else:
                st.error("❌ 入力デバイスが見つかりません")
                st.info("💡 ヒント: マイクが接続されているか、Dockerコンテナのデバイス権限を確認してください")
                
        except Exception as e:
            st.error(f"❌ デバイス情報取得エラー: {str(e)}")
            
    except ImportError as e:
        st.error(f"❌ sounddeviceインポートエラー: {str(e)}")
    
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
                
                tts_text = st.text_input("読み上げるテキスト:", "こんにちは、これはテストです")
                
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
    
    # 環境変数
    st.markdown("### 🔧 環境変数")
    env_vars = {
        'DISPLAY': os.environ.get('DISPLAY', 'Not set'),
        'ALSA_DEVICE': os.environ.get('ALSA_DEVICE', 'Not set'),
        'PULSE_SERVER': os.environ.get('PULSE_SERVER', 'Not set'),
    }
    
    for key, value in env_vars.items():
        st.write(f"{key}: {value}")
    
    # ヘルプセクション
    st.markdown("### 💡 ヘルプ")
    
    with st.expander("🔧 トラブルシューティング"):
        st.write("""
        **マイクが認識されない場合:**
        1. Dockerコンテナにデバイスアクセス権を付与
        2. ホストのマイクが正常に動作しているか確認
        3. 他のアプリケーションがマイクを使用していないか確認
        
        **録音に失敗する場合:**
        1. デバイスIDを確認して正しいデバイスを選択
        2. サンプルレートやチャンネル数を変更
        3. コンテナの再起動を試す
        
        **TTSが動作しない場合:**
        1. eSpeak/espeak-ngのインストールを確認
        2. 音声出力デバイスを確認
        3. 異なる音声を選択
        """)

if __name__ == "__main__":
    main()
