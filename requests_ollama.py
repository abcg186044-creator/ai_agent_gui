
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
