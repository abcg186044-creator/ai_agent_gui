#!/usr/bin/env python3
"""
Simple Ollama test without Unicode
"""

import subprocess
import json
import time

def test_ollama():
    print("Testing Ollama Connection")
    print("=" * 40)
    
    # Test 1: Check processes
    print("1. Checking Ollama processes...")
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        if 'ollama' in result.stdout.lower():
            print("Ollama processes found")
        else:
            print("No Ollama processes found")
            return False
    except:
        print("Error checking processes")
        return False
    
    # Test 2: Test API
    print("2. Testing API connection...")
    try:
        result = subprocess.run([
            'powershell', '-Command', 
            "Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("API connection successful")
        else:
            print(f"API connection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"API test error: {e}")
        return False
    
    # Test 3: Get models
    print("3. Getting models...")
    try:
        result = subprocess.run([
            'powershell', '-Command', 
            "Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get | ConvertTo-Json"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            models = data.get('models', [])
            print(f"Found {len(models)} models:")
            for model in models:
                print(f"  - {model.get('name', 'Unknown')}")
            
            if not models:
                print("No models available")
                return False
        else:
            print("Failed to get models")
            return False
    except Exception as e:
        print(f"Models error: {e}")
        return False
    
    # Test 4: Generate response
    print("4. Testing response generation...")
    try:
        json_data = {
            "model": "llama3.2",
            "prompt": "Hello, how are you?",
            "stream": False
        }
        
        result = subprocess.run([
            'powershell', '-Command', 
            f"Invoke-RestMethod -Uri 'http://localhost:11434/api/generate' -Method Post -ContentType 'application/json' -Body '{json.dumps(json_data)}'"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            ai_response = response.get('response', '')
            print(f"Response generated: {ai_response[:100]}...")
            return True
        else:
            print(f"Generation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Generation error: {e}")
        return False

def create_simple_test():
    print("Creating simple test...")
    
    test_code = '''
import subprocess
import json

def get_ai_response(prompt):
    """Get AI response using PowerShell"""
    try:
        json_data = {
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
        
        result = subprocess.run([
            'powershell', '-Command', 
            f"Invoke-RestMethod -Uri 'http://localhost:11434/api/generate' -Method Post -ContentType 'application/json' -Body '{json.dumps(json_data)}'"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            return response.get('response', '')
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

# Test
if __name__ == "__main__":
    response = get_ai_response("Hello, how are you?")
    print(f"AI Response: {response}")
'''
    
    with open('simple_ai_test.py', 'w') as f:
        f.write(test_code)
    
    print("Created simple_ai_test.py")

def main():
    if test_ollama():
        print("\nSUCCESS: Ollama is working!")
        create_simple_test()
        print("\nYou can test with:")
        print("  python simple_ai_test.py")
    else:
        print("\nFAILED: Ollama connection issues")
        print("\nTry these solutions:")
        print("1. Restart Ollama")
        print("2. Check firewall settings")
        print("3. Verify port 11434 is available")

if __name__ == "__main__":
    main()
