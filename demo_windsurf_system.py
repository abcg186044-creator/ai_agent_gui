#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WindsurfマルチAIシステム デモンストレーション
"""

import asyncio
import time
import threading
from typing import Dict, List, Any

from async_ollama_client import AsyncOllamaClient
from coding_task_runner import CodingTaskRunner, TaskPriority
from local_llm_server import LocalLLMServer

class WindsurfSystemDemo:
    """Windsurfシステムデモ"""
    
    def __init__(self):
        self.ollama_client = None
        self.task_runner = None
        self.local_server = None
        self.progress_log = []
    
    def log_progress(self, progress_info: Dict[str, Any]):
        """進捗をログ記録"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {progress_info.get('task_id', 'SYSTEM')}: {progress_info.get('message', 'No message')} ({progress_info.get('progress', 0):.1f}%)"
        self.progress_log.append(log_entry)
        print(log_entry)
    
    async def setup(self):
        """システムセットアップ"""
        print("🚀 WindsurfマルチAIシステム デモ開始")
        print("=" * 60)
        
        # 1. 非同期Ollamaクライアントをセットアップ
        print("\n📡 1. 非同期Ollamaクライアントをセットアップ...")
        self.ollama_client = AsyncOllamaClient(
            ports=[11434, 11435, 11436],
            models=["llama3.2:3b", "llama3.1:8b"]
        )
        
        # 2. タスクランナーをセットアップ
        print("📋 2. コーディングタスクランナーをセットアップ...")
        self.task_runner = CodingTaskRunner(max_workers=3)
        self.task_runner.add_progress_callback(self.log_progress)
        
        # 3. ローカルLLMサーバーを準備
        print("🖥️ 3. ローカルLLMサーバーを準備...")
        self.local_server = LocalLLMServer(port=11437)
        
        print("✅ セットアップ完了！")
    
    async def demo_parallel_ai_generation(self):
        """並列AI生成デモ"""
        print("\n🤖 デモ1: 並列AIコード生成")
        print("-" * 40)
        
        # 複数のコーディングタスク
        coding_tasks = [
            "PythonでGUI電卓アプリを作成してください。tkinterを使用し、四則演算ができるようにしてください。",
            "HTML/CSS/JavaScriptでレスポンシブな電卓を作成してください。",
            "Androidアプリで電卓を作成してください。Kotlinを使用してください。",
            "Reactで電卓コンポーネントを作成してください。"
        ]
        
        print(f"📝 {len(coding_tasks)}個のコーディングタスクを並列処理...")
        
        # 並列でAI生成を実行
        async with self.ollama_client as client:
            results = await client.generate_parallel_responses(
                coding_tasks,
                self.log_progress
            )
        
        print(f"\n📊 生成結果:")
        successful_count = 0
        for i, result in enumerate(results):
            if result["success"]:
                successful_count += 1
                print(f"   ✅ タスク{i+1}: {result['model']} (ポート: {result['port']}, 時間: {result['elapsed_time']:.2f}秒)")
                print(f"      コード長: {len(result['response'])} 文字")
            else:
                print(f"   ❌ タスク{i+1}: 失敗 - {result['error']}")
        
        print(f"\n🎯 成功率: {successful_count}/{len(coding_tasks)} ({successful_count/len(coding_tasks)*100:.1f}%)")
        
        return results
    
    def demo_task_runner(self, ai_results: List[Dict[str, Any]]):
        """タスクランナーデモ"""
        print("\n📋 デモ2: コーディングタスクランナー")
        print("-" * 40)
        
        # AI生成結果をタスクとして追加
        task_ids = []
        for i, result in enumerate(ai_results):
            if result["success"]:
                task_id = self.task_runner.add_task(
                    description=f"AI生成コード適用 {i+1}",
                    code=result["response"],
                    file_path=f"generated_code_{i+1}.py",
                    priority=TaskPriority.HIGH if i < 2 else TaskPriority.MEDIUM
                )
                task_ids.append(task_id)
                print(f"   📝 タスク追加: {task_id}")
        
        print(f"\n🔄 タスク処理を開始...")
        self.task_runner.start_processing()
        
        # 処理完了を待機
        max_wait_time = 30
        wait_time = 0
        
        while wait_time < max_wait_time:
            completed_tasks = self.task_runner.get_tasks_by_status(TaskStatus.COMPLETED)
            failed_tasks = self.task_runner.get_tasks_by_status(TaskStatus.FAILED)
            
            if len(completed_tasks) + len(failed_tasks) >= len(task_ids):
                break
            
            time.sleep(1)
            wait_time += 1
        
        # 結果表示
        print(f"\n📊 タスク処理結果:")
        for task_id in task_ids:
            task = self.task_runner.get_task_status(task_id)
            if task:
                status_emoji = {
                    "completed": "✅",
                    "failed": "❌",
                    "running": "🔄",
                    "pending": "⏳"
                }.get(task.status.value, "❓")
                
                print(f"   {status_emoji} {task.description}: {task.status.value}")
                if task.error_message:
                    print(f"      エラー: {task.error_message}")
        
        # 統計情報
        stats = self.task_runner.get_stats()
        print(f"\n📈 処理統計:")
        print(f"   総タスク数: {stats['total_tasks']}")
        print(f"   完了: {stats['completed_tasks']}")
        print(f"   失敗: {stats['failed_tasks']}")
        print(f"   キャンセル: {stats['cancelled_tasks']}")
        
        self.task_runner.stop_processing()
    
    def demo_local_server(self):
        """ローカルサーバーデモ"""
        print("\n🖥️ デモ3: ローカルLLMサーバー")
        print("-" * 40)
        
        print("📡 ローカルLLMサーバーをバックグラウンドで起動...")
        
        # バックグラウンドでサーバーを起動
        server_thread = threading.Thread(target=self.local_server.run, daemon=True)
        server_thread.start()
        
        # 少し待ってから接続テスト
        time.sleep(2)
        
        print("✅ ローカルLLMサーバーがポート11435で起動しました")
        print("📝 APIエンドポイント:")
        print("   - GET  http://localhost:11435/")
        print("   - GET  http://localhost:11435/api/tags")
        print("   - POST http://localhost:11435/api/generate")
        
        return server_thread
    
    def show_progress_summary(self):
        """進捗サマリー表示"""
        print("\n📜 進捗ログサマリー")
        print("-" * 40)
        
        if self.progress_log:
            print(f"総ログエントリ: {len(self.progress_log)}")
            
            # 最新の10件を表示
            print("\n最新の進捗:")
            for log in self.progress_log[-10:]:
                print(f"   {log}")
        else:
            print("進捗ログはありません")
    
    async def run_full_demo(self):
        """完全なデモを実行"""
        try:
            # セットアップ
            await self.setup()
            
            # デモ1: 並列AI生成
            ai_results = await self.demo_parallel_ai_generation()
            
            # デモ2: タスクランナー
            self.demo_task_runner(ai_results)
            
            # デモ3: ローカルサーバー
            server_thread = self.demo_local_server()
            
            # 進捗サマリー
            self.show_progress_summary()
            
            print("\n🎉 WindsurfマルチAIシステム デモ完了！")
            print("=" * 60)
            
            # 維持のため少し待機
            print("\n⏳ システムを5秒間維持...")
            time.sleep(5)
            
        except Exception as e:
            print(f"\n❌ デモ実行中にエラーが発生: {e}")
            import traceback
            traceback.print_exc()

# メイン実行
if __name__ == "__main__":
    demo = WindsurfSystemDemo()
    asyncio.run(demo.run_full_demo())
