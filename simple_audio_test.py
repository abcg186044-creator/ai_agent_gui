#!/usr/bin/env python3
"""
簡易音声入力テスト
"""

import sounddevice as sd
import numpy as np
import time

def test_audio():
    """音声テスト"""
    print("🎤️ 音声入力テストを開始します...")
    
    try:
        # デバイス情報表示
        device_info = sd.query_devices()
        default_input_device = sd.default.device[0]  # 既定の入力デバイスID
        
        print("\n📱 利用可能な音声デバイス:")
        
        input_devices = []
        
        for i, device in enumerate(device_info):
            if device['max_input_channels'] > 0:
                input_devices.append((i, device))
                is_default = (i == default_input_device)
                print(f"  デバイス {i}: {device['name']}")
                print(f"    入力チャンネル: {device['max_input_channels']}")
                print(f"    既定入力デバイス: {is_default}")
        
        if not input_devices:
            print("❌ 入力可能な音声デバイスが見つかりません")
            return
        
        # 既定デバイスを選択
        device_id = default_input_device
        device = device_info[device_id]
        
        print(f"\n🎯 既定の入力デバイス {device_id} を使用します: {device['name']}")
        
        # デバイスの詳細情報
        print(f"📋 デバイス詳細:")
        print(f"  名前: {device['name']}")
        print(f"  入力チャンネル: {device['max_input_channels']}")
        print(f"  出力チャンネル: {device['max_output_channels']}")
        print(f"  デフォルトサンプルレート: {device.get('default_samplerate', 'N/A')}")
        
        # 3秒録音テスト
        print("\n🔴 3秒間録音します...話してください")
        
        sample_rate = 16000
        duration = 3
        channels = 1
        
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype='int16',
            device=device_id
        )
        
        sd.wait()  # 録音完了を待機
        
        print("✅ 録音完了！")
        
        # 音声データ分析
        audio_array = np.array(recording)
        energy = np.sqrt(np.mean(audio_array**2))
        max_value = np.max(np.abs(audio_array))
        
        print(f"\n📊 録音データ情報:")
        print(f"  使用デバイス: {device['name']} (ID: {device_id})")
        print(f"  サンプル数: {len(audio_array)}")
        print(f"  サンプルレート: {sample_rate} Hz")
        print(f"  チャンネル数: {channels}")
        print(f"  最大値: {max_value}")
        print(f"  平均エネルギー: {energy:.6f}")
        
        # 音声検出判定
        if energy > 0.001:
            print("🎤️ 音声が検出されました！")
        else:
            print("⚠️ 音声が検出されませんでした")
            print("💡 マイクに近づいて、もう一度試してください")
        
        # リアルタイムテスト
        print("\n🔊 リアルタイム音声レベルテスト（5秒間）")
        print("話してみてください...")
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"❌ エラー: {status}")
                return
            
            energy = np.sqrt(np.mean(indata**2))
            if energy > 0.001:
                print(f"🎤️ 音声検出 (レベル: {energy:.6f})")
            else:
                print(f"🔇 無音 (レベル: {energy:.6f})")
        
        with sd.InputStream(
            samplerate=16000,
            channels=1,
            dtype='int16',
            device=device_id,
            callback=audio_callback
        ):
            time.sleep(5)
        
        print("✅ リアルタイムテスト完了")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        print("💡 マイクの接続や権限を確認してください")

if __name__ == "__main__":
    test_audio()
