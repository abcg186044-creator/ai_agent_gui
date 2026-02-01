#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コーディングタスクランナー - AI生成コードの検証と適用
"""

import asyncio
import queue
import threading
import time
import json
import subprocess
import tempfile
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

class TaskStatus(Enum):
    """タスクステータス"""
    PENDING = "pending"
    RUNNING = "running"
    VALIDATING = "validating"
    APPLYING = "applying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """タスク優先度"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

@dataclass
class CodingTask:
    """コーディングタスク"""
    id: str
    description: str
    code: str
    file_path: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    validation_result: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)

class TaskQueue:
    """タスクキュー管理"""
    
    def __init__(self):
        self.queue = queue.PriorityQueue()
        self.tasks: Dict[str, CodingTask] = {}
        self.lock = threading.Lock()
    
    def add_task(self, task: CodingTask):
        """タスクを追加"""
        with self.lock:
            # 優先度の逆数でキューに入れる（高い優先度が先）
            priority_value = -task.priority.value
            self.queue.put((priority_value, task.created_at, task.id))
            self.tasks[task.id] = task
    
    def get_next_task(self) -> Optional[CodingTask]:
        """次のタスクを取得"""
        try:
            priority, created_at, task_id = self.queue.get_nowait()
            with self.lock:
                return self.tasks.get(task_id)
        except queue.Empty:
            return None
    
    def get_task(self, task_id: str) -> Optional[CodingTask]:
        """タスクを取得"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus, error_message: Optional[str] = None):
        """タスクステータスを更新"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = status
                if error_message:
                    self.tasks[task_id].error_message = error_message
                
                if status == TaskStatus.RUNNING:
                    self.tasks[task_id].started_at = time.time()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    self.tasks[task_id].completed_at = time.time()
    
    def get_all_tasks(self) -> List[CodingTask]:
        """すべてのタスクを取得"""
        with self.lock:
            return list(self.tasks.values())
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[CodingTask]:
        """ステータスでタスクをフィルタリング"""
        with self.lock:
            return [task for task in self.tasks.values() if task.status == status]

