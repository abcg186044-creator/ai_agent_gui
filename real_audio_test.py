#!/usr/bin/env python3
"""
Real Audio Test - 実機音声入力テスト
"""

import streamlit as st
import time
import sys
import os
import numpy as np
from datetime import datetime

def test_sounddevice_import():
    """sounddeviceのインポートと基本機能テスト"""
    try:
        import sounddevice as sd
        st.success("✅ sounddevice: 正常にインポートされました")
        return True, sd
    except ImportError as e:
        st.error(f"❌ sounddeviceインポートエラー: {str(e)}")
        return False, None

def test_device_detection(sd):
    """デバイス検出テスト"""
    try:
        devices = sd.query_devices()
        st.info(f"🎧 検出されたデバイス数: {len(devices)}")
        
        if len(devices) == 0:
            st.warning("⚠️ デバイスが検出されません")
            return []
        
        # デバイス詳細表示
        input_devices = []
        for i, device in enumerate(devices):
            st.write(f"**デバイス {i}**: {device['name']}")
            st.write(f"  - 入力チャンネル: {device['max_input_channels']}")
            st.write(f"  - 出力チャンネル: {device['max_output_channels']}")
            st.write(f"  - サンプルレート: {device['default_samplerate']}")
            
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'id': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
            st.write("---")
        
        st.info(f"🎤 入力デバイス数: {len(input_devices)}")
        return input_devices
        
    except Exception as e:
        st.error(f"❌ デバイス検出エラー: {str(e)}")
        return []

def test_default_device(sd):
    """デフォルトデバイステスト"""
    try:
        default_input = sd.default.device[0]
        default_output = sd.default.device[1]
        
        st.info(f"🎤 デフォルト入力デバイス: {default_input}")
        st.info(f"🔊 デフォルト出力デバイス: {default_output}")
        
        return default_input, default_output
        
    except Exception as e:
        st.error(f"❌ デフォルトデバイス取得エラー: {str(e)}")
        return None, None

def test_audio_stream(sd, device_id=None, sample_rate=16000, channels=1, duration=2):
    """オーディオストリームテスト"""
    try:
        st.write(f"🎙️ オーディオストリームテスト開始...")
        st.write(f"📊 設定: {sample_rate}Hz, {channels}ch, {duration}s")
        
        if device_id is not None:
            st.write(f"🎤 デバイスID: {device_id}")
        else:
            st.write(f"🎤 デバイス: デフォルト")
        
        # ストリームコールバック
        audio_data = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                st.write(f"⚠️ ストリームステータス: {status}")
            audio_data.extend(indata.copy())
        
        # ストリーム開始
        with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            device=device_id,
            callback=audio_callback
        ):
            st.write("🔴 録音中...")
            time.sleep(duration)
        
        if audio_data:
            audio_array = np.array(audio_data)
            st.success(f"✅ 録音完了！ {len(audio_array)} サンプル")
            st.write(f"📊 最大振幅: {np.max(np.abs(audio_array)):.4f}")
            st.write(f"📊 平均振幅: {np.mean(np.abs(audio_array)):.4f}")
            
            # 波形表示
            st.write("📈 波形:")
            st.line_chart(audio_array.flatten()[:1000])  # 最初の1000サンプルのみ表示
            
            return True, audio_array
        else:
            st.warning("⚠️ 音声データがありません")
            return False, None
            
    except Exception as e:
        st.error(f"❌ ストリームエラー: {str(e)}")
        st.info("💡 考えられる原因:")
        st.info("  - デバイス権限の問題")
        st.info("  - 他のアプリケーションがデバイスを使用中")
        st.info("  - デバイスが接続されていない")
        st.info("  - Dockerコンテナの制限")
        return False, None

def test_simple_recording(sd, device_id=None, sample_rate=16000, channels=1, duration=2):
    """シンプル録音テスト"""
    try:
        st.write(f"🎙️ シンプル録音テスト開始...")
        st.write(f"📊 設定: {sample_rate}Hz, {channels}ch, {duration}s")
        
        if device_id is not None:
            st.write(f"🎤 デバイスID: {device_id}")
        else:
            st.write(f"🎤 デバイス: デフォルト")
        
        # 録音
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype='float32',
            device=device_id
        )
        
        st.write("🔴 録音中...")
        sd.wait()
        
        st.success("✅ 録音完了！")
        st.write(f"📊 録音データ: {len(recording)} サンプル")
        st.write(f"📊 最大振幅: {np.max(np.abs(recording)):.4f}")
        st.write(f"📊 平均振幅: {np.mean(np.abs(recording)):.4f}")
        
        # 波形表示
        st.write("📈 波形:")
        st.line_chart(recording.flatten())
        
        return True, recording
        
    except Exception as e:
        st.error(f"❌ 録音エラー: {str(e)}")
        st.info("💡 考えられる原因:")
        st.info("  - デバイス権限の問題")
        st.info("  - 他のアプリケーションがデバイスを使用中")
        st.info("  - デバイスが接続されていない")
        st.info("  - Dockerコンテナの制限")
        return False, None

