#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
並列ファイル処理システム
"""

import asyncio
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class FileTask:
    """ファイル処理タスク"""
    file_path: str
    task_type: str
    prompt: str
    priority: int = 0
    dependencies: List[str] = None

@dataclass
class FileResult:
    """ファイル処理結果"""
    file_path: str
    task_type: str
    success: bool
    response: str
    elapsed_time: float
    error: Optional[str] = None

class ParallelFileProcessor:
    """並列ファイル処理システム"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.async_ai_system = None
        self._init_ai_system()
    
    def _init_ai_system(self):
        """AIシステムを初期化"""
        try:
            from async_multi_ai import AsyncMultiAICodingSystem
            self.async_ai_system = AsyncMultiAICodingSystem()
        except ImportError:
            print("⚠️ async_multi_aiが見つかりません。フォールバックモードを使用します。")
            self.async_ai_system = None
    
    async def process_files_async(self, tasks: List[FileTask], progress_callback: Optional[Callable] = None) -> Dict[str, FileResult]:
        """非同期で複数ファイルを並列処理"""
        start_time = time.time()
        
        if progress_callback:
            progress_callback({
                "step": "🚀 並列ファイル処理を開始",
                "progress": 0,
                "total_files": len(tasks)
            })
        
        # タスクを優先度順にソート
        tasks.sort(key=lambda t: t.priority, reverse=True)
        
        # 依存関係を解決
        processed_files = set()
        results = {}
        
        while len(processed_files) < len(tasks):
            # 処理可能なタスクを収集
            ready_tasks = []
            for task in tasks:
                if task.file_path not in processed_files:
                    # 依存関係チェック
                    if not task.dependencies or all(dep in processed_files for dep in task.dependencies):
                        ready_tasks.append(task)
            
            if not ready_tasks:
                # 循環依存または未解決の依存関係
                remaining_tasks = [t for t in tasks if t.file_path not in processed_files]
                print(f"⚠️ 依存関係を解決できないタスク: {[t.file_path for t in remaining_tasks]}")
                break
            
            # 並列実行
            semaphore = asyncio.Semaphore(self.max_workers)
            tasks_to_execute = []
            
            for task in ready_tasks:
                task_coroutine = self._process_single_file_async(task, semaphore, progress_callback)
                tasks_to_execute.append(task_coroutine)
            
            # 結果を待機
            completed_results = await asyncio.gather(*tasks_to_execute, return_exceptions=True)
            
            for result in completed_results:
                if isinstance(result, FileResult):
                    results[result.file_path] = result
                    processed_files.add(result.file_path)
                elif isinstance(result, Exception):
                    print(f"❌ タスク実行エラー: {result}")
            
            if progress_callback:
                progress_callback({
                    "step": f"📊 バッチ処理完了 ({len(processed_files)}/{len(tasks)})",
                    "progress": (len(processed_files) / len(tasks)) * 90,
                    "completed_files": len(processed_files)
                })
        
        elapsed = time.time() - start_time
        
        if progress_callback:
            progress_callback({
                "step": "✅ すべてのファイル処理完了",
                "progress": 100,
                "total_time": elapsed,
                "successful_files": sum(1 for r in results.values() if r.success),
                "total_files": len(tasks)
            })
        
        return results
    
    async def _process_single_file_async(self, task: FileTask, semaphore: asyncio.Semaphore, progress_callback: Optional[Callable] = None) -> FileResult:
        """単一ファイルを非同期処理"""
        async with semaphore:
            start_time = time.time()
            
            if progress_callback:
                progress_callback({
                    "step": f"📄 処理中: {task.file_path}",
                    "progress": 0,
                    "current_file": task.file_path,
                    "task_type": task.task_type
                })
            
            try:
                # AIシステムで処理
                if self.async_ai_system:
                    ai_result = await self.async_ai_system.generate_response_async(
                        task.prompt, 
                        task.task_type,
                        lambda info: self._file_progress_callback(info, task.file_path, progress_callback)
                    )
                    
                    if ai_result['success']:
                        response = ai_result['response']
                        
                        # ファイルに保存
                        await self._save_result_to_file(task.file_path, response)
                        
                        elapsed = time.time() - start_time
                        
                        return FileResult(
                            file_path=task.file_path,
                            task_type=task.task_type,
                            success=True,
                            response=response,
                            elapsed_time=elapsed
                        )
                    else:
                        elapsed = time.time() - start_time
                        return FileResult(
                            file_path=task.file_path,
                            task_type=task.task_type,
                            success=False,
                            response="",
                            elapsed_time=elapsed,
                            error=ai_result.get('error', 'AI処理失敗')
                        )
                else:
                    # フォールバック処理
                    response = f"# {task.task_type}\n\n{task.prompt}\n\n// フォールバックモードで生成"
                    await self._save_result_to_file(task.file_path, response)
                    
                    elapsed = time.time() - start_time
                    return FileResult(
                        file_path=task.file_path,
                        task_type=task.task_type,
                        success=True,
                        response=response,
                        elapsed_time=elapsed
                    )
                    
            except Exception as e:
                elapsed = time.time() - start_time
                return FileResult(
                    file_path=task.file_path,
                    task_type=task.task_type,
                    success=False,
                    response="",
                    elapsed_time=elapsed,
                    error=str(e)
                )
    
    def _file_progress_callback(self, progress_info: Dict[str, Any], file_path: str, outer_callback: Optional[Callable] = None):
        """ファイル処理の進捗コールバック"""
        if outer_callback:
            outer_callback({
                "step": f"📄 {file_path}: {progress_info['step']}",
                "progress": progress_info.get('progress', 0),
                "current_file": file_path,
                "ai_type": progress_info.get('ai_type', 'unknown')
            })
    
    async def _save_result_to_file(self, file_path: str, content: str):
        """結果をファイルに保存"""
        # ディレクトリを作成
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 非同期でファイル書き込み
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._write_file_sync, file_path, content)
    
    def _write_file_sync(self, file_path: str, content: str):
        """同期ファイル書き込み"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def process_files_sync(self, tasks: List[FileTask], progress_callback: Optional[Callable] = None) -> Dict[str, FileResult]:
        """同期実行（非同期実行のラッパー）"""
        return asyncio.run(self.process_files_async(tasks, progress_callback))
    
    def create_project_structure(self, project_name: str, tasks: List[FileTask]) -> List[FileTask]:
        """プロジェクト構造を作成"""
        project_tasks = []
        
        for task in tasks:
            # プロジェクト名をプレフィックスとして追加
            file_path = f"{project_name}/{task.file_path}"
            
            project_task = FileTask(
                file_path=file_path,
                task_type=task.task_type,
                prompt=task.prompt,
                priority=task.priority,
                dependencies=task.dependencies
            )
            
            project_tasks.append(project_task)
        
        return project_tasks

# テスト用
if __name__ == "__main__":
    processor = ParallelFileProcessor(max_workers=3)
    
    # テストタスクの定義
    test_tasks = [
        FileTask(
            file_path="src/calculator.py",
            task_type="Python GUI電卓アプリ開発",
            prompt="PythonでGUIをクリックして操作できる電卓アプリを作成してください",
            priority=10
        ),
        FileTask(
            file_path="web/calculator.html",
            task_type="Web電卓アプリ開発",
            prompt="HTMLで電卓アプリを作成してください",
            priority=8
        ),
        FileTask(
            file_path="android/MainActivity.kt",
            task_type="Android電卓アプリ開発",
            prompt="Androidで電卓アプリを開発してください",
            priority=6
        ),
        FileTask(
            file_path="docs/README.md",
            task_type="ドキュメント作成",
            prompt="電卓アプリのREADMEドキュメントを作成してください",
            priority=4,
            dependencies=["src/calculator.py", "web/calculator.html"]
        ),
        FileTask(
            file_path="tests/test_calculator.py",
            task_type="テスト作成",
            prompt="電卓アプリの単体テストを作成してください",
            priority=3,
            dependencies=["src/calculator.py"]
        )
    ]
    
    print("🚀 並列ファイル処理システムテスト開始")
    print("=" * 60)
    
    def progress_callback(progress_info):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] 📊 {progress_info['step']} ({progress_info['progress']:.1f}%)")
        if 'current_file' in progress_info:
            print(f"           📄 ファイル: {progress_info['current_file']}")
        if 'ai_type' in progress_info:
            print(f"           🤖 AI: {progress_info['ai_type']}")
        if 'completed_files' in progress_info:
            print(f"           📁 完了: {progress_info['completed_files']}ファイル")
        print("-" * 30)
    
    start_time = time.time()
    results = processor.process_files_sync(test_tasks, progress_callback)
    elapsed = time.time() - start_time
    
    print(f"\n📊 処理結果サマリー:")
    print(f"✅ 成功: {sum(1 for r in results.values() if r.success)}/{len(results)} ファイル")
    print(f"⏱️ 総時間: {elapsed:.2f}秒")
    
    print(f"\n📋 詳細結果:")
    for file_path, result in results.items():
        status = "✅" if result.success else "❌"
        print(f"   {status} {file_path}: {result.elapsed_time:.2f}秒")
        if not result.success:
            print(f"      エラー: {result.error}")
    
    print(f"\n📁 生成されたファイル:")
    for file_path in results.keys():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   📄 {file_path} ({size} bytes)")
    
    print(f"\n🎉 並列ファイル処理テスト完了！")
