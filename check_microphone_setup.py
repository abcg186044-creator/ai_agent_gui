#!/usr/bin/env python3
"""
マイク設定チェックスクリプト
"""

import sounddevice as sd
import numpy as np
import sys

def check_microphone_setup():
    """マイク設定をチェック"""
    print("🎤️ マイク設定チェックを開始します...")
    print("=" * 50)
    
    # 1. 既定デバイスの確認
    print("\n1️⃣ 既定デバイスの確認:")
    try:
        device_info = sd.query_devices()
        default_input = sd.default.device[0]
        default_device = device_info[default_input]
        
        print(f"   現在の既定デバイス: {default_device['name']}")
        print(f"   入力チャンネル: {default_device['max_input_channels']}")
        
        if default_device['max_input_channels'] == 0:
            print("   ❌ 既定デバイスに入力チャンネルがありません")
            return False
        
        # 2. 録音テスト
        print("\n2️⃣ 録音テスト:")
        try:
            print("   🔴 2秒間録音テスト...")
            
            recording = sd.rec(
                int(2 * 16000),
                samplerate=16000,
                channels=1,
                dtype='int16',
                device=default_input
            )
            
            sd.wait()
            
            audio_array = np.array(recording)
            energy = np.sqrt(np.mean(audio_array**2))
            
            print(f"   📊 平均エネルギー: {energy:.6f}")
            
            if energy > 0.001:
                print("   ✅ 音声が検出されました")
                print("   ✅ マイク設定は正常です")
                return True
            else:
                print("   ⚠️ 音声が検出されませんでした")
                print("   💡 マイクに近づいて、もう一度テストしてください")
                
                # 再テスト
                print("\n   🔴 もう一度テストします（3秒間）...")
                input("   準備ができたらEnterキーを押してください...")
                
                recording = sd.rec(
                    int(3 * 16000),
                    samplerate=16000,
                    channels=1,
                    dtype='int16',
                    device=default_input
                )
                
                sd.wait()
                
                audio_array = np.array(recording)
                energy = np.sqrt(np.mean(audio_array**2))
                
                print(f"   📊 平均エネルギー: {energy:.6f}")
                
                if energy > 0.001:
                    print("   ✅ 音声が検出されました")
                    print("   ✅ マイク設定は正常です")
                    return True
                else:
                    print("   ❌ 音声が検出されませんでした")
                    return False
                    
        except Exception as e:
            print(f"   ❌ 録音テストエラー: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ デバイス確認エラー: {e}")
        return False

def show_microphone_guide():
    """マイク設定ガイドを表示"""
    print("\n" + "=" * 50)
    print("📋 マイク設定ガイド")
    print("=" * 50)
    
    print("\n🖥️ Windowsで既定マイクを設定する方法:")
    print("1. タスクバー右下のスピーカーアイコンを右クリック")
    print("2. 「サウンドの設定」を選択")
    print("3. 「入力デバイスを選択」セクション")
    print("4. 使用したいマイクを選択")
    print("5. 「既定として設定」をクリック")
    
    print("\n🖥️ またはサウンドコントロールパネル:")
    print("1. Win + R キーを押して「mmsys.cpl」と入力")
    print("2. 「録音」タブを開く")
    print("3. 使用したいマイクを右クリック")
    print("4. 「既定のデバイスとして設定」を選択")
    print("5. 「OK」をクリック")
    
    print("\n💡 設定後の確認:")
    print("- 設定したマイクに緑のチェックマークが表示")
    print("- 「既定のデバイス」と表示される")
    print("- このスクリプトを再実行して確認")

def main():
    """メイン処理"""
    success = check_microphone_setup()
    
    if not success:
        show_microphone_guide()
        
        print("\n" + "=" * 50)
        print("🎯 次の操作を選択してください:")
        print("1. マイク設定を変更して再テスト")
        print("2. 無視して続行（非推奨）")
        print("3. 終了")
        
        try:
            choice = input("\n選択 (1-3): ").strip()
            
            if choice == "1":
                print("\n🔄 マイク設定を変更してください...")
                print("設定が完了したら、このスクリプトを再実行してください")
                return False
            elif choice == "2":
                print("\n⚠️ 無視して続行します（音声機能は正常に動作しない可能性があります）")
                return True
            elif choice == "3":
                print("\n👋 終了します")
                return False
            else:
                print("\n❌ 無効な選択です")
                return False
                
        except KeyboardInterrupt:
            print("\n👋 終了します")
            return False
    else:
        print("\n🎉 マイク設定チェック完了！")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
