#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拡張版Ollamaクライアント（60秒タイムアウト）
"""

import requests
import json
import time

class ExtendedOllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="llama3.1:8b", timeout=60):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout  # 60秒に延長
        
    def generate_response(self, prompt, max_tokens=1000):
        """Ollama APIでレスポンスを生成（60秒タイムアウト）"""
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": max_tokens
                }
            }
            
            print(f"🔍 Ollama API呼び出し: {self.base_url}")
            print(f"🔍 モデル: {self.model}")
            print(f"🔍 タイムアウト: {self.timeout}秒")
            print(f"🔍 プロンプト長: {len(prompt)} 文字")
            
            start_time = time.time()
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            elapsed_time = time.time() - start_time
            print(f"⏱️ 応答時間: {elapsed_time:.2f}秒")
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "応答がありません")
            else:
                print(f"❌ APIエラー: {response.status_code}")
                return f"APIエラー: {response.status_code}"
                
        except requests.exceptions.Timeout:
            print(f"❌ Ollama APIタイムアウト（{self.timeout}秒）")
            return f"AI応答がタイムアウトしました（{self.timeout}秒）。時間を置いて再度お試しください。"
        except Exception as e:
            print(f"❌ Ollama APIエラー: {str(e)}")
            return f"API呼び出しエラー: {str(e)}"

# テスト用
if __name__ == "__main__":
    client = ExtendedOllamaClient()
    
    # 電卓アプリ作成リクエスト
    prompt = """PythonでGUIをクリックして操作できる電卓アプリを作成してください。
Tkinterを使用して、基本的な四則演算ができる完全なコードを生成してください。
以下の機能を含めてください：
1. 数字ボタン（0-9）
2. 演算子ボタン（+、-、*、/）
3. イコールボタン
4. クリアボタン
5. 小数点ボタン
6. 表示画面
7. エラー処理
8. キーボード入力対応
完全な実行可能なコードを生成してください。"""
    
    print("🚀 拡張版Ollamaクライアントで電卓アプリ作成開始")
    print("=" * 60)
    
    response = client.generate_response(prompt)
    
    print("\n🔧 生成されたコード:")
    print("-" * 40)
    print(response)
    
    # ファイルに保存
    with open("extended_calculator_app.py", "w", encoding="utf-8") as f:
        f.write(response)
    
    print("\n💾 コードを extended_calculator_app.py に保存しました")
