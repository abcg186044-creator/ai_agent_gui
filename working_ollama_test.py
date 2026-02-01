#!/usr/bin/env python3
"""
Working Ollama test with proper escaping
"""

import subprocess
import json
import time

def test_ollama_direct():
    """Test Ollama with proper PowerShell escaping"""
    print("Testing Ollama with proper escaping...")
    
    # Create a proper JSON file
    test_request = {
        "model": "llama3.2",
        "prompt": "Hello, how are you?",
        "stream": False
    }
    
    with open('test_request.json', 'w') as f:
        json.dump(test_request, f)
    
    try:
        # Use file-based approach
        result = subprocess.run([
            'powershell', '-Command', 
            '$body = Get-Content "test_request.json" -Raw; Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -ContentType "application/json" -Body $body'
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode == 0 and result.stdout:
            try:
                response = json.loads(result.stdout)
                ai_response = response.get('response', '')
                print(f"AI Response: {ai_response}")
                return True
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response: {result.stdout}")
                return False
        else:
            print("Command failed")
            return False
            
    except Exception as e:
        print(f"Test error: {e}")
        return False

def test_simple_curl():
    """Test with curl alternative"""
    print("\nTesting with curl alternative...")
    
    try:
        # Try using Invoke-WebRequest
        result = subprocess.run([
            'powershell', '-Command', 
            '$body = "{\\"model\\":\\"llama3.2\\",\\"prompt\\":\\"Hello\\",\\"stream\\":false}"; $response = Invoke-WebRequest -Uri "http://localhost:11434/api/generate" -Method Post -ContentType "application/json" -Body $body; $response.Content'
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        print(f"Response: {result.stdout[:200]}...")
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Curl test error: {e}")
        return False

def create_working_connection():
    """Create working connection class"""
    connection_code = '''
import subprocess
import json
import tempfile
import os

class WorkingOllamaConnection:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.timeout = 30
    
    def generate_response(self, prompt, model="llama3.2"):
        """Generate response using file-based approach"""
        try:
            # Create request data
            request_data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(request_data, f)
                temp_file = f.name
            
            try:
                # Use PowerShell with file
                result = subprocess.run([
                    'powershell', '-Command', 
                    f'$body = Get-Content "{temp_file}" -Raw; Invoke-RestMethod -Uri "{self.base_url}/api/generate" -Method Post -ContentType "application/json" -Body $body'
                ], capture_output=True, text=True, timeout=self.timeout)
                
                if result.returncode == 0:
                    response = json.loads(result.stdout)
                    return response.get('response', '')
                else:
                    return f"Error: {result.stderr}"
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except Exception as e:
            return f"Error: {str(e)}"
    
    def test_connection(self):
        """Test connection"""
        try:
            result = subprocess.run([
                'powershell', '-Command', 
                f'Invoke-RestMethod -Uri "{self.base_url}/api/tags" -Method Get'
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except:
            return False

# Test the connection
if __name__ == "__main__":
    ollama = WorkingOllamaConnection()
    
    if ollama.test_connection():
        print("Connection successful")
        response = ollama.generate_response("Hello, how are you?")
        print(f"Response: {response}")
    else:
        print("Connection failed")
'''
    
    with open('working_ollama.py', 'w') as f:
        f.write(connection_code)
    
    print("Created working_ollama.py")

def main():
    print("Working Ollama Test")
    print("=" * 40)
    
    # Test direct approach
    if test_ollama_direct():
        print("\nDirect test successful!")
    else:
        print("\nDirect test failed")
    
    # Test curl alternative
    if test_simple_curl():
        print("Curl test successful!")
    else:
        print("Curl test failed")
    
    # Create working connection
    create_working_connection()
    
    print("\nTest with:")
    print("  python working_ollama.py")

if __name__ == "__main__":
    main()
