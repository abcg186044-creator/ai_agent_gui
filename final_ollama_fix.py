#!/usr/bin/env python3
"""
Final Ollama fix - parse PowerShell response properly
"""

import subprocess
import json
import re

def parse_powershell_response(response_text):
    """Parse PowerShell response to extract JSON"""
    try:
        # PowerShell returns formatted text, we need to extract the JSON part
        lines = response_text.strip().split('\n')
        
        # Find the start of JSON-like content
        json_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('model') or line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start is None:
            return None
        
        # Collect all lines until we have a complete response
        json_lines = []
        for line in lines[json_start:]:
            json_lines.append(line)
            if 'done' in line and 'True' in line:
                break
        
        # Convert PowerShell format to JSON
        json_text = '\n'.join(json_lines)
        
        # Parse key-value pairs
        data = {}
        for line in json_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Handle different value types
                if value.startswith('{') or value.startswith('['):
                    # JSON value
                    try:
                        data[key] = json.loads(value)
                    except:
                        data[key] = value
                elif value.lower() in ['true', 'false']:
                    data[key] = value.lower() == 'true'
                elif value.isdigit():
                    data[key] = int(value)
                else:
                    # String value - remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    data[key] = value
        
        return data
        
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def test_fixed_ollama():
    """Test fixed Ollama connection"""
    print("Testing Fixed Ollama Connection")
    print("=" * 40)
    
    try:
        # Test with PowerShell
        result = subprocess.run([
            'powershell', '-Command', 
            '$body = "{\\"model\\":\\"llama3.2\\",\\"prompt\\":\\"Hello\\",\\"stream\\":false}"; $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -ContentType "application/json" -Body $body; $response'
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            # Parse the response
            parsed = parse_powershell_response(result.stdout)
            
            if parsed and 'response' in parsed:
                print(f"SUCCESS: {parsed['response']}")
                return True
            else:
                print("Failed to parse response")
                print(f"Raw response: {result.stdout}")
                return False
        else:
            print(f"Command failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Test error: {e}")
        return False

def create_final_ollama_class():
    """Create final working Ollama class"""
    class_code = '''
import subprocess
import json
import re

def parse_powershell_response(response_text):
    """Parse PowerShell response to extract JSON"""
    try:
        lines = response_text.strip().split('\\n')
        
        # Find the start of response
        json_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('model') or line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start is None:
            return None
        
        # Collect response lines
        json_lines = []
        for line in lines[json_start:]:
            json_lines.append(line)
            if 'done' in line and 'True' in line:
                break
        
        # Parse key-value pairs
        data = {}
        for line in json_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if value.startswith('{') or value.startswith('['):
                    try:
                        data[key] = json.loads(value)
                    except:
                        data[key] = value
                elif value.lower() in ['true', 'false']:
                    data[key] = value.lower() == 'true'
                elif value.isdigit():
                    data[key] = int(value)
                else:
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    data[key] = value
        
        return data
        
    except Exception as e:
        print(f"Parse error: {e}")
        return None

class FinalOllamaConnection:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.timeout = 30
    
    def generate_response(self, prompt, model="llama3.2"):
        """Generate response using PowerShell"""
        try:
            # Escape the prompt properly
            escaped_prompt = prompt.replace('"', '\\"').replace("'", "\\'")
            
            # Create PowerShell command
            ps_command = f'$body = "{{\\"model\\":\\"{model}\\",\\"prompt\\":\\"{escaped_prompt}\\",\\"stream\\":false}}"; $response = Invoke-RestMethod -Uri "{self.base_url}/api/generate" -Method Post -ContentType "application/json" -Body $body; $response'
            
            result = subprocess.run([
                'powershell', '-Command', ps_command
            ], capture_output=True, text=True, timeout=self.timeout)
            
            if result.returncode == 0:
                parsed = parse_powershell_response(result.stdout)
                if parsed and 'response' in parsed:
                    return parsed['response']
                else:
                    return f"Parse error: {result.stdout}"
            else:
                return f"Command error: {result.stderr}"
                
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

# Test
if __name__ == "__main__":
    ollama = FinalOllamaConnection()
    
    if ollama.test_connection():
        print("Connection successful")
        response = ollama.generate_response("Hello, how are you?")
        print(f"Response: {response}")
    else:
        print("Connection failed")
'''
    
    with open('final_ollama.py', 'w') as f:
        f.write(class_code)
    
    print("Created final_ollama.py")

def main():
    if test_fixed_ollama():
        print("\nSUCCESS: Fixed Ollama connection!")
        create_final_ollama_class()
        print("\nTest with:")
        print("  python final_ollama.py")
    else:
        print("\nFAILED: Still having issues")

if __name__ == "__main__":
    main()
