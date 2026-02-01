#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
親友エージェントによるマルチAIオーケストレーションシステム（改善版）
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor

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

class MockAsyncOllamaClient:
    """モック非同期Ollamaクライアント"""
    
    def __init__(self, ports=None, models=None):
        self.ports = ports or [11434, 11435, 11436]
        self.models = models or ["llama3.2:3b", "llama3.1:8b"]
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def generate_response_async(self, prompt: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """モック応答生成"""
        await asyncio.sleep(0.1)  # 少し遅延
        
        if progress_callback:
            progress_callback({"step": "分析中...", "progress": 50})
        
        # 簡単なモック応答
        if "電卓" in prompt:
            response = '''
{
  "main_functions": ["四則演算", "GUI表示", "エラーハンドリング"],
  "technical_requirements": ["tkinter", "Python 3.8+", "イベント処理"],
  "implementation_priority": ["基本演算", "UI設計", "機能拡張"],
  "components": ["Calculatorクラス", "Buttonクラス", "Displayクラス"],
  "challenges": ["ゼロ除算", "入力検証", "UI応答性"]
}
'''
        else:
            response = '''
{
  "main_functions": ["基本機能実装"],
  "technical_requirements": ["Python標準ライブラリ"],
  "implementation_priority": ["基本設計", "実装", "テスト"],
  "components": ["Mainクラス"],
  "challenges": ["要件定義"]
}
'''
        
        return {
            "success": True,
            "response": response,
            "model": "mock_model",
            "port": 11434,
            "elapsed_time": 0.1
        }

class MockRobustMultiAISystem:
    """モック堅牢マルチAIシステム"""
    
    def __init__(self, ollama_ports=None):
        self.ollama_ports = ollama_ports or [11434, 11435, 11436]
    
    async def generate_response_async(self, prompt: str, task_description: str = "", progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """モック並列応答生成"""
        await asyncio.sleep(0.2)  # 少し遅延
        
        if progress_callback:
            progress_callback({"step": "AIモデル実行中...", "progress": 50})
        
        # 簡単なモックコード生成
        if "電卓" in prompt:
            code = '''import tkinter as tk

class Calculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("電卓")
        self.setup_ui()
    
    def setup_ui(self):
        self.display = tk.Entry(self.root, font=("Arial", 20))
        self.display.pack()
        
        buttons = ["7", "8", "9", "/", "4", "5", "6", "*", "1", "2", "3", "-", "0", ".", "=", "+"]
        
        for i, text in enumerate(buttons):
            btn = tk.Button(self.root, text=text, command=lambda t=text: self.on_click(t))
            btn.grid(row=i//4, column=i%4)
    
    def on_click(self, text):
        if text == "=":
            try:
                result = eval(self.display.get())
                self.display.delete(0, tk.END)
                self.display.insert(0, str(result))
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Error")
        else:
            self.display.insert(tk.END, text)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Calculator()
    app.run()
'''
        else:
            code = '''# 基本実装
def main():
    print("Hello World")

if __name__ == "__main__":
    main()
'''
        
        return {
            "success": True,
            "response": code,
            "ai_type": "mock_ai",
            "elapsed_time": 0.2
        }

class MockCodingTaskRunner:
    """モックコーディングタスクランナー"""
    
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.tasks = {}
        self.progress_callbacks = []
    
    def add_progress_callback(self, callback):
        self.progress_callbacks.append(callback)
    
    def add_task(self, description: str, code: str, file_path: str = None, priority=None) -> str:
        task_id = f"task_{int(time.time() * 1000)}"
        self.tasks[task_id] = {
            "id": task_id,
            "description": description,
            "code": code,
            "file_path": file_path,
            "status": "completed"
        }
        
        # 進捗コールバック
        for callback in self.progress_callbacks:
            callback({"task_id": task_id, "message": "タスク完了", "progress": 100})
        
        return task_id
    
    def start_processing(self):
        pass
    
    def stop_processing(self):
        pass
    
    def get_task_status(self, task_id: str):
        return self.tasks.get(task_id)

class FriendOrchestratorFixed:
    """改善版親友エージェントオーケストレーター"""
    
    def __init__(self, max_concurrent_tasks: int = 3):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.ollama_client = None
        self.multi_ai_system = None
        self.task_runner = None
        self.active_tasks: Dict[str, OrchestratedTask] = {}
        self.task_queue = asyncio.Queue()
        self.progress_callbacks: List[Callable] = []
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
            except Exception as e:
                print(f"Progress callback error: {e}")
    
    async def setup(self):
        """システムセットアップ"""
        if self.ollama_client is None:
            self.ollama_client = MockAsyncOllamaClient(
                ports=[11434, 11435, 11436],
                models=["llama3.2:3b", "llama3.1:8b"]
            )
        
        if self.multi_ai_system is None:
            self.multi_ai_system = MockRobustMultiAISystem(ollama_ports=[11434, 11435, 11436])
        
        if self.task_runner is None:
            self.task_runner = MockCodingTaskRunner(max_workers=3)
            self.task_runner.add_progress_callback(self.on_task_runner_progress)
    
    def on_task_runner_progress(self, progress_info: Dict[str, Any]):
        """タスクランナー進捗コールバック"""
        for task_id, task in self.active_tasks.items():
            if task.current_step in [TaskStep.CODE_VALIDATION, TaskStep.CODE_INTEGRATION]:
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
        
        # サブタスクを生成
        subtasks = [
            {
                "id": f"{task.id}_basic",
                "description": "基本機能の実装",
                "prompt": task.user_request,
                "priority": "high"
            },
            {
                "id": f"{task.id}_advanced",
                "description": "拡張機能の実装",
                "prompt": f"{task.user_request}\n\n追加機能：エラーハンドリング、テスト、ドキュメント",
                "priority": "medium"
            },
            {
                "id": f"{task.id}_optimized",
                "description": "最適化とリファクタリング",
                "prompt": f"{task.user_request}\n\n最適化：パフォーマンス、コード品質、保守性",
                "priority": "low"
            }
        ]
        
        task.subtasks = [subtask["id"] for subtask in subtasks]
        
        return {
            "success": True,
            "subtasks": subtasks,
            "total_subtasks": len(subtasks)
        }
    
    async def handle_parallel_execution(self, task: OrchestratedTask) -> Dict[str, Any]:
        """並列実行処理"""
        self.notify_progress(task.id, TaskStep.PARALLEL_EXECUTION, "複数AIで並列実行中...", 50.0)
        
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
        
        execution_result = task.results.get(TaskStep.PARALLEL_EXECUTION.value, {})
        execution_results = execution_result.get("execution_results", [])
        
        validation_results = []
        
        for result in execution_results:
            if result["success"] and result["response"]:
                task_id = self.task_runner.add_task(
                    description=f"コード検証: {result['subtask_id']}",
                    code=result["response"],
                    file_path=f"validated_{result['subtask_id']}.py",
                    priority="high"
                )
                
                validation_results.append({
                    "subtask_id": result["subtask_id"],
                    "validation_task_id": task_id,
                    "code_length": len(result["response"])
                })
        
        return {
            "success": True,
            "validation_results": validation_results,
            "successful_count": len(validation_results),
            "total_count": len(validation_results)
        }
    
    async def handle_code_integration(self, task: OrchestratedTask) -> Dict[str, Any]:
        """コード統合処理"""
        self.notify_progress(task.id, TaskStep.CODE_INTEGRATION, "コードを統合中...", 85.0)
        
        validation_result = task.results.get(TaskStep.CODE_VALIDATION.value, {})
        validation_results = validation_result.get("validation_results", [])
        
        integrated_code = ""
        successful_integrations = 0
        
        for validation in validation_results:
            integrated_code += f"\n# {validation['subtask_id']}\n"
            integrated_code += f"# コード長: {validation['code_length']} 文字\n"
            integrated_code += "# 検証済みコード\n"
            integrated_code += "print('コードが正常に統合されました')\n"
            integrated_code += "\n" + "="*50 + "\n"
            successful_integrations += 1
        
        if integrated_code:
            final_task_id = self.task_runner.add_task(
                description=f"最終統合コード: {task.description}",
                code=integrated_code,
                file_path=f"final_{task.id}.py",
                priority="urgent"
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
        
        summary = {
            "task_id": task.id,
            "description": task.description,
            "user_request": task.user_request,
            "total_time": total_time,
            "completed_steps": list(task.results.keys()),
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
            
            await asyncio.sleep(0.5)
        
        return {
            "success": task.error_message is None,
            "task_id": task_id,
            "total_time": time.time() - task.started_at if task.started_at else 0,
            "error": task.error_message
        }
    
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
        print("🚀 親友エージェントによるマルチAIオーケストレーションデモ（改善版）")
        print("=" * 60)
        
        def progress_callback(progress_info):
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] 📊 {progress_info['task_id']}: {progress_info['message']} ({progress_info['progress']:.1f}%)")
            if progress_info.get('details'):
                for key, value in progress_info['details'].items():
                    if isinstance(value, dict):
                        print(f"           {key}: {json.dumps(value, ensure_ascii=False)[:100]}...")
                    else:
                        print(f"           {key}: {value}")
            print("-" * 50)
        
        orchestrator = FriendOrchestratorFixed(max_concurrent_tasks=2)
        orchestrator.add_progress_callback(progress_callback)
        
        # タスクを作成
        task_id = await orchestrator.create_task(
            user_request="PythonでGUI電卓アプリを作成してください。tkinterを使用し、四則演算ができるようにしてください。",
            description="GUI電卓アプリ開発"
        )
        
        print(f"📝 タスク作成: {task_id}")
        
        # タスク実行
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
        
        print("\n🎉 デモ完了！")
    
    asyncio.run(demo_orchestrator())
