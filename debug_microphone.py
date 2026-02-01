#!/usr/bin/env python3
"""
マイク録音デバッグスクリプト
"""

import sounddevice as sd
import numpy as np
import time
import sys
import traceback

def debug_microphone():
    """マイク録音の詳細デバッグ"""
    print("🔍 マイク録音デバッグを開始します...")
    print("=" * 60)
    
    # 1. sounddeviceのバージョンとバックエンド
    print("\n1️⃣ sounddevice情報:")
    try:
        print(f"   バージョン: {sd.__version__}")
        print(f"   バックエンド: {sd.get_portaudio_version()}")
        print(f"   API: {sd._lib.portaudio.get_host_api_count()}個")
    except Exception as e:
        print(f"   ❌ 情報取得エラー: {e}")
    
    # 2. デバイスの詳細情報
    print("\n2️⃣ デバイス詳細情報:")
    try:
        device_info = sd.query_devices()
        default_input = sd.default.device[0]
        
        for i, device in enumerate(device_info):
            if device['max_input_channels'] > 0:
                is_default = (i == default_input)
                print(f"\n   デバイス {i}: {device['name']}")
                print(f"     入力チャンネル: {device['max_input_channels']}")
                print(f"     出力チャンネル: {device['max_output_channels']}")
                print(f"     デフォルトサンプルレート: {device.get('default_samplerate', 'N/A')}")
                print(f"     既定入力: {'✅' if is_default else '❌'}")
                
                if is_default:
                    print(f"     🎯 このデバイスを使用します")
                    
                    # デバイスの詳細設定を表示
                    try:
                        device_info_detail = sd.query_devices(i)
                        print(f"     詳細: {device_info_detail}")
                    except Exception as e:
                        print(f"     ❌ 詳細取得エラー: {e}")
    
    except Exception as e:
        print(f"   ❌ デバイス情報取得エラー: {e}")
    
    # 3. サンプルレートのテスト
    print("\n3️⃣ サンプルレートテスト:")
    sample_rates = [8000, 16000, 22050, 44100, 48000]
    default_input = sd.default.device[0]
    
    for rate in sample_rates:
        try:
            sd.check_input_settings(
                device=default_input,
                channels=1,
                dtype='int16',
                samplerate=rate
            )
            print(f"   ✅ {rate} Hz: サポートされています")
        except Exception as e:
            print(f"   ❌ {rate} Hz: {e}")
    
    # 4. 簡単な録音テスト（様々な設定）
    print("\n4️⃣ 録音テスト（様々な設定）:")
    
    test_configs = [
        {"samplerate": 16000, "channels": 1, "dtype": "int16", "duration": 1},
        {"samplerate": 44100, "channels": 1, "dtype": "int16", "duration": 1},
        {"samplerate": 16000, "channels": 2, "dtype": "int16", "duration": 1},
        {"samplerate": 16000, "channels": 1, "dtype": "float32", "duration": 1},
    ]
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n   テスト {i}: {config}")
        try:
            print(f"     🔴 {config['duration']}秒間録音中...")
            
            # 設定をチェック
            sd.check_input_settings(
                device=default_input,
                channels=config['channels'],
                dtype=config['dtype'],
                samplerate=config['samplerate']
            )
            
            # 録音実行
            recording = sd.rec(
                int(config['duration'] * config['samplerate']),
                samplerate=config['samplerate'],
                channels=config['channels'],
                dtype=config['dtype'],
                device=default_input
            )
            
            print(f"     ⏳ 録音完了を待機中...")
            sd.wait(timeout=5)  # 5秒タイムアウト
            
            print(f"     ✅ 録音完了！")
            
            # データ分析
            audio_array = np.array(recording)
            energy = np.sqrt(np.mean(audio_array**2))
            max_value = np.max(np.abs(audio_array))
            
            print(f"     📊 サンプル数: {len(audio_array)}")
            print(f"     📊 最大値: {max_value}")
            print(f"     📊 平均エネルギー: {energy:.6f}")
            
            if energy > 0.0001:  # 閾値を下げてテスト
                print(f"     🎤️ 音声が検出されました！")
            else:
                print(f"     ⚠️ 音声が検出されませんでした")
            
        except sd.PortAudioError as e:
            print(f"     ❌ PortAudioエラー: {e}")
        except Exception as e:
            print(f"     ❌ その他エラー: {e}")
            print(f"     📋 詳細: {traceback.format_exc()}")
    
    # 5. コールバック方式のテスト
    print("\n5️⃣ コールバック方式のテスト:")
    try:
        audio_data = []
        
        def callback(indata, frames, time, status):
            if status:
                print(f"     ⚠️ コールバックステータス: {status}")
            audio_data.extend(indata.flatten())
        
        print("     🔴 3秒間コールバック録音中...")
        
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
            print(f"     ✅ コールバック録音完了！")
            print(f"     📊 サンプル数: {len(audio_array)}")
            print(f"     📊 平均エネルギー: {energy:.6f}")
            
            if energy > 0.0001:
                print(f"     🎤️ 音声が検出されました！")
            else:
                print(f"     ⚠️ 音声が検出されませんでした")
        else:
            print(f"     ❌ 音声データがありません")
            
    except Exception as e:
        print(f"     ❌ コールバックエラー: {e}")
        print(f"     📋 詳細: {traceback.format_exc()}")
    
    # 6. 権限とアクセスの確認
    print("\n6️⃣ 権限とアクセスの確認:")
    print("   💡 以下を確認してください:")
    print("   1. Windows設定 → プライバシー → マイク")
    print("   2. 「デスクトップアプリがマイクにアクセスできるようにする」がオン")
    print("   3. ブラウザのマイク権限が許可されている")
    print("   4. マイクが他のアプリで使用されていない")
    
    # 7. 解決策の提案
    print("\n7️⃣ 解決策の提案:")
    print("   🔧 1. 別のライブラリを試す:")
    print("      pip install pyaudio")
    print("      pip uninstall sounddevice")
    
    print("   🔧 2. 別のデバイスを試す:")
    print("      利用可能な他のマイクを試してください")
    
    print("   🔧 3. PCを再起動:")
    print("      ドライバの再読み込みで改善することがあります")
    
    print("   🔧 4. 管理者権限で実行:")
    print("      コマンドプロンプトを管理者として実行")

def main():
    """メイン処理"""
    try:
        debug_microphone()
    except KeyboardInterrupt:
        print("\n\n👋 デバッグを中断しました")
    except Exception as e:
        print(f"\n❌ デバッグエラー: {e}")
        print(f"📋 詳細: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
