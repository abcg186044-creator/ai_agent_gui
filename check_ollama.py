#!/usr/bin/env python3
"""
Ollama接続チェックスクリプト
"""

import requests
import subprocess
import sys
import time

def check_ollama_status():
    """Ollamaの状態をチェック"""
    print("🤖 Ollama接続チェックを開始します...")
    
    # 1. Ollamaプロセスの確認
    print("\n1️⃣ Ollamaプロセスの確認...")
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        if 'ollama' in result.stdout.lower():
            print("✅ Ollamaプロセスが実行中です")
        else:
            print("❌ Ollamaプロセスが実行されていません")
            print("💡 Ollamaを起動してください")
            return False
    except Exception as e:
        print(f"❌ プロセス確認エラー: {e}")
        return False
    
    # 2. Ollama API接続チェック
    print("\n2️⃣ Ollama API接続チェック...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama APIに接続できました")
            
            # 利用可能なモデルを表示
            data = response.json()
            models = data.get('models', [])
            if models:
                print(f"📦 利用可能なモデル: {len(models)}個")
                for model in models:
                    print(f"  - {model['name']}")
            else:
                print("⚠️ モデルが見つかりません")
                print("💡 モデルをダウンロードしてください")
        else:
            print(f"❌ Ollama API接続エラー: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama APIに接続できません")
        print("💡 Ollamaが起動しているか確認してください")
        return False
    except Exception as e:
        print(f"❌ APIチェックエラー: {e}")
        return False
    
    # 3. llama3.2モデルの確認
    print("\n3️⃣ llama3.2モデルの確認...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        data = response.json()
        models = data.get('models', [])
        
        llama32_found = False
        for model in models:
            if 'llama3.2' in model['name']:
                print(f"✅ llama3.2モデルが見つかりました: {model['name']}")
                llama32_found = True
        
        if not llama32_found:
            print("❌ llama3.2モデルが見つかりません")
            print("💡 以下のコマンドでモデルをダウンロードしてください:")
            print("   ollama pull llama3.2")
            return False
            
    except Exception as e:
        print(f"❌ モデル確認エラー: {e}")
        return False
    
    print("\n🎉 Ollamaのチェックが完了しました！")
    return True

def start_ollama():
    """Ollamaを起動"""
    print("\n🚀 Ollamaを起動します...")
    try:
        subprocess.Popen(['ollama', 'serve'], shell=True)
        print("✅ Ollamaを起動しました")
        print("⏳ 5秒待機してから再チェックします...")
        time.sleep(5)
        return True
    except FileNotFoundError:
        print("❌ Ollamaが見つかりません")
        print("💡 Ollamaをインストールしてください: https://ollama.com/download")
        return False
    except Exception as e:
        print(f"❌ Ollama起動エラー: {e}")
        return False

def main():
    """メイン処理"""
    if not check_ollama_status():
        print("\n🔄 Ollamaの起動を試みます...")
        if start_ollama():
            check_ollama_status()
        else:
            print("\n❌ Ollamaの起動に失敗しました")
            print("💡 手動でOllamaを起動してください")
            sys.exit(1)
    
    print("\n✅ AI Agent Systemを起動できます！")

if __name__ == "__main__":
    main()
