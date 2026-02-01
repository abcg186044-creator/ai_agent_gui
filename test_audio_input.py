#!/usr/bin/env python3
"""
音声入力テストスクリプト
"""

import streamlit as st
import sounddevice as sd
import numpy as np
import time

def test_audio_devices():
    """音声デバイスをテスト"""
    st.title("🎤️ 音声入力テスト")
    
    # デバイス情報を表示
    try:
        device_info = sd.query_devices()
        st.write("### 📱 音声デバイス情報")
        
        input_devices = []
        for i, device in enumerate(device_info):
            if device['max_input_channels'] > 0:
                input_devices.append((i, device))
                st.write(f"**デバイス {i}**: {device['name']}")
                st.write(f"  - 入力チャンネル: {device['max_input_channels']}")
                st.write(f"  - サンプルレート: {device.get('default_samplerate', 'N/A')}")
                st.write("---")
        
        if not input_devices:
            st.error("❌ 入力可能な音声デバイスが見つかりません")
            st.info("💡 マイクが接続されているか確認してください")
            return
        
        # デバイス選択
        selected_device = st.selectbox(
            "🎤️ 音声デバイスを選択",
            options=[f"{i}: {device['name']}" for i, device in input_devices],
            index=0
        )
        
        device_id = int(selected_device.split(":")[0])
        
        # 簡単な録音テスト
        if st.button("🎤️ 録音テスト"):
            st.info("🎤️ 3秒間録音します...")
            
            # 録音パラメータ
            sample_rate = 16000
            duration = 3
            channels = 1
            
            try:
                # 録音
                recording = sd.rec(
                    int(duration * sample_rate),
                    samplerate=sample_rate,
                    channels=channels,
                    dtype='int16',
                    device=device_id
                )
                
                st.info("🔴 録音中...")
                sd.wait()  # 録音完了を待機
                
                st.success("✅ 録音完了！")
                
                # 音声データの基本情報
                audio_array = np.array(recording)
                energy = np.sqrt(np.mean(audio_array**2))
                
                st.write("### 📊 録音データ情報")
                st.write(f"- サンプル数: {len(audio_array)}")
                st.write(f"- サンプルレート: {sample_rate} Hz")
                st.write(f"- チャンネル数: {channels}")
                st.write(f"- 最大値: {np.max(np.abs(audio_array))}")
                st.write(f"- 平均エネルギー: {energy:.6f}")
                
                # エネルギーに基づく音声検出
                if energy > 0.001:  # 閾値を調整
                    st.success("🎤️ 音声が検出されました！")
                else:
                    st.warning("⚠️ 音声が検出されませんでした。マイクを確認してください。")
                
                # 波形表示
                st.write("### 📈 波形（最初の1000サンプル）")
                if len(audio_array) > 1000:
                    st.line_chart(audio_array[:1000])
                else:
                    st.line_chart(audio_array)
                
                # 音声レベルのヒストグラム
                st.write("### 📊 音声レベル分布")
                st.write("音声の大きさの分布を確認します")
                
                # 音声データを保存
                if st.button("💾 録音データを保存"):
                    import wave
                    with wave.open("test_recording.wav", 'wb') as wf:
                        wf.setnchannels(channels)
                        wf.setsampwidth(2)  # 16-bit
                        wf.setframerate(sample_rate)
                        wf.writeframes(recording.tobytes())
                    st.success("✅ test_recording.wav に保存しました")
                
            except Exception as e:
                st.error(f"❌ 録音エラー: {str(e)}")
                st.info("💡 マイクの権限やデバイス設定を確認してください")
        
        # リアルタイム音声レベルテスト
        if st.button("🔊 リアルタイム音声レベル"):
            st.info("🔊 音声レベルを監視中...")
            
            audio_data_list = []
            
            def audio_callback(indata, frames, time, status):
                if status:
                    st.error(f"❌ 音声入力エラー: {status}")
                    return
                
                # 音声レベルを計算
                energy = np.sqrt(np.mean(indata**2))
                audio_data_list.append(energy)
                
                # 最新のデータを保持（最大100個）
                if len(audio_data_list) > 100:
                    audio_data_list.pop(0)
            
            try:
                with sd.InputStream(
                    samplerate=16000,
                    channels=1,
                    dtype='int16',
                    device=device_id,
                    callback=audio_callback
                ):
                    st.info("🔊 5秒間音声レベルを監視します...")
                    
                    for i in range(50):  # 5秒間（0.1秒ごと）
                        time.sleep(0.1)
                        
                        if audio_data_list:
                            current_level = audio_data_list[-1]
                            avg_level = np.mean(audio_data_list)
                            
                            # リアルタイム表示
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("現在のレベル", f"{current_level:.6f}")
                            with col2:
                                st.metric("平均レベル", f"{avg_level:.6f}")
                            with col3:
                                if current_level > 0.001:
                                    st.success("🎤️ 音声検出中")
                                else:
                                    st.info("🔇 無音")
                
                st.success("✅ リアルタイム監視完了")
                
            except Exception as e:
                st.error(f"❌ リアルタイム監視エラー: {str(e)}")
        
    except Exception as e:
        st.error(f"❌ デバイス情報取得エラー: {str(e)}")
        st.info("💡 sounddeviceライブラリのインストールを確認してください")
        st.code("pip install sounddevice")

if __name__ == "__main__":
    test_audio_devices()