class CodeValidator:
    """コード検証器"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def validate_syntax(self, code: str, language: str = "python") -> Dict[str, Any]:
        """構文を検証"""
        try:
            if language == "python":
                # Python構文チェック
                compile(code, '<string>', 'exec')
                return {"valid": True, "error": None}
            elif language == "javascript":
                # JavaScript構文チェック（簡易）
                if "function" in code or "const" in code or "let" in code or "var" in code:
                    return {"valid": True, "error": None}
                else:
                    return {"valid": False, "error": "Invalid JavaScript syntax"}
            else:
                return {"valid": True, "error": f"Unsupported language: {language}"}
        except SyntaxError as e:
            return {"valid": False, "error": str(e)}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def validate_logic(self, code: str, description: str) -> Dict[str, Any]:
        """論理を検証"""
        # 簡単な論理チェック
        issues = []
        
        # 基本的なセキュリティチェック
        dangerous_patterns = ["eval(", "exec(", "__import__", "subprocess.call"]
        for pattern in dangerous_patterns:
            if pattern in code:
                issues.append(f"Potentially dangerous pattern found: {pattern}")
        
        # 説明との一致チェック
        if "function" in description.lower() and "def " not in code:
            issues.append("Description mentions function but no function definition found")
        
        if "class" in description.lower() and "class " not in code:
            issues.append("Description mentions class but no class definition found")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "score": max(0, 100 - len(issues) * 10)
        }
    
    def test_execution(self, code: str, language: str = "python") -> Dict[str, Any]:
        """実行テスト"""
        try:
            if language == "python":
                # 安全な実行環境でテスト
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    f.flush()
                    
                    # タイムアウト付きで実行
                    result = subprocess.run(
                        ['python', f.name],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        cwd=self.temp_dir
                    )
                    
                    os.unlink(f.name)
                    
                    return {
                        "success": result.returncode == 0,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode
                    }
            else:
                return {"success": False, "error": f"Execution test not supported for {language}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class CodeApplicator:
    """コード適用器"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
    
    def apply_to_file(self, task: CodingTask) -> Dict[str, Any]:
        """ファイルにコードを適用"""
        try:
            if not task.file_path:
                return {"success": False, "error": "No file path specified"}
            
            full_path = os.path.join(self.base_path, task.file_path)
            
            # ディレクトリを作成
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # バックアップを作成
            backup_path = None
            if os.path.exists(full_path):
                backup_path = f"{full_path}.backup.{int(time.time())}"
                with open(full_path, 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(backup_content)
            
            # コードを書き込み
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(task.code)
            
            return {
                "success": True,
                "file_path": full_path,
                "backup_path": backup_path,
                "size": len(task.code)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_new_file(self, task: CodingTask) -> Dict[str, Any]:
        """新しいファイルを作成"""
        return self.apply_to_file(task)

class CodingTaskRunner:
    """コーディングタスクランナー"""
    
    def __init__(self, max_workers: int = 3, base_path: str = "."):
        self.task_queue = TaskQueue()
        self.validator = CodeValidator()
        self.applicator = CodeApplicator(base_path)
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = False
        self.progress_callbacks: List[Callable] = []
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "cancelled_tasks": 0
        }
    
    def add_progress_callback(self, callback: Callable):
        """進捗コールバックを追加"""
        self.progress_callbacks.append(callback)
    
    def notify_progress(self, task_id: str, message: str, progress: float = 0.0):
        """進捗を通知"""
        for callback in self.progress_callbacks:
            try:
                callback({
                    "task_id": task_id,
                    "message": message,
                    "progress": progress,
                    "timestamp": time.time()
                })
            except:
                pass
    
    def add_task(self, description: str, code: str, file_path: Optional[str] = None, 
                 priority: TaskPriority = TaskPriority.MEDIUM, dependencies: List[str] = None) -> str:
        """タスクを追加"""
        task_id = f"task_{int(time.time() * 1000)}_{len(self.task_queue.tasks)}"
        task = CodingTask(
            id=task_id,
            description=description,
            code=code,
            file_path=file_path,
            priority=priority,
            dependencies=dependencies or []
        )
        
        self.task_queue.add_task(task)
        self.stats["total_tasks"] += 1
        
        self.notify_progress(task_id, f"タスク追加: {description}", 0.0)
        return task_id
    
    def process_task(self, task: CodingTask) -> Dict[str, Any]:
        """単一タスクを処理"""
        try:
            # 実行中に設定
            self.task_queue.update_task_status(task.id, TaskStatus.RUNNING)
            self.notify_progress(task.id, f"処理開始: {task.description}", 10.0)
            
            # 依存関係チェック
            if task.dependencies:
                for dep_id in task.dependencies:
                    dep_task = self.task_queue.get_task(dep_id)
                    if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                        raise Exception(f"Dependency {dep_id} not completed")
            
            # 構文検証
            self.task_queue.update_task_status(task.id, TaskStatus.VALIDATING)
            self.notify_progress(task_id, "構文検証中...", 30.0)
            
            syntax_result = self.validator.validate_syntax(task.code)
            if not syntax_result["valid"]:
                raise Exception(f"Syntax error: {syntax_result['error']}")
            
            # 論理検証
            self.notify_progress(task_id, "論理検証中...", 50.0)
            logic_result = self.validator.validate_logic(task.code, task.description)
            
            # 実行テスト（オプション）
            self.notify_progress(task_id, "実行テスト中...", 70.0)
            exec_result = self.validator.test_execution(task.code)
            
            # 適用
            self.task_queue.update_task_status(task.id, TaskStatus.APPLYING)
            self.notify_progress(task_id, "コード適用中...", 85.0)
            
            if task.file_path:
                apply_result = self.applicator.apply_to_file(task)
            else:
                apply_result = {"success": True, "message": "No file path specified, skipping application"}
            
            if not apply_result["success"]:
                raise Exception(f"Application failed: {apply_result['error']}")
            
            # 完了
            self.task_queue.update_task_status(task.id, TaskStatus.COMPLETED)
            self.notify_progress(task_id, "タスク完了", 100.0)
            
            self.stats["completed_tasks"] += 1
            
            return {
                "success": True,
                "task_id": task.id,
                "syntax_result": syntax_result,
                "logic_result": logic_result,
                "exec_result": exec_result,
                "apply_result": apply_result
            }
            
        except Exception as e:
            self.task_queue.update_task_status(task.id, TaskStatus.FAILED, str(e))
            self.notify_progress(task_id, f"エラー: {str(e)}", 0.0)
            self.stats["failed_tasks"] += 1
            
            return {
                "success": False,
                "task_id": task.id,
                "error": str(e)
            }
    
    def start_processing(self):
        """タスク処理を開始"""
        if self.running:
            return
        
        self.running = True
        
        def worker():
            while self.running:
                task = self.task_queue.get_next_task()
                if task:
                    self.process_task(task)
                else:
                    time.sleep(0.1)
        
        # ワーカースレッドを起動
        for _ in range(self.max_workers):
            self.executor.submit(worker)
    
    def stop_processing(self):
        """タスク処理を停止"""
        self.running = False
    
    def get_task_status(self, task_id: str) -> Optional[CodingTask]:
        """タスクステータスを取得"""
        return self.task_queue.get_task(task_id)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[CodingTask]:
        """ステータスでタスクをフィルタリング"""
        return self.task_queue.get_tasks_by_status(status)
    
    def get_all_tasks(self) -> List[CodingTask]:
        """すべてのタスクを取得"""
        return self.task_queue.get_all_tasks()
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return self.stats.copy()
    
    def cancel_task(self, task_id: str) -> bool:
        """タスクをキャンセル"""
        task = self.task_queue.get_task(task_id)
        if task and task.status in [TaskStatus.PENDING]:
            self.task_queue.update_task_status(task_id, TaskStatus.CANCELLED)
            self.stats["cancelled_tasks"] += 1
            self.notify_progress(task_id, "タスクキャンセル", 0.0)
            return True
        return False

# テスト用
if __name__ == "__main__":
    def progress_callback(progress_info):
        print(f"[{progress_info['task_id']}] {progress_info['message']} ({progress_info['progress']:.1f}%)")
    
    runner = CodingTaskRunner(max_workers=2)
    runner.add_progress_callback(progress_callback)
    
    # テストタスクを追加
    tasks = [
        ("電卓関数を作成", '''
def calculator(a, b, operation):
    """簡単な電卓関数"""
    if operation == "+":
        return a + b
    elif operation == "-":
        return a - b
    elif operation == "*":
        return a * b
    elif operation == "/":
        return a / b if b != 0 else "Error"
    else:
        return "Invalid operation"
''', "calculator.py", TaskPriority.HIGH),
        
        ("HTML電卓ページ", '''
<!DOCTYPE html>
<html>
<head>
    <title>電卓</title>
</head>
<body>
    <h1>電卓アプリ</h1>
    <script>
        function calculate() {
            console.log("電計算機能");
        }
    </script>
</body>
</html>
''', "calculator.html", TaskPriority.MEDIUM),
        
        ("バグのあるコード", '''
def buggy_function():
    print("This will cause syntax error
    return True
''', "buggy.py", TaskPriority.LOW)
    ]
    
    # タスクを追加
    task_ids = []
    for desc, code, path, priority in tasks:
        task_id = runner.add_task(desc, code, path, priority)
        task_ids.append(task_id)
    
    # 処理を開始
    runner.start_processing()
    
    # しばらく待ってから結果を表示
    time.sleep(10)
    
    print("\n📊 最終結果:")
    for task_id in task_ids:
        task = runner.get_task_status(task_id)
        if task:
            status_text = {
                TaskStatus.PENDING: "待機中",
                TaskStatus.RUNNING: "実行中",
                TaskStatus.VALIDATING: "検証中",
                TaskStatus.APPLYING: "適用中",
                TaskStatus.COMPLETED: "完了",
                TaskStatus.FAILED: "失敗",
                TaskStatus.CANCELLED: "キャンセル"
            }.get(task.status, task.status.value)
            
            print(f"   {task.description}: {status_text}")
            if task.error_message:
                print(f"     エラー: {task.error_message}")
    
    print(f"\n📈 統計: {runner.get_stats()}")
    
    # 処理を停止
    runner.stop_processing()
