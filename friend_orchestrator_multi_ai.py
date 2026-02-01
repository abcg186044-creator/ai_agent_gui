#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
親友エージェントによるマルチAIオーケストレーションシステム
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor

from async_ollama_client import AsyncOllamaClient
from robust_multi_ai import RobustMultiAISystem
from coding_task_runner import CodingTaskRunner, TaskPriority, TaskStatus

class TaskStep(Enum):
    """タスクステップ"""
    INITIALIZATION = "initialization"
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    AI_PLANNING = "ai_planning"
    PARALLEL_EXECUTION = "parallel_execution"
    CODE_VALIDATION = "code_validation"
    CODE_INTEGRATION = "code_integration"
    FINALIZATION = "finalization"

@dataclass
class OrchestratedTask:
    """オーケストレーションタスク"""
    id: str
    description: str
    user_request: str
    current_step: TaskStep = TaskStep.INITIALIZATION
    progress: float = 0.0
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    results: Dict[str, Any] = field(default_factory=dict)
    subtasks: List[str] = field(default_factory=list)
    step_progress: Dict[str, float] = field(default_factory=dict)

class FriendOrchestrator:
    """親友エージェントオーケストレーター"""
    
    def __init__(self, max_concurrent_tasks: int = 3):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.ollama_client = None
        self.multi_ai_system = None
        self.task_runner = None
        self.active_tasks: Dict[str, OrchestratedTask] = {}
        self.task_queue = asyncio.Queue()
        self.progress_callbacks: List[Callable] = []
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self.running = False
        self.step_handlers = {}
        self.setup_step_handlers()
    
    def setup_step_handlers(self):
        """ステップハンドラーを設定"""
        self.step_handlers = {
            TaskStep.INITIALIZATION: self.handle_initialization,
            TaskStep.REQUIREMENT_ANALYSIS: self.handle_requirement_analysis,
            TaskStep.AI_PLANNING: self.handle_ai_planning,
            TaskStep.PARALLEL_EXECUTION: self.handle_parallel_execution,
            TaskStep.CODE_VALIDATION: self.handle_code_validation,
            TaskStep.CODE_INTEGRATION: self.handle_code_integration,
            TaskStep.FINALIZATION: self.handle_finalization
        }
    
    def add_progress_callback(self, callback: Callable):
        """進捗コールバックを追加"""
        self.progress_callbacks.append(callback)
    
    def notify_progress(self, task_id: str, step: TaskStep, message: str, progress: float, details: Dict[str, Any] = None):
        """進捗を通知"""
        progress_info = {
            "task_id": task_id,
            "step": step.value,
            "message": message,
            "progress": progress,
            "timestamp": time.time(),
            "details": details or {}
        }
        
        for callback in self.progress_callbacks:
            try:
                callback(progress_info)
            except:
                pass
    
    async def setup(self):
        """システムセットアップ"""
        if self.ollama_client is None:
            self.ollama_client = AsyncOllamaClient(
                ports=[11434, 11435, 11436],
                models=["llama3.2:3b", "llama3.1:8b", "qwen2.5:7b"]
            )
        
        if self.multi_ai_system is None:
            self.multi_ai_system = RobustMultiAISystem(ollama_ports=[11434, 11435, 11436])
        
        if self.task_runner is None:
            self.task_runner = CodingTaskRunner(max_workers=3)
            self.task_runner.add_progress_callback(self.on_task_runner_progress)
    
    def on_task_runner_progress(self, progress_info: Dict[str, Any]):
        """タスクランナー進捗コールバック"""
        # 親タスクに進捗を反映
        for task_id, task in self.active_tasks.items():
            if task.current_step == TaskStep.CODE_VALIDATION or task.current_step == TaskStep.CODE_INTEGRATION:
                task.step_progress[task.current_step.value] = progress_info.get('progress', 0.0)
                self.notify_progress(
                    task_id, 
                    task.current_step, 
                    f"コード処理中: {progress_info.get('message', '')}", 
                    task.progress,
                    {"subtask_progress": progress_info}
                )
    
    async def create_task(self, user_request: str, description: str) -> str:
        """タスクを作成"""
        task_id = f"orch_task_{int(time.time() * 1000)}"
        
        task = OrchestratedTask(
            id=task_id,
            description=description,
            user_request=user_request
        )
        
        self.active_tasks[task_id] = task
        await self.task_queue.put(task_id)
        
        self.notify_progress(task_id, TaskStep.INITIALIZATION, "タスクを作成しました", 0.0)
        return task_id
    
    async def process_task_step(self, task_id: str, step: TaskStep) -> bool:
        """タスクステップを処理"""
        task = self.active_tasks.get(task_id)
        if not task:
            return False
        
        task.current_step = step
        handler = self.step_handlers.get(step)
        
        if handler:
            try:
                self.notify_progress(task_id, step, f"{step.value}を開始します", task.progress)
                result = await handler(task)
                
                if result["success"]:
                    task.results[step.value] = result
                    task.progress += (100.0 / len(TaskStep))
                    self.notify_progress(task_id, step, f"{step.value}が完了しました", task.progress, result)
                    return True
                else:
                    task.error_message = result.get("error", "Unknown error")
                    self.notify_progress(task_id, step, f"{step.value}でエラーが発生", task.progress, {"error": task.error_message})
                    return False
                    
            except Exception as e:
                task.error_message = str(e)
                self.notify_progress(task_id, step, f"{step.value}で例外が発生", task.progress, {"error": str(e)})
                return False
        
        return False
    
    async def handle_initialization(self, task: OrchestratedTask) -> Dict[str, Any]:
        """初期化処理"""
        await self.setup()
        
        return {
            "success": True,
            "message": "システム初期化完了",
            "systems_initialized": ["ollama_client", "multi_ai_system", "task_runner"]
        }
    
    async def handle_requirement_analysis(self, task: OrchestratedTask) -> Dict[str, Any]:
        """要件分析処理"""
        self.notify_progress(task.id, TaskStep.REQUIREMENT_ANALYSIS, "ユーザー要求を分析中...", 10.0)
        
        # 親友エージェントとして要件を分析
        analysis_prompt = f"""
        以下のユーザー要求を分析し、実装計画を作成してください：
        
        要求: {task.user_request}
        説明: {task.description}
        
        分析項目：
        1. 主要機能の特定
        2. 技術要件の抽出
        3. 実装優先順位
        4. 必要なコンポーネント
        5. 予測される課題
        
        JSON形式で回答してください。
        """
        
        async with self.ollama_client as client:
            result = await client.generate_response_async(
                analysis_prompt,
                lambda p: self.notify_progress(task.id, TaskStep.REQUIREMENT_ANALYSIS, p.get('step', ''), 30.0 + p.get('progress', 0) * 0.4)
            )
        
        if result["success"]:
            try:
                analysis = json.loads(result["response"])
                return {
                    "success": True,
                    "analysis": analysis,
                    "model_used": result["model"],
                    "port_used": result["port"]
                }
            except:
                return {
                    "success": True,
                    "analysis": {"raw_response": result["response"]},
                    "model_used": result["model"],
                    "port_used": result["port"]
                }
        else:
            return {"success": False, "error": result.get("error", "Analysis failed")}
    
    async def handle_ai_planning(self, task: OrchestratedTask) -> Dict[str, Any]:
        """AI計画処理"""
        self.notify_progress(task.id, TaskStep.AI_PLANNING, "AI実行計画を作成中...", 40.0)
        
        # 複数AIの実行計画を作成
        analysis = task.results.get(TaskStep.REQUIREMENT_ANALYSIS.value, {})
        
        # サブタスクを生成
        subtasks = []
        
        # 基本実装サブタスク
        subtasks.append({
            "id": f"{task.id}_basic",
            "description": "基本機能の実装",
            "prompt": task.user_request,
            "priority": "high"
        })
        
        # 拡張機能サブタスク
        subtasks.append({
            "id": f"{task.id}_advanced",
            "description": "拡張機能の実装",
            "prompt": f"{task.user_request}\n\n追加機能：エラーハンドリング、テスト、ドキュメント",
            "priority": "medium"
        })
        
        # 最適化サブタスク
        subtasks.append({
            "id": f"{task.id}_optimized",
            "description": "最適化とリファクタリング",
            "prompt": f"{task.user_request}\n\n最適化：パフォーマンス、コード品質、保守性",
            "priority": "low"
        })
        
        task.subtasks = [subtask["id"] for subtask in subtasks]
        
        return {
            "success": True,
            "subtasks": subtasks,
            "total_subtasks": len(subtasks)
        }
    
    async def handle_parallel_execution(self, task: OrchestratedTask) -> Dict[str, Any]:
        """並列実行処理"""
        self.notify_progress(task.id, TaskStep.PARALLEL_EXECUTION, "複数AIで並列実行中...", 50.0)
        
        # マルチAIシステムで並列実行
        planning_result = task.results.get(TaskStep.AI_PLANNING.value, {})
        subtasks = planning_result.get("subtasks", [])
        
        if not subtasks:
            return {"success": False, "error": "No subtasks to execute"}
        
        # 各サブタスクを並列実行
        execution_results = []
        
        def progress_callback_factory(subtask_id):
            def callback(progress_info):
                new_info = progress_info.copy()
                new_info["subtask_id"] = subtask_id
                self.notify_progress(task.id, TaskStep.PARALLEL_EXECUTION, 
                                  f"サブタスク実行中: {progress_info.get('step', '')}", 
                                  50.0 + progress_info.get('progress', 0) * 0.3, new_info)
            return callback
        
        # 並列実行
        tasks = []
        for subtask in subtasks:
            task_coroutine = self.multi_ai_system.generate_response_async(
                subtask["prompt"],
                subtask["description"],
                progress_callback_factory(subtask["id"])
            )
            tasks.append(task_coroutine)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                execution_results.append({
                    "subtask_id": subtasks[i]["id"],
                    "success": False,
                    "error": str(result)
                })
            else:
                execution_results.append({
                    "subtask_id": subtasks[i]["id"],
                    "success": result["success"],
                    "response": result.get("response", ""),
                    "ai_type": result.get("ai_type", ""),
                    "elapsed_time": result.get("elapsed_time", 0)
                })
        
        successful_results = [r for r in execution_results if r["success"]]
        
        return {
            "success": len(successful_results) > 0,
            "execution_results": execution_results,
            "successful_count": len(successful_results),
            "total_count": len(execution_results)
        }
    
    async def handle_code_validation(self, task: OrchestratedTask) -> Dict[str, Any]:
        """コード検証処理"""
        self.notify_progress(task.id, TaskStep.CODE_VALIDATION, "生成コードを検証中...", 70.0)
        
        # 並列実行結果からコードを抽出して検証
        execution_result = task.results.get(TaskStep.PARALLEL_EXECUTION.value, {})
        execution_results = execution_result.get("execution_results", [])
        
        validation_results = []
        
        for result in execution_results:
            if result["success"] and result["response"]:
                # タスクランナーに追加して検証
                task_id = self.task_runner.add_task(
                    description=f"コード検証: {result['subtask_id']}",
                    code=result["response"],
                    file_path=f"validated_{result['subtask_id']}.py",
                    priority=TaskPriority.HIGH
                )
                
                validation_results.append({
                    "subtask_id": result["subtask_id"],
                    "validation_task_id": task_id,
                    "code_length": len(result["response"])
                })
        
        # タスク処理を開始
        self.task_runner.start_processing()
        
        # 検証完了を待機（最大60秒）
        max_wait = 60
        wait_time = 0
        
        while wait_time < max_wait:
            completed_validations = 0
            for validation in validation_results:
                validation_task = self.task_runner.get_task_status(validation["validation_task_id"])
                if validation_task and validation_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    completed_validations += 1
            
            if completed_validations >= len(validation_results):
                break
            
            await asyncio.sleep(2)
            wait_time += 2
        
        # 検証結果を収集
        final_validation_results = []
        for validation in validation_results:
            validation_task = self.task_runner.get_task_status(validation["validation_task_id"])
            if validation_task:
                final_validation_results.append({
                    "subtask_id": validation["subtask_id"],
                    "status": validation_task.status.value,
                    "error_message": validation_task.error_message
                })
        
        successful_validations = [v for v in final_validation_results if v["status"] == "completed"]
        
        return {
            "success": len(successful_validations) > 0,
            "validation_results": final_validation_results,
            "successful_count": len(successful_validations),
            "total_count": len(validation_results)
        }
    
    async def handle_code_integration(self, task: OrchestratedTask) -> Dict[str, Any]:
        """コード統合処理"""
        self.notify_progress(task.id, TaskStep.CODE_INTEGRATION, "コードを統合中...", 85.0)
        
        # 検証されたコードを統合
        validation_result = task.results.get(TaskStep.CODE_VALIDATION.value, {})
        validation_results = validation_result.get("validation_results", [])
        
        integrated_code = ""
        successful_integrations = 0
        
        for validation in validation_results:
            if validation["status"] == "completed":
                # 検証されたコードを取得
                validation_task_id = validation["validation_task_id"]
                validation_task = self.task_runner.get_task_status(validation_task_id)
                
                if validation_task and validation_task.code:
                    integrated_code += f"\n# {validation['subtask_id']}\n"
                    integrated_code += validation_task.code
                    integrated_code += "\n" + "="*50 + "\n"
                    successful_integrations += 1
        
        # 統合コードを最終ファイルとして保存
        if integrated_code:
            final_task_id = self.task_runner.add_task(
                description=f"最終統合コード: {task.description}",
                code=integrated_code,
                file_path=f"final_{task.id}.py",
                priority=TaskPriority.URGENT
            )
            
            return {
                "success": True,
                "integrated_code_length": len(integrated_code),
                "successful_integrations": successful_integrations,
                "final_task_id": final_task_id
            }
        else:
            return {
                "success": False,
                "error": "No validated code to integrate"
            }
    
    async def handle_finalization(self, task: OrchestratedTask) -> Dict[str, Any]:
        """最終処理"""
        self.notify_progress(task.id, TaskStep.FINALIZATION, "タスクを完了しています...", 95.0)
        
        task.completed_at = time.time()
        total_time = task.completed_at - task.created_at
        
        # サマリーを作成
        summary = {
            "task_id": task.id,
            "description": task.description,
            "user_request": task.user_request,
            "total_time": total_time,
            "completed_steps": list(task.results.keys()),
            "successful_subtasks": len([s for s in task.subtasks if any(s in r.get("subtask_id", "") for r in task.results.get(TaskStep.CODE_VALIDATION.value, {}).get("validation_results", []))]),
            "final_status": "completed" if task.error_message is None else "failed"
        }
        
        self.notify_progress(task.id, TaskStep.FINALIZATION, "タスクが完了しました！", 100.0, summary)
        
        return {
            "success": True,
            "summary": summary,
            "total_time": total_time
        }
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """タスクを実行"""
        task = self.active_tasks.get(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}
        
        task.started_at = time.time()
        
        # 各ステップを順次実行
        for step in TaskStep:
            success = await self.process_task_step(task_id, step)
            
            if not success:
                task.error_message = f"Failed at step: {step.value}"
                break
            
            # 少し待機して進捗を表示
            await asyncio.sleep(0.5)
        
        return {
            "success": task.error_message is None,
            "task_id": task_id,
            "total_time": time.time() - task.started_at if task.started_at else 0,
            "error": task.error_message
        }
    
    async def start_orchestration(self):
        """オーケストレーションを開始"""
        self.running = True
        
        async def worker():
            while self.running:
                try:
                    task_id = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                    asyncio.create_task(self.execute_task(task_id))
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"Orchestration worker error: {e}")
        
        # ワーカーを起動
        await worker()
    
    def stop_orchestration(self):
        """オーケストレーションを停止"""
        self.running = False
        if self.task_runner:
            self.task_runner.stop_processing()
    
    def get_task_status(self, task_id: str) -> Optional[OrchestratedTask]:
        """タスクステータスを取得"""
        return self.active_tasks.get(task_id)
    
    def get_all_tasks(self) -> List[OrchestratedTask]:
        """すべてのタスクを取得"""
        return list(self.active_tasks.values())

