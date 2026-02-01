#!/usr/bin/env python3
"""
マイク選択スクリプト
"""

import sounddevice as sd
import numpy as np
import sys

def get_microphone_list():
    """利用可能なマイクリストを取得"""
    device_info = sd.query_devices()
    microphones = []
    
    for i, device in enumerate(device_info):
        if device['max_input_channels'] > 0:
            microphones.append({
                'id': i,
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': device.get('default_samplerate', 44100)
            })
    
    return microphones

def test_microphone(device_id, duration=2):
    """マイクをテスト"""
    try:
        print(f"Testing microphone {device_id} for {duration} seconds...")
        
        recording = sd.rec(
            int(duration * 16000),
            samplerate=16000,
            channels=1,
            dtype='int16',
            device=device_id
        )
        
        sd.wait()
        
        audio_array = np.array(recording)
        energy = np.sqrt(np.mean(audio_array**2))
        
        return {
            'success': True,
            'energy': energy,
            'max_value': np.max(np.abs(audio_array)),
            'samples': len(audio_array)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def select_microphone():
    """マイク選択インターフェース"""
    print("Microphone Selection Tool")
    print("=" * 50)
    
    # 利用可能なマイクを表示
    microphones = get_microphone_list()
    
    if not microphones:
        print("No microphones found!")
        return None
    
    print("\nAvailable Microphones:")
    print("-" * 50)
    
    for i, mic in enumerate(microphones):
        print(f"{i+1}. {mic['name']}")
        print(f"   ID: {mic['id']}")
        print(f"   Channels: {mic['channels']}")
        print(f"   Sample Rate: {mic['sample_rate']}")
        print()
    
    # 現在の既定デバイスを表示
    try:
        default_input = sd.default.device[0]
        default_device = sd.query_devices(default_input)
        print(f"Current Default: {default_device['name']} (ID: {default_input})")
        print()
    except:
        pass
    
    while True:
        try:
            choice = input("Select microphone (1-{}), or 't' to test, 'd' for default, 'q' to quit: ".format(len(microphones)))
            
            if choice.lower() == 'q':
                print("Quitting...")
                return None
            
            elif choice.lower() == 'd':
                try:
                    default_input = sd.default.device[0]
                    print(f"Using default microphone: {sd.query_devices(default_input)['name']}")
                    return default_input
                except:
                    print("Error getting default microphone")
                    continue
            
            elif choice.lower() == 't':
                # テストモード
                test_choice = input("Enter microphone number to test (1-{}): ".format(len(microphones)))
                try:
                    test_idx = int(test_choice) - 1
                    if 0 <= test_idx < len(microphones):
                        mic = microphones[test_idx]
                        print(f"\nTesting {mic['name']}...")
                        print("Please speak into the microphone...")
                        
                        result = test_microphone(mic['id'])
                        
                        if result['success']:
                            print(f"✅ Test successful!")
                            print(f"   Energy: {result['energy']:.6f}")
                            print(f"   Max Value: {result['max_value']}")
                            print(f"   Samples: {result['samples']}")
                            
                            if result['energy'] > 0.001:
                                print("🎤 Voice detected!")
                            else:
                                print("⚠️ No voice detected (try speaking louder)")
                        else:
                            print(f"❌ Test failed: {result['error']}")
                        print()
                    else:
                        print("Invalid microphone number")
                except ValueError:
                    print("Invalid input")
                continue
            
            else:
                # マイク選択
                mic_idx = int(choice) - 1
                if 0 <= mic_idx < len(microphones):
                    selected_mic = microphones[mic_idx]
                    print(f"\nSelected: {selected_mic['name']}")
                    
                    # 最終テスト
                    print("Testing selected microphone...")
                    print("Please speak into the microphone...")
                    
                    result = test_microphone(selected_mic['id'])
                    
                    if result['success']:
                        print(f"✅ Test successful!")
                        print(f"   Energy: {result['energy']:.6f}")
                        
                        if result['energy'] > 0.001:
                            print("🎤 Voice detected! Microphone is working.")
                            confirm = input("Use this microphone? (y/n): ").lower()
                            if confirm == 'y':
                                return selected_mic['id']
                            else:
                                continue
                        else:
                            print("⚠️ No voice detected")
                            retry = input("Try again or select different microphone? (r/d): ").lower()
                            if retry == 'r':
                                continue
                            else:
                                return selected_mic['id']
                    else:
                        print(f"❌ Test failed: {result['error']}")
                        continue
                else:
                    print("Invalid microphone number")
                    
        except ValueError:
            print("Invalid input")
        except KeyboardInterrupt:
            print("\nQuitting...")
            return None

def set_default_microphone(device_id):
    """既定マイクを設定（情報表示のみ）"""
    try:
        device_info = sd.query_devices(device_id)
        print(f"\nTo set '{device_info['name']}' as default microphone:")
        print("1. Right-click speaker icon in taskbar")
        print("2. Select 'Sound settings'")
        print("3. Choose input device")
        print("4. Select '{}'".format(device_info['name']))
        print("5. Click 'Set as default'")
        print("\nOr use Sound Control Panel:")
        print("1. Press Win+R and type 'mmsys.cpl'")
        print("2. Go to 'Recording' tab")
        print("3. Right-click '{}'".format(device_info['name']))
        print("4. Select 'Set as Default Device'")
        print("5. Click 'OK'")
        
        return device_info['name']
    except Exception as e:
        print(f"Error getting device info: {e}")
        return None

def main():
    """メイン処理"""
    print("AI Agent System - Microphone Selection")
    print("=" * 50)
    
    selected_device = select_microphone()
    
    if selected_device is not None:
        device_name = set_default_microphone(selected_device)
        
        if device_name:
            print(f"\n✅ Microphone selected: {device_name}")
            print("Please set it as default in Windows settings")
            print("Then run: start_ai.bat")
            
            # 設定を保存
            with open('selected_microphone.txt', 'w') as f:
                f.write(f"{selected_device}\n{device_name}")
            
            print("Selection saved to 'selected_microphone.txt'")
        else:
            print("Error selecting microphone")
    else:
        print("No microphone selected")

if __name__ == "__main__":
    main()
