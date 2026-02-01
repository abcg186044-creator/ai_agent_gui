
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
