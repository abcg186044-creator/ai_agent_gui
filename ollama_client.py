#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama APIクライアント
"""

import requests
import json
import time
import threading
from queue import Queue

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="llama3.1:8b", timeout=180):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.progress_queue = Queue()
        self.is_generating = False

    def _progress_reporter(self, callback):
        """途中報告を行うスレッド"""
        import time as time_module
        start_time = time_module.time()
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
            elapsed = time_module.time() - start_time
            progress_percent = min((elapsed / self.timeout) * 100, 95)
            callback({
                "step": progress_steps[step],
                "progress": progress_percent,
                "elapsed": elapsed,
                "remaining": max(self.timeout - elapsed, 0)
            })
            step += 1
            time_module.sleep(10)
        if self.is_generating:
            callback({
                "step": "🔄 まだ応答を生成中...もう少々お待ちください",
                "progress": 95,
                "elapsed": time_module.time() - start_time,
                "remaining": max(self.timeout - (time_module.time() - start_time), 0)
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
        """Ollama APIでレスポンスを生成"""
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
            print(f"🔍 プロンプト長: {len(prompt)} 文字")
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
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
        finally:
            self.is_generating = False
