#!/usr/bin/env python3
"""
既定のマイクを設定するスクリプト
"""

import sounddevice as sd
import subprocess
import sys

def show_microphone_guide():
    """マイク設定ガイドを表示"""
    print("🎤️ 既定のマイク設定ガイド")
    print("=" * 50)
    
    # 現在のデバイス情報を表示
    device_info = sd.query_devices()
    default_input = sd.default.device[0]
    
    print("\n📱 現在の音声デバイス:")
    input_devices = []
    
    for i, device in enumerate(device_info):
        if device['max_input_channels'] > 0:
            is_default = (i == default_input)
            input_devices.append((i, device))
            print(f"  デバイス {i}: {device['name']}")
            print(f"    入力チャンネル: {device['max_input_channels']}")
            print(f"    既定デバイス: {'✅' if is_default else '❌'}")
    
    print(f"\n🎯 現在の既定デバイス: {default_input}")
    print(f"   デバイス名: {device_info[default_input]['name']}")
    
    print("\n" + "=" * 50)
    print("📋 既定マイクの設定方法:")
    print("=" * 50)
    
    print("\n🖥️ 方法1: Windowsサウンド設定")
    print("1. タスクバー右下のスピーカーアイコンを右クリック")
    print("2. 「サウンドの設定」を選択")
    print("3. 「入力デバイスを選択」セクション")
    print("4. 使用したいマイクを選択")
    print("5. 「既定として設定」をクリック")
    
    print("\n🖥️ 方法2: サウンドコントロールパネル")
    print("1. Win + R キーを押して「mmsys.cpl」と入力")
    print("2. 「録音」タブを開く")
    print("3. 使用したいマイクを右クリック")
    print("4. 「既定のデバイスとして設定」を選択")
    print("5. 「OK」をクリック")
    
    print("\n🖥️ 方法3: 設定アプリ")
    print("1. Win + I キーで設定を開く")
    print("2. 「システム」→「サウンド」を選択")
    print("3. 「入力デバイス」セクション")
    print("4. 使用したいマイクを選択")
    print("5. 「既定として設定」をクリック")
    
    print("\n" + "=" * 50)
    print("🔧 設定後の確認:")
    print("=" * 50)
    
    print("\n1️⃣ 設定を確認:")
    print("   - 設定したマイクに緑のチェックマークが表示")
    print("   - 「既定のデバイス」と表示される")
    
    print("\n2️⃣ テスト:")
    print("   - Windowsの音声録音アプリでテスト")
    print("   - 音声認識アプリでテスト")
    
    print("\n3️⃣ 再起動:")
    print("   - 設定後、アプリを再起動")
    print("   - PCの再起動で確実に反映")

def open_sound_settings():
    """サウンド設定を開く"""
    try:
        print("\n🚀 サウンド設定を開きます...")
        subprocess.run(['mmsys.cpl'], shell=True)
        print("✅ サウンド設定が開きました")
        print("💡 「録音」タブで既定デバイスを設定してください")
    except Exception as e:
        print(f"❌ サウンド設定の起動エラー: {e}")

def test_microphone():
    """マイクテスト"""
    print("\n🎤️ マイクテストを実行します...")
    try:
        import numpy as np
        import time
        
        # 既定デバイスで録音テスト
        sample_rate = 16000
        duration = 3
        
        print("🔴 3秒間録音します...話してください")
        
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16'
        )
        
        sd.wait()
        
        # 音声データ分析
        audio_array = np.array(recording)
        energy = np.sqrt(np.mean(audio_array**2))
        
        print(f"✅ 録音完了！")
        print(f"📊 平均エネルギー: {energy:.6f}")
        
        if energy > 0.001:
            print("🎤️ 音声が検出されました！")
        else:
            print("⚠️ 音声が検出されませんでした")
            print("💡 マイクの設定を確認してください")
            
    except Exception as e:
        print(f"❌ テストエラー: {e}")

def main():
    """メイン処理"""
    show_microphone_guide()
    
    print("\n" + "=" * 50)
    print("🎯 実行したい操作を選択:")
    print("=" * 50)
    print("1. サウンド設定を開く")
    print("2. マイクテストを実行")
    print("3. 終了")
    
    try:
        choice = input("\n選択 (1-3): ").strip()
        
        if choice == "1":
            open_sound_settings()
        elif choice == "2":
            test_microphone()
        elif choice == "3":
            print("👋 終了します")
        else:
            print("❌ 無効な選択です")
            
    except KeyboardInterrupt:
        print("\n👋 終了します")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    main()