def test_environment_info():
    """環境情報表示"""
    st.markdown("### 📊 環境情報")
    
    env_info = {
        "Python": sys.version,
        "Streamlit": st.__version__,
        "実行環境": "Dockerコンテナ",
        "OS": os.uname() if hasattr(os, 'uname') else "Unknown",
        "DISPLAY": os.environ.get('DISPLAY', 'Not set'),
        "ALSA_DEVICE": os.environ.get('ALSA_DEVICE', 'Not set'),
        "PULSE_SERVER": os.environ.get('PULSE_SERVER', 'Not set'),
    }
    
    for key, value in env_info.items():
        st.write(f"**{key}**: {value}")

def main():
    st.set_page_config(
        page_title="Real Audio Test",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎤 Real Audio Test")
    st.markdown("### 実機音声入力テスト")
    
    st.info("ℹ️ このテストは実際の音声デバイスを使用します")
    
    # 環境情報
    test_environment_info()
    
    # sounddeviceテスト
    st.markdown("### 🎵 sounddeviceテスト")
    sd_available, sd = test_sounddevice_import()
    
    if not sd_available:
        st.error("❌ sounddeviceが利用できないため、テストを続行できません")
        return
    
    # デバイス検出テスト
    st.markdown("### 🔍 デバイス検出テスト")
    input_devices = test_device_detection(sd)
    
    # デフォルトデバイステスト
    st.markdown("### 🎯 デフォルトデバイステスト")
    default_input, default_output = test_default_device(sd)
    
    if input_devices:
        # デバイス選択
        st.markdown("### 🎤 デバイス選択")
        device_options = [f"{dev['id']}: {dev['name']}" for dev in input_devices]
        selected_device_option = st.selectbox("デバイスを選択:", device_options, index=0)
        selected_device_id = int(selected_device_option.split(':')[0])
        
        # 録音テスト設定
        st.markdown("### 🎙️ 録音テスト設定")
        col1, col2 = st.columns(2)
        
        with col1:
            duration = st.slider("録音時間（秒）:", 1, 5, 2)
            sample_rate = st.selectbox("サンプルレート:", [8000, 16000, 22050, 44100], index=1)
        
        with col2:
            channels = st.selectbox("チャンネル数:", [1, 2], index=0)
            test_method = st.selectbox("テスト方法:", ["シンプル録音", "ストリーム録音"], index=0)
        
        # 録音テスト実行
        st.markdown("### 🎙️ 録音テスト実行")
        
        if st.button("🎙️ 録音テスト開始"):
            if test_method == "シンプル録音":
                success, audio_data = test_simple_recording(
                    sd, selected_device_id, sample_rate, channels, duration
                )
            else:
                success, audio_data = test_audio_stream(
                    sd, selected_device_id, sample_rate, channels, duration
                )
            
            if success and audio_data is not None:
                st.success("✅ 録音テスト成功！")
                
                # 音声分析
                st.markdown("### 📊 音声分析")
                st.write(f"サンプル数: {len(audio_data)}")
                st.write(f"サンプリングレート: {sample_rate} Hz")
                st.write(f"録音時間: {len(audio_data) / sample_rate:.2f} 秒")
                st.write(f"チャンネル数: {channels}")
                st.write(f"データ型: {audio_data.dtype}")
                
                # 統計情報
                st.write("統計情報:")
                st.json({
                    "max_amplitude": float(np.max(np.abs(audio_data))),
                    "min_amplitude": float(np.min(audio_data)),
                    "mean_amplitude": float(np.mean(np.abs(audio_data))),
                    "std_amplitude": float(np.std(audio_data)),
                    "rms": float(np.sqrt(np.mean(audio_data**2))),
                })
                
                # 周波数分析（簡易）
                if channels == 1:
                    try:
                        fft = np.fft.fft(audio_data.flatten())
                        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
                        magnitude = np.abs(fft)
                        
                        st.write("周波数分析:")
                        st.write(f"主周波数: {freqs[np.argmax(magnitude[1:len(magnitude)//2]) + 1]:.2f} Hz")
                        
                    except Exception as e:
                        st.warning(f"⚠️ 周波数分析エラー: {str(e)}")
    
    else:
        st.warning("⚠️ 入力デバイスが見つかりません")
        st.info("💡 Dockerコンテナでは音声デバイスにアクセスできない場合があります")
        st.info("💡 解決策:")
        st.info("  1. Dockerコンテナにデバイス権限を付与")
        st.info("  2. ホストOSの音声サーバーを共有")
        st.info("  3. シミュレーションモードを使用する")

if __name__ == "__main__":
    main()
