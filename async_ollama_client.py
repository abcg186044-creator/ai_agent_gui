#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
非同期・並列Ollamaクライアント
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import random

class ModelStatus(Enum):
    """モデルステータス"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"

@dataclass
class OllamaInstance:
    """Ollamaインスタンス情報"""
    port: int
    model: str
    status: ModelStatus
    last_used: float
    current_task: Optional[str] = None
    response_time: float = 0.0

class AsyncOllamaClient:
    """非同期Ollamaクライアント"""
    
    def __init__(self, ports: List[int] = None, models: List[str] = None):
        self.ports = ports or [11434, 11435, 11436]
        self.models = models or ["llama3.2:3b", "llama3.1:8b", "qwen2.5:7b"]
        self.instances: Dict[int, OllamaInstance] = {}
        self.session = None
        self.request_queue = asyncio.Queue()
        self.processing = False
        
        # インスタンスを初期化
        self._initialize_instances()
    
    def _initialize_instances(self):
        """Ollamaインスタンスを初期化"""
        for port in self.ports:
            for model in self.models:
                instance_id = f"{port}_{model.replace(':', '_')}"
                self.instances[instance_id] = OllamaInstance(
                    port=port,
                    model=model,
                    status=ModelStatus.IDLE,
                    last_used=0.0
                )
    
    async def __aenter__(self):
        """非同期コンテキストマネージャー"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャー終了"""
        if self.session:
            await self.session.close()
    
    async def get_available_instance(self) -> Optional[OllamaInstance]:
        """利用可能なインスタンスを取得"""
        available_instances = [
            inst for inst in self.instances.values() 
            if inst.status == ModelStatus.IDLE
        ]
        
        if not available_instances:
            return None
        
        # レスポンスタイムが最も速いインスタンスを選択
        return min(available_instances, key=lambda x: x.response_time)
    
    async def generate_response_async(
        self, 
        prompt: str, 
        progress_callback: Optional[Callable] = None,
        preferred_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """非同期で応答を生成"""
        start_time = time.time()
        
        if progress_callback:
            progress_callback({
                "step": "🔍 利用可能なOllamaインスタンスを検索中...",
                "progress": 0
            })
        
        # 利用可能なインスタンスを取得
        instance = await self.get_available_instance()
        
        if not instance:
            if progress_callback:
                progress_callback({
                    "step": "⏳ すべてのインスタンスが使用中。待機中...",
                    "progress": 10
                })
            
            # 少し待って再試行
            await asyncio.sleep(0.5)
            instance = await self.get_available_instance()
            
            if not instance:
                return {
                    "success": False,
                    "error": "利用可能なOllamaインスタンスがありません",
                    "elapsed_time": time.time() - start_time
                }
        
        # インスタンスをビジー状態に設定
        instance.status = ModelStatus.BUSY
        instance.current_task = prompt[:50] + "..."
        
        try:
            if progress_callback:
                progress_callback({
                    "step": f"🔌 ポート {instance.port} の {instance.model} で実行中...",
                    "progress": 20,
                    "port": instance.port,
                    "model": instance.model
                })
            
            # APIリクエストを実行
            response = await self._call_ollama_api(
                instance.port, 
                instance.model, 
                prompt, 
                progress_callback
            )
            
            # レスポンスタイムを記録
            instance.response_time = time.time() - start_time
            instance.last_used = time.time()
            
            if progress_callback:
                progress_callback({
                    "step": f"✅ 応答生成完了 (ポート: {instance.port})",
                    "progress": 100,
                    "port": instance.port,
                    "model": instance.model,
                    "response_time": instance.response_time
                })
            
            return {
                "success": True,
                "response": response,
                "model": instance.model,
                "port": instance.port,
                "elapsed_time": time.time() - start_time
            }
            
        except Exception as e:
            instance.status = ModelStatus.ERROR
            elapsed = time.time() - start_time
            
            if progress_callback:
                progress_callback({
                    "step": f"❌ エラー発生 (ポート: {instance.port}): {str(e)}",
                    "progress": 0,
                    "port": instance.port,
                    "error": str(e)
                })
            
            return {
                "success": False,
                "error": str(e),
                "port": instance.port,
                "elapsed_time": elapsed
            }
        
        finally:
            # インスタンスを解放
            if instance.status == ModelStatus.BUSY:
                instance.status = ModelStatus.IDLE
            instance.current_task = None
    
    async def _call_ollama_api(
        self, 
        port: int, 
        model: str, 
        prompt: str, 
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Ollama APIを呼び出し"""
        url = f"http://localhost:{port}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2048
            }
        }
        
        if progress_callback:
            progress_callback({
                "step": f"📡 APIリクエスト送信中... (ポート: {port})",
                "progress": 40,
                "port": port
            })
        
        async with self.session.post(url, json=payload) as response:
            if response.status != 200:
                raise Exception(f"APIエラー: {response.status}")
            
            if progress_callback:
                progress_callback({
                    "step": f"🤖 モデル応答を待機中... (ポート: {port})",
                    "progress": 70,
                    "port": port
                })
            
            result = await response.json()
            
            if "response" not in result:
                raise Exception("不正なレスポンス形式")
            
            return result["response"]
    
    async def generate_parallel_responses(
        self, 
        prompts: List[str], 
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """並列で複数の応答を生成"""
        if progress_callback:
            progress_callback({
                "step": f"🚀 {len(prompts)}個のタスクを並列実行中...",
                "progress": 0,
                "total_tasks": len(prompts)
            })
        
        # タスクを作成
        tasks = []
        for i, prompt in enumerate(prompts):
            def make_progress_callback(task_id):
                def callback(progress_info):
                    if progress_callback:
                        new_info = progress_info.copy()
                        new_info["task_id"] = task_id
                        progress_callback(new_info)
                return callback
            
            task = asyncio.create_task(
                self.generate_response_async(prompt, make_progress_callback(i))
            )
            tasks.append(task)
        
        # すべてのタスクを実行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 結果を整形
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                formatted_results.append({
                    "success": False,
                    "error": str(result),
                    "task_id": i
                })
            else:
                result["task_id"] = i
                formatted_results.append(result)
        
        if progress_callback:
            progress_callback({
                "step": "✅ すべての並列タスク完了",
                "progress": 100,
                "total_tasks": len(prompts)
            })
        
        return formatted_results
    
    async def get_instance_status(self) -> Dict[str, Any]:
        """インスタンスステータスを取得"""
        status = {
            "total_instances": len(self.instances),
            "idle_instances": len([i for i in self.instances.values() if i.status == ModelStatus.IDLE]),
            "busy_instances": len([i for i in self.instances.values() if i.status == ModelStatus.BUSY]),
            "error_instances": len([i for i in self.instances.values() if i.status == ModelStatus.ERROR]),
            "instances": []
        }
        
        for instance_id, instance in self.instances.items():
            status["instances"].append({
                "id": instance_id,
                "port": instance.port,
                "model": instance.model,
                "status": instance.status.value,
                "current_task": instance.current_task,
                "last_used": instance.last_used,
                "response_time": instance.response_time
            })
        
        return status

# テスト用
if __name__ == "__main__":
    async def test_async_client():
        """非同期クライアントテスト"""
        print("🚀 非同期Ollamaクライアントテスト開始")
        print("=" * 60)
        
        async with AsyncOllamaClient() as client:
            # 単一リクエストテスト
            print("\n📋 単一リクエストテスト:")
            def progress_callback(progress_info):
                print(f"   {progress_info['step']} ({progress_info['progress']:.1f}%)")
            
            result = await client.generate_response_async(
                "Pythonで簡単な電卓アプリを作成してください",
                progress_callback
            )
            
            if result["success"]:
                print(f"✅ 成功: {result['model']} (ポート: {result['port']}, 時間: {result['elapsed_time']:.2f}秒)")
                print(f"📝 応答: {result['response'][:100]}...")
            else:
                print(f"❌ 失敗: {result['error']}")
            
            # 並列リクエストテスト
            print("\n📋 並列リクエストテスト:")
            prompts = [
                "HTMLで電卓アプリを作成してください",
                "Androidで電卓アプリを開発してください",
                "Reactでダッシュボードを作成してください"
            ]
            
            def parallel_progress_callback(progress_info):
                if "task_id" in progress_info:
                    print(f"   タスク{progress_info['task_id']}: {progress_info['step']} ({progress_info['progress']:.1f}%)")
            
            results = await client.generate_parallel_responses(prompts, parallel_progress_callback)
            
            for i, result in enumerate(results):
                if result["success"]:
                    print(f"✅ タスク{i}: {result['model']} (ポート: {result['port']}, 時間: {result['elapsed_time']:.2f}秒)")
                else:
                    print(f"❌ タスク{i}: {result['error']}")
            
            # ステータス確認
            print("\n📊 最終インスタンスステータス:")
            status = await client.get_instance_status()
            print(f"   総インスタンス: {status['total_instances']}")
            print(f"   アイドル: {status['idle_instances']}")
            print(f"   ビジー: {status['busy_instances']}")
            print(f"   エラー: {status['error_instances']}")
        
        print("\n🎉 非同期Ollamaクライアントテスト完了！")
    
    asyncio.run(test_async_client())
