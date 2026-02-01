#!/usr/bin/env python3
"""
Speech Recognition App - 音声認識機能付き
"""

import streamlit as st
import time
import sys
import os
import numpy as np
from datetime import datetime
import tempfile
import wave

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
            'channels': 1,
            'sample_rate': 16000,
            'type': 'simulated',
            'description': '音声認識用シミュレーションマイク'
        }
    ]

def simulate_speech_recording(duration=3, sample_rate=16000):
    """音声認識用のシミュレートされた音声データを生成"""
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples)
    
    # 音声らしい信号（複数の周波数成分）
    signal = (
        np.sin(2 * np.pi * 200 * t) * 0.3 +  # 基本周波数
        np.sin(2 * np.pi * 400 * t) * 0.2 +  # 第2倍音
        np.sin(2 * np.pi * 800 * t) * 0.1 +  # 第3倍音
        np.random.normal(0, 0.05, samples)   # 軽いノイズ
    )
    
    # 音声らしい包絡線
    envelope = np.exp(-t * 0.5) * (1 - np.exp(-t * 10))
    signal = signal * envelope
    
    return signal.astype(np.float32)

def save_audio_to_wav(audio_data, sample_rate, filename):
    """音声データをWAVファイルとして保存"""
    try:
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # float32をint16に変換
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())
        
        return True
    except Exception as e:
        st.error(f"WAVファイル保存エラー: {str(e)}")
        return False

def test_faster_whisper():
    """faster-whisperのテスト"""
    try:
        from faster_whisper import WhisperModel
        st.success("✅ faster-whisper: 正常にインポートされました")
        
        # モデルの初期化テスト
        with st.spinner("Whisperモデルを初期化中..."):
            model = WhisperModel("base", compute_type="float32")
        
        st.success("✅ Whisperモデルの初期化成功")
        return True, model
        
    except ImportError as e:
        st.error(f"❌ faster-whisperインポートエラー: {str(e)}")
        st.info("💡 faster-whisperがインストールされていません")
        return False, None
    except Exception as e:
        st.error(f"❌ Whisperモデル初期化エラー: {str(e)}")
        return False, None

def transcribe_audio(model, audio_file_path):
    """音声ファイルを文字起こし"""
    try:
        with st.spinner("音声認識中..."):
            segments, info = model.transcribe(
                audio_file_path, 
                language="ja",  # 日本語
                beam_size=5
            )
        
        transcription = ""
        confidence_scores = []
        
        for segment in segments:
            transcription += segment.text + " "
            confidence_scores.append(segment.avg_logprob)
        
        # 結果の表示
        st.success("✅ 音声認識完了！")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**認識されたテキスト:**")
            st.write(transcription.strip())
        
        with col2:
            st.write("**認識情報:**")
            st.write(f"検出言語: {info.language}")
            st.write(f"言語確率: {info.language_probability:.2f}")
            st.write(f"セグメント数: {len(list(segments))}")
            
            if confidence_scores:
                avg_confidence = np.mean(confidence_scores)
                st.write(f"平均信頼度: {avg_confidence:.2f}")
        
        return transcription.strip(), info
        
    except Exception as e:
        st.error(f"❌ 音声認識エラー: {str(e)}")
        return None, None

