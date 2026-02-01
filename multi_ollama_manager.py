#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マルチOllamaポート管理システム
"""

import asyncio
import time
import threading
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import queue

class OllamaInstance:
    """Ollamaインスタンス管理"""
    
    def __init__(self, port: int, name: str):
        self.port = port
        self.name = name
        self.is_busy = False
        self.last_used = time.time()
        self.request_queue = queue.Queue()
        self.lock = threading.Lock()
    
    def acquire(self) -> bool:
        """インスタンスを確保"""
        with self.lock:
            if not self.is_busy:
                self.is_busy = True
                self.last_used = time.time()
                return True
            return False
    
    def release(self):
        """インスタンスを解放"""
        with self.lock:
            self.is_busy = False
            self.last_used = time.time()

class MultiOllamaManager:
    """マルチOllamaポート管理システム"""
    
    def __init__(self, base_port: int = 11434, max_instances: int = 3):
        self.base_port = base_port
        self.max_instances = max_instances
        self.instances = []
        self.current_index = 0
        
        # 複数のOllamaインスタンスを初期化
        self._initialize_instances()
    
    def _initialize_instances(self):
        """Ollamaインスタンスを初期化"""
        for i in range(self.max_instances):
            port = self.base_port + i
            instance = OllamaInstance(port, f"ollama_{i}")
            self.instances.append(instance)
    
    def get_available_instance(self) -> Optional[OllamaInstance]:
        """利用可能なインスタンスを取得"""
        # まず空いているインスタンスを探す
        for instance in self.instances:
            if instance.acquire():
                return instance
        
        # すべて Busy の場合は最も古く使用されたインスタンスを待機
        oldest_instance = min(self.instances, key=lambda x: x.last_used)
        if oldest_instance.acquire():
            return oldest_instance
        
        return None
    
    def release_instance(self, instance: OllamaInstance):
        """インスタンスを解放"""
        instance.release()
    
    def get_instance_status(self) -> Dict[str, Any]:
        """インスタンスのステータスを取得"""
        return {
            "total_instances": len(self.instances),
            "busy_instances": sum(1 for i in self.instances if i.is_busy),
            "available_instances": sum(1 for i in self.instances if not i.is_busy),
            "instances": [
                {
                    "name": i.name,
                    "port": i.port,
                    "is_busy": i.is_busy,
                    "last_used": i.last_used
                }
                for i in self.instances
            ]
        }

class SafeOllamaClient:
    """安全なOllamaクライアント"""
    
    def __init__(self, port: int, timeout: int = 60, model: str = "llama3.2:3b"):
        self.port = port
        self.timeout = timeout
        self.model = model
        self.base_url = f"http://localhost:{port}"
    
    async def generate_response_async(self, prompt: str, progress_callback: Optional[Callable] = None) -> str:
        """非同期で応答を生成"""
        try:
            # 実際のOllama API呼び出しをシミュレート
            if progress_callback:
                progress_callback({
                    "step": f"🔍 Ollamaサーバーに接続中... (ポート: {self.port})",
                    "progress": 0,
                    "port": self.port,
                    "model": self.model
                })
            
            await asyncio.sleep(0.1)  # 接続遅延をシミュレート
            
            if progress_callback:
                progress_callback({
                    "step": f"📝 プロンプトを送信中... ({self.model})",
                    "progress": 20,
                    "port": self.port
                })
            
            await asyncio.sleep(0.2)  # 処理遅延をシミュレート
            
            if progress_callback:
                progress_callback({
                    "step": f"🤖 AIモデルが応答を生成中...",
                    "progress": 60,
                    "port": self.port
                })
            
            await asyncio.sleep(0.1)  # 生成遅延をシミュレート
            
            response = self._generate_mock_response(prompt)
            
            if progress_callback:
                progress_callback({
                    "step": f"✅ 応答生成完了 (ポート: {self.port})",
                    "progress": 100,
                    "port": self.port
                })
            
            return response
            
        except Exception as e:
            if progress_callback:
                progress_callback({
                    "step": f"❌ エラー発生 (ポート: {self.port}): {str(e)}",
                    "progress": 0,
                    "port": self.port,
                    "error": str(e)
                })
            return f"Ollama APIエラー (ポート: {self.port}): {str(e)}"
    
    def _generate_mock_response(self, prompt: str) -> str:
        """モック応答を生成"""
        if "電卓" in prompt:
            return f'''# Ollama応答 (ポート: {self.port}, モデル: {self.model})

## Python GUI電卓アプリ

完全な電卓アプリのコードを生成しました。

```python
import tkinter as tk

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("電卓")
        self.setup_ui()
    
    def setup_ui(self):
        # UI実装
        pass

if __name__ == "__main__":
    app = Calculator()
    app.run()
```

## 実行方法
1. コードを保存
2. 実行して起動'''
        
        return f"# Ollama応答 (ポート: {self.port})\n\n{prompt} についての応答を生成しました。"

class AsyncMultiOllamaSystem:
    """非同期マルチOllamaシステム"""
    
    def __init__(self, max_instances: int = 3):
        self.ollama_manager = MultiOllamaManager(max_instances=max_instances)
        self.semaphore = asyncio.Semaphore(max_instances)
    
    async def generate_response_async(self, prompt: str, task_description: str = "", progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """非同期で応答を生成（ポート競合を回避）"""
        start_time = time.time()
        
        if progress_callback:
            progress_callback({
                "step": "🚀 マルチOllamaシステムを起動中...",
                "progress": 0
            })
        
        # 利用可能なインスタンスを取得
        instance = self.ollama_manager.get_available_instance()
        
        if not instance:
            if progress_callback:
                progress_callback({
                    "step": "⏳ すべてのインスタンスが使用中。待機中...",
                    "progress": 10
                })
            
            # 少し待って再試行
            await asyncio.sleep(0.5)
            instance = self.ollama_manager.get_available_instance()
            
            if not instance:
                # それでも取得できない場合はエラー
                elapsed = time.time() - start_time
                return {
                    "success": False,
                    "error": "すべてのOllamaインスタンスがビジー状態です",
                    "elapsed_time": elapsed,
                    "port_status": self.ollama_manager.get_instance_status()
                }
        
        try:
            if progress_callback:
                progress_callback({
                    "step": f"🔌 ポート {instance.port} を使用して処理中...",
                    "progress": 20,
                    "port": instance.port
                })
            
            # クライアントを作成して実行
            client = SafeOllamaClient(
                port=instance.port,
                timeout=60,
                model="llama3.2:3b"
            )
            
            response = await client.generate_response_async(prompt, progress_callback)
            
            elapsed = time.time() - start_time
            
            if progress_callback:
                progress_callback({
                    "step": f"✅ ポート {instance.port} で処理完了",
                    "progress": 100,
                    "port": instance.port,
                    "total_time": elapsed
                })
            
            return {
                "success": True,
                "response": response,
                "elapsed_time": elapsed,
                "port": instance.port,
                "model": client.model,
                "port_status": self.ollama_manager.get_instance_status()
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "elapsed_time": elapsed,
                "port": instance.port if instance else None,
                "port_status": self.ollama_manager.get_instance_status()
            }
        
        finally:
            # インスタンスを解放
            if instance:
                self.ollama_manager.release_instance(instance)
    
    def generate_response_sync(self, prompt: str, task_description: str = "", progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """同期実行"""
        return asyncio.run(self.generate_response_async(prompt, task_description, progress_callback))

# テスト用
if __name__ == "__main__":
    system = AsyncMultiOllamaSystem(max_instances=3)
    
    test_cases = [
        ("PythonでGUIをクリックして操作できる電卓アプリを作成してください", "Python GUI電卓アプリ開発"),
        ("HTMLで電卓アプリを作成してください", "Web電卓アプリ開発"),
        ("Androidで電卓アプリを開発してください", "Android電卓アプリ開発"),
        ("複雑な機械学習システムを設計してください", "機械学習システム設計"),
        ("Reactでダッシュボードを作成してください", "Reactダッシュボード開発")
    ]
    
    print("🚀 マルチOllamaポート管理システムテスト開始")
    print("=" * 60)
    
    async def test_parallel():
        """並列テスト"""
        tasks = []
        
        for i, (prompt, task) in enumerate(test_cases, 1):
            def progress_callback_factory(test_id):
                def progress_callback(progress_info):
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] 📊 テスト{test_id}: {progress_info['step']} ({progress_info['progress']:.1f}%)")
                    if 'port' in progress_info:
                        print(f"           🔌 ポート: {progress_info['port']}")
                    if 'error' in progress_info:
                        print(f"           ❌ エラー: {progress_info['error']}")
                    print("-" * 30)
                return progress_callback
            
            task = asyncio.create_task(
                system.generate_response_async(prompt, task, progress_callback_factory(i))
            )
            tasks.append(task)
        
        # すべてのタスクを並列実行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        print(f"\n📊 並列実行結果:")
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"   テスト{i}: ❌ 例外 - {str(result)}")
            elif result['success']:
                print(f"   テスト{i}: ✅ 成功 (ポート: {result['port']}, 時間: {result['elapsed_time']:.2f}秒)")
            else:
                print(f"   テスト{i}: ❌ 失敗 - {result['error']}")
        
        # 最終ステータス
        print(f"\n📊 最終ポートステータス:")
        status = system.ollama_manager.get_instance_status()
        print(f"   総インスタンス: {status['total_instances']}")
        print(f"   ビジー: {status['busy_instances']}")
        print(f"   利用可能: {status['available_instances']}")
        
        for instance in status['instances']:
            status_text = "🔴 使用中" if instance['is_busy'] else "🟢 利用可能"
            print(f"   {instance['name']} (ポート: {instance['port']}): {status_text}")
    
    # 並列テスト実行
    asyncio.run(test_parallel())
    
    print(f"\n🎉 マルチOllamaポート管理システムテスト完了！")
