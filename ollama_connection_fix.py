#!/usr/bin/env python3
"""
Fixed Ollama connection for AI Agent System
"""

import requests
import subprocess
import json
import time

class OllamaConnection:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.timeout = 30
    
    def test_connection(self):
        """Test Ollama connection"""
        try:
            # Use PowerShell for reliable connection
            result = subprocess.run([
                'powershell', '-Command', 
                f"Invoke-RestMethod -Uri '{self.base_url}/api/tags' -Method Get -TimeoutSec {self.timeout}"
            ], capture_output=True, text=True, timeout=self.timeout)
            
            if result.returncode == 0:
                return True, "Connection successful"
            else:
                return False, f"PowerShell error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Connection timeout"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def get_models(self):
        """Get available models"""
        try:
            result = subprocess.run([
                'powershell', '-Command', 
                f"Invoke-RestMethod -Uri '{self.base_url}/api/tags' -Method Get -TimeoutSec {self.timeout} | ConvertTo-Json"
            ], capture_output=True, text=True, timeout=self.timeout)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('models', [])
            else:
                return []
                
        except Exception as e:
            print(f"Error getting models: {e}")
            return []
    
    def generate_response(self, prompt, model="llama3.2"):
        """Generate AI response"""
        try:
            json_data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            result = subprocess.run([
                'powershell', '-Command', 
                f"Invoke-RestMethod -Uri '{self.base_url}/api/generate' -Method Post -ContentType 'application/json' -Body '{json.dumps(json_data)}' -TimeoutSec {self.timeout}"
            ], capture_output=True, text=True, timeout=self.timeout)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                return response.get('response', ''), None
            else:
                return None, f"Generation error: {result.stderr}"
                
        except Exception as e:
            return None, f"Generation error: {str(e)}"

def test_ollama_complete():
    """Complete Ollama test"""
    print("Testing Ollama Connection...")
    print("=" * 50)
    
    ollama = OllamaConnection()
    
    # Test connection
    print("1. Testing connection...")
    success, message = ollama.test_connection()
    if success:
        print("✅ Connection successful")
    else:
        print(f"❌ Connection failed: {message}")
        return False
    
    # Test models
    print("\n2. Getting models...")
    models = ollama.get_models()
    if models:
        print(f"✅ Found {len(models)} models:")
        for model in models:
            print(f"   - {model.get('name', 'Unknown')}")
    else:
        print("❌ No models found")
        return False
    
    # Test generation
    print("\n3. Testing response generation...")
    response, error = ollama.generate_response("Hello, how are you?")
    if response:
        print(f"✅ Response generated: {response[:100]}...")
        return True
    else:
        print(f"❌ Generation failed: {error}")
        return False

def create_fixed_agent():
    """Create fixed AI agent with new connection"""
    fixed_code = '''
import streamlit as st
import requests
import subprocess
import json
import time

class FixedOllamaConnection:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.timeout = 30
    
    def generate_response(self, prompt, model="llama3.2"):
        """Generate AI response using PowerShell"""
        try:
            json_data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            result = subprocess.run([
                'powershell', '-Command', 
                f"Invoke-RestMethod -Uri '{self.base_url}/api/generate' -Method Post -ContentType 'application/json' -Body '{json.dumps(json_data)}' -TimeoutSec {self.timeout}"
            ], capture_output=True, text=True, timeout=self.timeout)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                return response.get('response', '')
            else:
                return f"Error: {result.stderr}"
                
        except Exception as e:
            return f"Error: {str(e)}"

class FixedAIAgent:
    def __init__(self):
        self.ollama = FixedOllamaConnection()
    
    def generate_response(self, prompt):
        """Generate AI response"""
        return self.ollama.generate_response(prompt)

# Use this in your main app
def main():
    st.title("Fixed AI Agent System")
    
    if 'agent' not in st.session_state:
        st.session_state.agent = FixedAIAgent()
    
    user_input = st.text_area("Enter your message:")
    
    if st.button("Send"):
        if user_input:
            with st.spinner("Generating response..."):
                response = st.session_state.agent.generate_response(user_input)
                st.write("AI Response:")
                st.write(response)

if __name__ == "__main__":
    main()
'''
    
    with open('fixed_ai_agent.py', 'w', encoding='utf-8') as f:
        f.write(fixed_code)
    
    print("✅ Fixed AI agent created: fixed_ai_agent.py")

def main():
    """Main function"""
    print("Ollama Connection Fix Tool")
    print("=" * 50)
    
    # Test current connection
    if test_ollama_complete():
        print("\n✅ Ollama is working correctly!")
        
        # Create fixed agent
        create_fixed_agent()
        
        print("\n🚀 You can now run:")
        print("   start_ai.bat (original)")
        print("   streamlit run fixed_ai_agent.py (test)")
        
    else:
        print("\n❌ Ollama connection issues found")
        print("\n🔧 Solutions:")
        print("1. Restart Ollama")
        print("2. Check firewall")
        print("3. Verify port 11434")
        
        # Try to fix
        print("\n🔄 Attempting to fix...")
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], capture_output=True)
            subprocess.run(['taskkill', '/F', '/IM', 'ollama app.exe'], capture_output=True)
            time.sleep(2)
            subprocess.Popen(['ollama', 'serve'], shell=True)
            print("✅ Ollama restarted")
            time.sleep(5)
            
            if test_ollama_complete():
                print("✅ Fixed successfully!")
                create_fixed_agent()
            else:
                print("❌ Still having issues")
                
        except Exception as e:
            print(f"❌ Fix failed: {e}")

if __name__ == "__main__":
    main()