def main():
    st.set_page_config(
        page_title="Speech Recognition",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎤 Speech Recognition App")
    st.markdown("### 音声認識機能付き")
    
    # 基本情報表示
    st.success("✅ Streamlit is running!")
    st.info("ℹ️ これは音声認識機能のテスト版です。シミュレーション音声を使用します。")
    
    # faster-whisperテスト
    st.markdown("### 🤖 音声認識ライブラリテスト")
    
    whisper_available, whisper_model = test_faster_whisper()
    
    if not whisper_available:
        st.warning("⚠️ 音声認識機能が利用できません")
        st.info("💡 faster-whisperのインストールが必要です")
        return
    
    # シミュレーションデバイス選択
    st.markdown("### 🎤 シミュレーションデバイス選択")
    
    simulated_devices = get_simulated_devices()
    st.info(f"🎤 利用可能なシミュレーションデバイス数: {len(simulated_devices)}")
    
    # サイドバーでデバイス選択
    st.sidebar.markdown("### 🎤 デバイス選択")
    
    device_options = [f"{dev['id']}: {dev['name']}" for dev in simulated_devices]
    selected_device_option = st.sidebar.selectbox(
        "シミュレーションマイクを選択:",
        device_options,
        index=1  # 音声認識用デバイスをデフォルト
    )
    
    selected_device_id = int(selected_device_option.split(':')[0])
    selected_device = next((dev for dev in simulated_devices if dev['id'] == selected_device_id), None)
    
    st.sidebar.success(f"✅ 選択されたデバイス: {selected_device['name']}")
    
    # デバイス詳細表示
    with st.expander("🎤 シミュレーションデバイス詳細"):
        for dev in simulated_devices:
            if dev['id'] == selected_device_id:
                st.write(f"**🎯 選択中**: {dev['name']}")
            else:
                st.write(f"**デバイス {dev['id']}**: {dev['name']}")
            st.write(f"  - 説明: {dev['description']}")
            st.write(f"  - サンプルレート: {dev['sample_rate']}")
            st.write("---")
    
    # 音声認識テスト
    st.markdown("### 🎙️ 音声認識テスト")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.slider("録音時間（秒）:", 1, 10, 3)
        sample_rate = st.selectbox("サンプルレート:", [8000, 16000, 22050, 44100], index=1)
    
    with col2:
        speech_type = st.selectbox("音声タイプ:", ["日本語", "英語", "数字", "混合"], index=0)
        noise_level = st.slider("ノイズレベル:", 0.0, 0.2, 0.05, 0.01)
    
    if st.button("🎙️ 録音と音声認識"):
        try:
            st.write(f"🎙️ {duration}秒間の音声録音を開始します...")
            st.write(f"🎤 デバイス: {selected_device['name']}")
            st.write(f"📊 設定: {sample_rate}Hz, {speech_type}, ノイズ: {noise_level}")
            
            # プログレスバー
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # シミュレーション録音データ生成
            audio_data = simulate_speech_recording(duration, sample_rate)
            
            # ノイズを追加
            if noise_level > 0:
                noise = np.random.normal(0, noise_level, len(audio_data))
                audio_data = audio_data + noise
                audio_data = np.clip(audio_data, -1.0, 1.0)
            
            st.success("✅ 録音完了！")
            st.write(f"📊 録音データ: {len(audio_data)} サンプル")
            st.write(f"📊 最大振幅: {np.max(np.abs(audio_data)):.4f}")
            
            # 波形表示
            st.write("📈 録音波形:")
            st.line_chart(audio_data.flatten()[:1000])  # 最初の1000サンプルのみ表示
            
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # WAVファイルとして保存
            if save_audio_to_wav(audio_data, sample_rate, temp_filename):
                st.write("💾 音声ファイル保存完了")
                
                # 音声認識実行
                transcription, info = transcribe_audio(whisper_model, temp_filename)
                
                if transcription:
                    # 結果の詳細表示
                    st.markdown("### 📝 認識結果")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**認識テキスト:**")
                        st.text_area("", transcription, height=100, key="transcription_result")
                    
                    with col2:
                        st.write("**メタデータ:**")
                        st.json({
                            "language": info.language if info else "unknown",
                            "language_probability": info.language_probability if info else 0.0,
                            "duration": duration,
                            "sample_rate": sample_rate,
                            "speech_type": speech_type,
                            "noise_level": noise_level
                        })
                    
                    # テキスト処理オプション
                    st.markdown("### 🔧 テキスト処理")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📋 クリップボードにコピー"):
                            st.write("テキストがクリップボードにコピーされました（シミュレーション）")
                    
                    with col2:
                        if st.button("🔄 再認識"):
                            st.write("再認識を実行します...")
                            transcription, info = transcribe_audio(whisper_model, temp_filename)
                            if transcription:
                                st.experimental_rerun()
                    
                    with col3:
                        if st.button("💾 保存"):
                            st.write("テキストが保存されました（シミュレーション）")
                
                # 一時ファイルを削除
                try:
                    os.unlink(temp_filename)
                except:
                    pass
            
        except Exception as e:
            st.error(f"❌ 録音・認識エラー: {str(e)}")
    
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
                
                tts_text = st.text_input("読み上げるテキスト:", "こんにちは、これは音声認識のテストです")
                
                col1, col2 = st.columns(2)
                
                with col1:
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
                
                with col2:
                    if st.button("🔄 音声認識テスト"):
                        st.write("TTS音声を認識するテスト（実装が必要）")
            
        except Exception as e:
            st.error(f"❌ TTSエンジン初期化エラー: {str(e)}")
            
    except ImportError as e:
        st.error(f"❌ pyttsx3インポートエラー: {str(e)}")
    
    # システム情報
    st.markdown("### 📊 システム情報")
    st.write(f"Pythonバージョン: {sys.version}")
    st.write(f"Streamlitバージョン: {st.__version__}")
    st.write(f"実行環境: Dockerコンテナ")
    st.write(f"音声デバイス: シミュレーション")
    st.write(f"音声認識: faster-whisper")
    
    # ヘルプセクション
    st.markdown("### 💡 ヘルプ")
    
    with st.expander("🔧 音声認識について"):
        st.write("""
        **faster-whisperについて:**
        - OpenAI Whisperの高速実装
        - 多言語対応（日本語・英語など）
        - 高精度な音声認識
        - リアルタイム処理可能
        
        **シミュレーションの特徴:**
        - 実際の音声入力は使用しない
        - 音声らしい信号を生成
        - 音声認識パイプラインをテスト
        - UIと処理ロジックの検証
        
        **認識精度:**
        - シミュレーション音声では意味のあるテキストは生成されません
        - 音声認識プロセスの動作確認が目的
        - 実際の音声認識は実機入力が必要
        """)

if __name__ == "__main__":
    main()