# テスト用
if __name__ == "__main__":
    async def demo_orchestrator():
        """オーケストレーターデモ"""
        print("🚀 親友エージェントによるマルチAIオーケストレーションデモ")
        print("=" * 60)
        
        def progress_callback(progress_info):
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] 📊 {progress_info['task_id']}: {progress_info['message']} ({progress_info['progress']:.1f}%)")
            if progress_info.get('details'):
                for key, value in progress_info['details'].items():
                    if isinstance(value, dict):
                        print(f"           {key}: {json.dumps(value, ensure_ascii=False, indent=2)[:200]}...")
                    else:
                        print(f"           {key}: {value}")
            print("-" * 50)
        
        orchestrator = FriendOrchestrator(max_concurrent_tasks=2)
        orchestrator.add_progress_callback(progress_callback)
        
        # タスクを作成
        task_id = await orchestrator.create_task(
            user_request="PythonでGUI電卓アプリを作成してください。tkinterを使用し、四則演算ができるようにしてください。",
            description="GUI電卓アプリ開発"
        )
        
        print(f"📝 タスク作成: {task_id}")
        
        # オーケストレーションを開始
        orchestration_task = asyncio.create_task(orchestrator.start_orchestration())
        
        # タスク実行を待機
        result = await orchestrator.execute_task(task_id)
        
        print(f"\n🎯 タスク実行結果:")
        print(f"   成功: {result['success']}")
        print(f"   総時間: {result['total_time']:.2f}秒")
        if result['error']:
            print(f"   エラー: {result['error']}")
        
        # 最終タスクステータス
        final_task = orchestrator.get_task_status(task_id)
        if final_task:
            print(f"\n📋 最終タスク詳細:")
            print(f"   ID: {final_task.id}")
            print(f"   説明: {final_task.description}")
            print(f"   進捗: {final_task.progress:.1f}%")
            print(f"   現在ステップ: {final_task.current_step.value}")
            print(f"   完了ステップ: {list(final_task.results.keys())}")
        
        orchestrator.stop_orchestration()
        print("\n🎉 デモ完了！")
    
    asyncio.run(demo_orchestrator())
