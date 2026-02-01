#!/usr/bin/env python3
"""
Quick Ollama connection fix
"""

import subprocess
import time

def quick_fix():
    print("Quick Ollama Connection Fix")
    print("=" * 40)
    
    # 1. Check Ollama processes
    print("\n1. Checking Ollama processes...")
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        if 'ollama' in result.stdout.lower():
            print("Ollama processes found:")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'ollama' in line.lower():
                    print(f"  {line.strip()}")
        else:
            print("No Ollama processes found")
    except Exception as e:
        print(f"Error checking processes: {e}")
    
    # 2. Test connection with PowerShell
    print("\n2. Testing API connection...")
    try:
        result = subprocess.run([
            'powershell', '-Command', 
            "Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("API connection successful!")
            print("Response received")
            return True
        else:
            print(f"API connection failed: {result.stderr}")
    except Exception as e:
        print(f"Connection test error: {e}")
    
    # 3. Restart Ollama
    print("\n3. Restarting Ollama...")
    try:
        # Kill existing processes
        subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], capture_output=True)
        subprocess.run(['taskkill', '/F', '/IM', 'ollama app.exe'], capture_output=True)
        
        time.sleep(2)
        
        # Start Ollama
        subprocess.Popen(['ollama', 'serve'], shell=True)
        print("Ollama restarted")
        
        time.sleep(5)
        
        # Test again
        print("\n4. Testing connection after restart...")
        result = subprocess.run([
            'powershell', '-Command', 
            "Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("Connection successful after restart!")
            return True
        else:
            print("Still failing after restart")
            
    except Exception as e:
        print(f"Restart error: {e}")
    
    return False

if __name__ == "__main__":
    if quick_fix():
        print("\nSUCCESS: Ollama is ready!")
        print("You can now run: start_ai.bat")
    else:
        print("\nFAILED: Ollama connection issues persist")
        print("Please check:")
        print("1. Ollama is installed correctly")
        print("2. Port 11434 is not blocked")
        print("3. Firewall settings")
