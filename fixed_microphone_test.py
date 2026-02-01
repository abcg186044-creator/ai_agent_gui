#!/usr/bin/env python3
"""
修正版マイク録音テスト
"""

import sounddevice as sd
import numpy as np
import time
import sys

def test_microphone_fixed():
    """修正版マイクテスト"""
    print("🎤️ 修正版マイク録音テスト")
    print("=" * 50)
    
    # 既定デバイス情報
    default_input = sd.default.device[0]
    device_info = sd.query_devices(default_input)
    
    print(f"🎯 既定デバイス: {device_info['name']}")
    print(f"   入力チャンネル: {device_info['max_input_channels']}")
    print(f"   デフォルトサンプルレート: {device_info.get('default_samplerate', 'N/A')}")
    
    # 1. 基本的な録音テスト（修正版）
    print("\n1️⃣ 基本的な録音テスト:")
    try:
        sample_rate = 16000
        duration = 3
        channels = 1  # ヘッドセットはモノラル
        
        print(f"🔴 {duration}秒間録音します...話してください")
        
        # 録音開始
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype='int16',
            device=default_input
        )
        
        # タイムアウトなしで待機
        print("⏳ 録音中...")
        sd.wait()  # timeout引数を削除
        
        print("✅ 録音完了！")
        
        # データ分析
        audio_array = np.array(recording)
        energy = np.sqrt(np.mean(audio_array**2))
        max_value = np.max(np.abs(audio_array))
        
        print(f"📊 録音データ情報:")
        print(f"   サンプル数: {len(audio_array)}")
        print(f"   サンプルレート: {sample_rate} Hz")
        print(f"   チャンネル数: {channels}")
        print(f"   最大値: {max_value}")
        print(f"   平均エネルギー: {energy:.6f}")
        
        # 音声検出判定（閾値を調整）
        threshold = 0.001
        if energy > threshold:
            print(f"🎤️ 音声が検出されました！（閾値: {threshold})")
            return True
        else:
            print(f"⚠️ 音声が検出されませんでした（閾値: {threshold}）")
            print("💡 マイクに近づいて、もっと大きな声で話してみてください")
            
            # 波形の一部を表示
            if len(audio_array) > 100:
                print(f"📈 波形サンプル（最初の100点）:")
                print(f"   {audio_array[:100]}")
            
            return False
            
    except Exception as e:
        print(f"❌ 録音エラー: {e}")
        return False
    
    # 2. 別のサンプルレートでテスト
    print("\n2️⃣ 別のサンプルレートでテスト:")
    for rate in [44100, 48000]:
        try:
            print(f"🔴 {rate} Hzで2秒間録音...")
            
            recording = sd.rec(
                int(2 * rate),
                samplerate=rate,
                channels=1,
                dtype='int16',
                device=default_input
            )
            
            sd.wait()
            
            audio_array = np.array(recording)
            energy = np.sqrt(np.mean(audio_array**2))
            
            print(f"   ✅ {rate} Hz: エネルギー {energy:.6f}")
            
            if energy > 0.001:
                print(f"   🎤️ 音声検出！")
                return True
            
        except Exception as e:
            print(f"   ❌ {rate} Hz: {e}")
    
    # 3. コールバック方式（修正版）
    print("\n3️⃣ コールバック方式テスト:")
    try:
        audio_data = []
        
        def callback(indata, frames, time_info, status):
            if status:
                print(f"   ⚠️ ステータス: {status}")
            audio_data.extend(indata.flatten())
        
        print("🔴 3秒間コールバック録音...")
        
        with sd.InputStream(
            samplerate=16000,
            channels=1,
            dtype='int16',
            device=default_input,
            callback=callback
        ):
            time.sleep(3)
        
        if audio_data:
            audio_array = np.array(audio_data)
            energy = np.sqrt(np.mean(audio_array**2))
            
            print(f"✅ コールバック録音完了！")
            print(f"📊 サンプル数: {len(audio_array)}")
            print(f"📊 平均エネルギー: {energy:.6f}")
            
            if energy > 0.001:
                print(f"🎤️ 音声が検出されました！")
                return True
            else:
                print(f"⚠️ 音声が検出されませんでした")
        else:
            print(f"❌ 音声データがありません")
            
    except Exception as e:
        print(f"❌ コールバックエラー: {e}")
    
    return False

def test_different_devices():
    """別のデバイスをテスト"""
    print("\n4️⃣ 別のデバイスをテスト:")
    
    device_info = sd.query_devices()
    input_devices = []
    
    # 入力デバイスを収集
    for i, device in enumerate(device_info):
        if device['max_input_channels'] > 0:
            input_devices.append((i, device))
    
    # 最初の3つのデバイスをテスト
    for i, (device_id, device) in enumerate(input_devices[:3]):
        print(f"\n🎯 デバイス {device_id}: {device['name']}")
        
        try:
            # 1秒録音テスト
            recording = sd.rec(
                16000,  # 1秒
                samplerate=16000,
                channels=1,
                dtype='int16',
                device=device_id
            )
            
            sd.wait()
            
            audio_array = np.array(recording)
            energy = np.sqrt(np.mean(audio_array**2))
            
            print(f"   📊 エネルギー: {energy:.6f}")
            
            if energy > 0.001:
                print(f"   🎤️ このデバイスで音声検出！")
                print(f"   💡 このデバイスを既定に設定することをお勧めします")
                return device_id
                
        except Exception as e:
            print(f"   ❌ エラー: {e}")
    
    return None

def main():
    """メイン処理"""
    print("🎤️ ヘッドセット (ATH-CK150BT) 専用テスト")
    print("=" * 50)
    
    # 基本的なテスト
    success = test_microphone_fixed()
    
    if not success:
        # 別のデバイスをテスト
        recommended_device = test_different_devices()
        
        if recommended_device is not None:
            print(f"\n💡 推奨デバイスが見つかりました: {recommended_device}")
            print("このデバイスを既定に設定することをお勧めします")
        else:
            print("\n🔧 トラブルシューティング:")
            print("1. ヘッドセットの接続を確認")
            print("2. 他のアプリでマイクを使用していないか確認")
            print("3. Windowsのマイク権限を確認")
            print("4. ヘッドセットを再接続")
    
    print("\n🎯 結論:")
    if success:
        print("✅ マイク録音は正常に動作しています")
        print("🚀 AI Agent Systemを起動できます")
    else:
        print("❌ マイク録音に問題があります")
        print("🔧 上記のトラブルシューティングを試してください")

if __name__ == "__main__":
    main()
