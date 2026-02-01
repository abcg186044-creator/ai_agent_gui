#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama APIクライアント（240秒タイムアウト + 途中報告機能）
"""

import requests
import json
import time
import threading
from queue import Queue

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="llama3.1:8b", timeout=240):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.progress_queue = Queue()
        self.is_generating = False
        
    def _progress_reporter(self, callback):
        """途中報告を行うスレッド"""
        start_time = time.time()
        progress_steps = [
            "🔍 Ollamaサーバーに接続中...",
            "📝 プロンプトを送信中...",
            "🤖 AIモデルが思考を開始...",
            "🧠 言語モデルが応答を生成中...",
            "⚡ レスポンスを整形中...",
            "✅ 応答生成完了"
        ]
        
        step = 0
        while self.is_generating and step < len(progress_steps):
            elapsed = time.time() - start_time
            progress_percent = min((elapsed / self.timeout) * 100, 95)
            
            callback({
                "step": progress_steps[step],
                "progress": progress_percent,
                "elapsed": elapsed,
                "remaining": max(self.timeout - elapsed, 0)
            })
            
            step += 1
            time.sleep(10)  # 10秒ごとに報告
        
        # 最終報告
        if self.is_generating:
            callback({
                "step": "🔄 まだ応答を生成中...もう少々お待ちください",
                "progress": 95,
                "elapsed": time.time() - start_time,
                "remaining": max(self.timeout - (time.time() - start_time), 0)
            })
    
    def generate_response(self, prompt, max_tokens=1000, progress_callback=None):
        """Ollama APIでレスポンスを生成（途中報告付き）"""
        self.is_generating = True
        progress_thread = None
        
        if progress_callback:
            # 途中報告スレッドを開始
            progress_thread = threading.Thread(
                target=self._progress_reporter, 
                args=(progress_callback,),
                daemon=True
            )
            progress_thread.start()
        
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
            
            self.is_generating = False
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "応答がありません")
                
                # 最終報告
                if progress_callback:
                    progress_callback({
                        "step": "✅ 応答生成完了",
                        "progress": 100,
                        "elapsed": elapsed_time,
                        "remaining": 0,
                        "response_length": len(response_text)
                    })
                
                return response_text
            else:
                print(f"❌ APIエラー: {response.status_code}")
                return f"APIエラー: {response.status_code}"
                
        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            print(f"❌ Ollama APIタイムアウト（{self.timeout}秒）")
            self.is_generating = False
            
            if progress_callback:
                progress_callback({
                    "step": f"❌ タイムアウト発生（{self.timeout}秒）",
                    "progress": 100,
                    "elapsed": elapsed_time,
                    "remaining": 0,
                    "error": "timeout"
                })
            
            return f"AI応答がタイムアウトしました（{self.timeout}秒）。時間を置いて再度お試しください。"
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ Ollama APIエラー: {str(e)}")
            self.is_generating = False
            
            if progress_callback:
                progress_callback({
                    "step": f"❌ エラー発生: {str(e)}",
                    "progress": 100,
                    "elapsed": elapsed_time,
                    "remaining": 0,
                    "error": str(e)
                })
            
            return f"API呼び出しエラー: {str(e)}"
        finally:
            self.is_generating = False

# テスト用
if __name__ == "__main__":
    def progress_callback(progress_info):
        print(f"📊 {progress_info['step']} ({progress_info['progress']:.1f}%)")
        print(f"   ⏱️ 経過時間: {progress_info['elapsed']:.1f}秒")
        print(f"   ⏳ 残り時間: {progress_info['remaining']:.1f}秒")
        print("-" * 50)
    
    client = OllamaClient(timeout=240)
    
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
    
    print("🚀 240秒タイムアウト + 途中報告機能で電卓アプリ作成開始")
    print("=" * 60)
    
    response = client.generate_response(prompt, progress_callback=progress_callback)
    
    print("\n🔧 生成されたコード:")
    print("-" * 40)
    print(response)
    
    # ファイルに保存
    with open("calculator_with_progress.py", "w", encoding="utf-8") as f:
        f.write(response)
    
    print("\n💾 コードを calculator_with_progress.py に保存しました")
    
    if response and not response.startswith("AI応答がタイムアウトしました"):
        print("✅ 電卓アプリの生成に成功しました！")
        print("🚀 実行方法: python calculator_with_progress.py")
    else:
        print("❌ 電卓アプリの生成に失敗しました")
