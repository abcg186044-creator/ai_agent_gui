#!/usr/bin/env python3
"""
Ollama接続修正スクリプト
"""

import requests
import subprocess
import time
import sys

def test_ollama_connection():
    """Ollama接続をテスト"""
    print("🔍 Ollama接続テスト...")
    
    try:
        # PowerShellでcurlを試す
        result = subprocess.run([
            'powershell', '-Command', 
            "Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ PowerShell接続成功")
            print(f"応答: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ PowerShell接続失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 接続テストエラー: {e}")
        return False

def fix_ollama_connection():
    """Ollama接続を修正"""
    print("🔧 Ollama接続を修正します...")
    
    # 1. Ollamaプロセスの確認
    print("\n1️⃣ Ollamaプロセス確認:")
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        if 'ollama' in result.stdout.lower():
            print("✅ Ollamaプロセスが実行中")
            
            # プロセス情報を取得
            lines = result.stdout.split('\n')
            for line in lines:
                if 'ollama' in line.lower():
                    print(f"   {line.strip()}")
        else:
            print("❌ Ollamaプロセスが実行されていません")
            return False
    except Exception as e:
        print(f"❌ プロセス確認エラー: {e}")
        return False
    
    # 2. API接続テスト
    print("\n2️⃣ API接続テスト:")
    if not test_ollama_connection():
        print("❌ API接続に失敗しました")
        return False
    
    # 3. モデル確認
    print("\n3️⃣ モデル確認:")
    try:
        result = subprocess.run([
            'powershell', '-Command', 
            "Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get | ConvertTo-Json"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ モデルリスト取得成功")
            if 'llama3.2' in result.stdout:
                print("✅ llama3.2モデルが見つかりました")
            else:
                print("⚠️ llama3.2モデルが見つかりません")
        else:
            print(f"❌ モデルリスト取得失敗: {result.stderr}")
            
    except Exception as e:
        print(f"❌ モデル確認エラー: {e}")
    
    return True

def create_fixed_connection():
    """修正された接続方法を作成"""
    print("\n🔧 修正された接続方法を作成...")
    
    # 修正版接続コード
    fixed_code = '''
import requests
import subprocess
import json

def get_ollama_models():
    """Ollamaモデルを取得（修正版）"""
    try:
        # PowerShellを使用して接続
        result = subprocess.run([
            'powershell', '-Command', 
            "Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get | ConvertTo-Json"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get('models', [])
        else:
            return []
            
    except Exception as e:
        print(f"Ollama接続エラー: {e}")
        return []

def test_ollama_response(prompt):
    """Ollama応答テスト（修正版）"""
    try:
        # PowerShellを使用してPOSTリクエスト
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
            return f"エラー: {result.stderr}"
            
    except Exception as e:
        return f"エラー: {str(e)}"
'''
    
    with open('ollama_connection_fixed.py', 'w', encoding='utf-8') as f:
        f.write(fixed_code)
    
    print("✅ 修正版接続コードを作成しました: ollama_connection_fixed.py")

def main():
    """メイン処理"""
    print("🔧 Ollama接続修正ツール")
    print("=" * 50)
    
    if fix_ollama_connection():
        print("\n✅ Ollama接続は正常です")
        
        # 修正版接続コードを作成
        create_fixed_connection()
        
        print("\n🚀 AI Agent Systemを起動できます")
        print("💡 start_ai.bat を実行してください")
        
    else:
        print("\n❌ Ollama接続に問題があります")
        print("\n🔧 対処方法:")
        print("1. Ollamaを再起動")
        print("2. ファイアウォールを確認")
        print("3. ポート11434が使用可能か確認")
        
        # Ollama再起動を試行
        print("\n🔄 Ollama再起動を試行します...")
        try:
            # Ollamaプロセスを終了
            subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], capture_output=True)
            subprocess.run(['taskkill', '/F', '/IM', 'ollama app.exe'], capture_output=True)
            
            time.sleep(2)
            
            # Ollamaを再起動
            subprocess.Popen(['ollama', 'serve'], shell=True)
            print("✅ Ollamaを再起動しました")
            print("⏳ 5秒待機してから再試行します...")
            
            time.sleep(5)
            
            if fix_ollama_connection():
                print("✅ 再起動後、接続に成功しました")
            else:
                print("❌ 再起動後も接続に失敗しました")
                
        except Exception as e:
            print(f"❌ 再起動エラー: {e}")

if __name__ == "__main__":
    main()
