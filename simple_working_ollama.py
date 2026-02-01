#!/usr/bin/env python3
"""
Simple working Ollama connection using requests
"""

import requests
import json
import time

def test_requests_connection():
    """Test connection using requests library"""
    print("Testing with requests library...")
    
    try:
        # Test basic connection
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            print("Basic connection successful")
            
            # Get models
            data = response.json()
            models = data.get('models', [])
            print(f"Found {len(models)} models")
            
            # Test generation
            generation_data = {
                "model": "llama3.2",
                "prompt": "Hello, how are you?",
                "stream": False
            }
            
            gen_response = requests.post(
                "http://localhost:11434/api/generate",
                json=generation_data,
                timeout=30
            )
            
            if gen_response.status_code == 200:
                result = gen_response.json()
                ai_response = result.get('response', '')
                print(f"AI Response: {ai_response}")
                return True
            else:
                print(f"Generation failed: {gen_response.status_code}")
                return False
        else:
            print(f"Connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Requests error: {e}")
        return False

def create_requests_ollama():
    """Create Ollama class using requests"""
    class_code = '''
import requests
import json

class RequestsOllamaConnection:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.timeout = 30
    
    def generate_response(self, prompt, model="llama3.2"):
        """Generate response using requests"""
        try:
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def test_connection(self):
        """Test connection"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            return response.status_code == 200
        except:
            return False

# Test
if __name__ == "__main__":
    ollama = RequestsOllamaConnection()
    
    if ollama.test_connection():
        print("Connection successful")
        response = ollama.generate_response("Hello, how are you?")
        print(f"Response: {response}")
    else:
        print("Connection failed")
'''
    
    with open('requests_ollama.py', 'w') as f:
        f.write(class_code)
    
    print("Created requests_ollama.py")

def main():
    print("Simple Working Ollama Test")
    print("=" * 40)
    
    if test_requests_connection():
        print("\nSUCCESS: requests library works!")
        create_requests_ollama()
        print("\nTest with:")
        print("  python requests_ollama.py")
        
        print("\nTo fix your smart_voice_agent.py:")
        print("1. Replace the Ollama connection with requests_ollama.py")
        print("2. Or run: streamlit run requests_ollama.py")
    else:
        print("\nFAILED: requests library also failed")

if __name__ == "__main__":
    main()
