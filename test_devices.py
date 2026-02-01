#!/usr/bin/env python3
import sounddevice as sd

print("=== Sound Device Test ===")
try:
    devices = sd.query_devices()
    print(f"Total devices: {len(devices)}")
    
    print("\n=== All Devices ===")
    for i, device in enumerate(devices):
        print(f"ID {i}: {device['name']}")
        print(f"  - Input channels: {device['max_input_channels']}")
        print(f"  - Output channels: {device['max_output_channels']}")
        print(f"  - Default sample rate: {device['default_samplerate']}")
        print()
    
    print("=== Input Devices Only ===")
    input_devices = []
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append({
                'id': i,
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': device['default_samplerate']
            })
            print(f"ID {i}: {device['name']} ({device['max_input_channels']} channels)")
    
    print(f"\nFound {len(input_devices)} input devices")
    
    if len(input_devices) == 0:
        print("No input devices found!")
        print("This is expected in Docker containers without device access.")
    else:
        print("Input devices are available!")
        
except Exception as e:
    print(f"Error: {e}")
    print("This is expected in Docker containers without audio device access.")
