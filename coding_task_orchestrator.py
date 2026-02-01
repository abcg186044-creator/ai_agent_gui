#!/usr/bin/env python3
"""
コーディングタスクオーケストレーター
親友エージェントからのコーディング指示をステップ分割し、
5つのコーディングAIで非同期実行するシステム
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

from coding_ai_agents import (
    BaseCodingAI, CodingTask, ProjectContext, TaskStatus, CodingRole,
    create_all_coding_ai
)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskStep:
    """タスクステップの定義"""
    id: str
    name: str
    description: str
    role: CodingRole
    dependencies: List[str] = field(default_factory=list)
    estimated_time: int = 60  # 秒
    priority: int = 1

@dataclass
class CodingProject:
    """コーディングプロジェクト"""
    id: str
    name: str
    requirements: str
    tech_stack: List[str]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    context: Optional[ProjectContext] = None
    tasks: List[CodingTask] = field(default_factory=list)
    progress: float = 0.0

class CodingTaskOrchestrator:
    """コーディングタスクオーケストレーター"""
    
    def __init__(self):
        self.coding_ai_agents = create_all_coding_ai()
        self.projects: Dict[str, CodingProject] = {}
        self.active_tasks: Dict[str, CodingTask] = {}
        self.progress_callbacks: List[Callable] = []
        self.is_running = False
        
    def add_progress_callback(self, callback: Callable):
        """進捗コールバックを追加"""
        self.progress_callbacks.append(callback)
    
    def notify_progress(self, project_id: str, task_id: str, progress_data: Dict[str, Any]):
        """進捗通知を送信"""
        for callback in self.progress_callbacks:
            try:
                callback(project_id, task_id, progress_data)
            except Exception as e:
                logger.error(f"進捗コールバックエラー: {e}")
    
    def create_project_from_request(self, request: str, tech_stack: List[str] = None) -> str:
        """親友エージェントからのリクエストからプロジェクトを作成"""
        project_id = str(uuid.uuid4())
        
        # デフォルト技術スタック
        if tech_stack is None:
            tech_stack = ["Python", "FastAPI", "React", "PostgreSQL", "Docker"]
        
        project = CodingProject(
            id=project_id,
            name=self._extract_project_name(request),
            requirements=request,
            tech_stack=tech_stack
        )
        
        # プロジェクトコンテキストの初期化
        project.context = ProjectContext(
            project_name=project.name,
            requirements=request,
            tech_stack=tech_stack
        )
        
        # 先にプロジェクトを保存（タスク作成前）
        self.projects[project_id] = project
        logger.info(f"プロジェクト保存: {project.name} (ID: {project_id})")
        
        # タスクステップの作成
        tasks = self._create_task_steps(project_id, request, tech_stack)
        project.tasks = tasks
        
        logger.info(f"プロジェクト作成完了: {project.name} (ID: {project_id})")
        
        return project_id
    
    def _extract_project_name(self, request: str) -> str:
        """リクエストからプロジェクト名を抽出"""
        # 簡単なプロジェクト名抽出ロジック
        if "電卓" in request:
            return "電卓アプリ"
        elif "チャット" in request:
            return "チャットアプリ"
        elif "ブログ" in request:
            return "ブログシステム"
        elif "EC" in request or "ショッピング" in request:
            return "ECサイト"
        else:
            return "AI生成アプリ"
    
    def _create_task_steps(self, project_id: str, request: str, tech_stack: List[str]) -> List[CodingTask]:
        """コーディングタスクをステップ分割"""
        tasks = []
        
        # ステップ1: 設計
        design_task = CodingTask(
            id=str(uuid.uuid4()),
            role=CodingRole.DESIGNER,
            description=f"アプリケーション設計: {request}",
            input_data={
                "requirements": request,
                "tech_stack": tech_stack
            }
        )
        tasks.append(design_task)
        
        # ステップ2: 実装（設計に依存）
        implementation_task = CodingTask(
            id=str(uuid.uuid4()),
            role=CodingRole.IMPLEMENTER,
            description="アプリケーション実装",
            input_data={},
            dependencies=[design_task.id]
        )
        tasks.append(implementation_task)
        
        # ステップ3: テスト（実装に依存）
        test_task = CodingTask(
            id=str(uuid.uuid4()),
            role=CodingRole.TESTER,
            description="テスト作成と実行",
            input_data={},
            dependencies=[implementation_task.id]
        )
        tasks.append(test_task)
        
        # ステップ4: 最適化（テストに依存）
        optimization_task = CodingTask(
            id=str(uuid.uuid4()),
            role=CodingRole.OPTIMIZER,
            description="パフォーマンス最適化",
            input_data={},
            dependencies=[test_task.id]
        )
        tasks.append(optimization_task)
        
        # ステップ5: 統合（最適化に依存）
        integration_task = CodingTask(
            id=str(uuid.uuid4()),
            role=CodingRole.INTEGRATOR,
            description="システム統合とデプロイ",
            input_data={},
            dependencies=[optimization_task.id]
        )
        tasks.append(integration_task)
        
        return tasks
    
    async def execute_project(self, project_id: str) -> bool:
        """プロジェクトを実行"""
        if project_id not in self.projects:
            logger.error(f"プロジェクトが見つかりません: {project_id}")
            return False
        
        project = self.projects[project_id]
        project.status = TaskStatus.IN_PROGRESS
        project.started_at = datetime.now()
        self.is_running = True
        
        logger.info(f"プロジェクト実行開始: {project.name}")
        
        try:
            # タスクを依存関係順に実行
            completed_tasks = set()
            
            while len(completed_tasks) < len(project.tasks):
                # 実行可能なタスクを探す
                ready_tasks = [
                    task for task in project.tasks
                    if task.id not in completed_tasks and
                    all(dep in completed_tasks for dep in task.dependencies)
                ]
                
                if not ready_tasks:
                    logger.error("実行可能なタスクがありません - 循環依存の可能性")
                    project.status = TaskStatus.FAILED
                    return False
                
                # 準備ができたタスクを並列実行
                await self._execute_tasks_parallel(project, ready_tasks, completed_tasks)
                
                # 進捗更新
                project.progress = len(completed_tasks) / len(project.tasks) * 100
                self._update_project_progress(project)
            
            project.status = TaskStatus.COMPLETED
            project.completed_at = datetime.now()
            project.progress = 100.0
            
            logger.info(f"プロジェクト完了: {project.name}")
            return True
            
        except Exception as e:
            logger.error(f"プロジェクト実行エラー: {e}")
            project.status = TaskStatus.FAILED
            return False
        finally:
            self.is_running = False
    
    async def _execute_tasks_parallel(self, project: CodingProject, tasks: List[CodingTask], completed_tasks: set):
        """タスクを並列実行"""
        async def execute_single_task(task: CodingTask):
            try:
                # AIエージェントを取得
                ai_agent = self.coding_ai_agents[task.role]
                
                # タスク実行
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.now()
                
                # 進捗通知
                self.notify_progress(project.id, task.id, {
                    "status": "started",
                    "role": task.role.value,
                    "description": task.description
                })
                
                # AIにタスクを処理させる
                result = await ai_agent.process_task(task, project.context)
                
                # タスク完了
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.output_data = result
                completed_tasks.add(task.id)
                
                # 進捗通知
                self.notify_progress(project.id, task.id, {
                    "status": "completed",
                    "role": task.role.value,
                    "result": result
                })
                
                logger.info(f"タスク完了: {task.role.value} - {task.description}")
                
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                
                # 進捗通知
                self.notify_progress(project.id, task.id, {
                    "status": "failed",
                    "role": task.role.value,
                    "error": str(e)
                })
                
                logger.error(f"タスク失敗: {task.role.value} - {e}")
        
        # 並列実行
        await asyncio.gather(
            *[execute_single_task(task) for task in tasks],
            return_exceptions=True
        )
    
    def _update_project_progress(self, project: CodingProject):
        """プロジェクト進捗を更新"""
        progress_data = {
            "project_id": project.id,
            "project_name": project.name,
            "progress": project.progress,
            "status": project.status.value,
            "completed_tasks": len([t for t in project.tasks if t.status == TaskStatus.COMPLETED]),
            "total_tasks": len(project.tasks)
        }
        
        self.notify_progress(project.id, "project_progress", progress_data)
    
    def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """プロジェクトステータスを取得"""
        if project_id not in self.projects:
            return None
        
        project = self.projects[project_id]
        
        return {
            "project_id": project.id,
            "name": project.name,
            "status": project.status.value,
            "progress": project.progress,
            "created_at": project.created_at.isoformat(),
            "started_at": project.started_at.isoformat() if project.started_at else None,
            "completed_at": project.completed_at.isoformat() if project.completed_at else None,
            "requirements": project.requirements,
            "tech_stack": project.tech_stack,
            "completed_tasks": len([t for t in project.tasks if t.status == TaskStatus.COMPLETED]),
            "total_tasks": len(project.tasks),
            "tasks": [
                {
                    "id": task.id,
                    "role": task.role.value,
                    "description": task.description,
                    "status": task.status.value,
                    "progress": task.progress,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "error_message": task.error_message
                }
                for task in project.tasks
            ]
        }
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """全てのプロジェクトステータスを取得"""
        return [self.get_project_status(project_id) for project_id in self.projects.keys()]
    
    def get_ai_agents_status(self) -> Dict[str, Any]:
        """AIエージェントのステータスを取得"""
        return {
            role.value: {
                "role": role.value,
                "is_busy": agent.is_busy,
                "completed_tasks": agent.completed_tasks,
                "capabilities": agent.get_capabilities()
            }
            for role, agent in self.coding_ai_agents.items()
        }
    
    async def cancel_project(self, project_id: str) -> bool:
        """プロジェクトをキャンセル"""
        if project_id not in self.projects:
            return False
        
        project = self.projects[project_id]
        if project.status == TaskStatus.COMPLETED:
            return False
        
        project.status = TaskStatus.FAILED
        project.completed_at = datetime.now()
        
        # 実行中のタスクをキャンセル
        for task in project.tasks:
            if task.status == TaskStatus.IN_PROGRESS:
                task.status = TaskStatus.FAILED
                task.error_message = "プロジェクトがキャンセルされました"
        
        logger.info(f"プロジェクトキャンセル: {project.name}")
        return True
    
    def generate_project_report(self, project_id: str) -> Optional[str]:
        """プロジェクトレポートを生成"""
        if project_id not in self.projects:
            return None
        
        project = self.projects[project_id]
        
        if project.status != TaskStatus.COMPLETED:
            return "プロジェクトが完了していません"
        
        # レポート生成
        report = f"""
# {project.name} - 完了レポート

## プロジェクト概要
- プロジェクトID: {project.id}
- 要件: {project.requirements}
- 技術スタック: {', '.join(project.tech_stack)}
- 開始時間: {project.started_at}
- 完了時間: {project.completed_at}

## タスク実行結果
"""
        
        for task in project.tasks:
            report += f"""
### {task.role.value.upper()}
- 状態: {task.status.value}
- 開始: {task.started_at}
- 完了: {task.completed_at}
- 説明: {task.description}
"""
        
        if project.context:
            report += "\n## 生成成果物\n"
            
            if project.context.design_docs:
                report += "\n### 設計ドキュメント\n"
                for doc_type, content in project.context.design_docs.items():
                    report += f"- {doc_type}: 作成完了\n"
            
            if project.context.implementation:
                report += "\n### 実装コード\n"
                for file_type, content in project.context.implementation.items():
                    report += f"- {file_type}: 作成完了\n"
            
            if project.context.test_results:
                report += "\n### テスト結果\n"
                test_results = project.context.test_results.get("test_results", {})
                if test_results:
                    report += f"- 成功率: {test_results.get('success_rate', 'N/A')}\n"
                
                coverage = project.context.test_results.get("coverage_report", {})
                if coverage:
                    report += f"- カバレッジ: {coverage.get('total_coverage', 'N/A')}\n"
        
        return report

# シングルトンインスタンス
orchestrator_instance = None

def get_orchestrator() -> CodingTaskOrchestrator:
    """オーケストレーターのシングルトンインスタンスを取得"""
    global orchestrator_instance
    if orchestrator_instance is None:
        orchestrator_instance = CodingTaskOrchestrator()
    return orchestrator_instance

# デモ用関数
async def demo_coding_orchestrator():
    """コーディングオーケストレーターのデモ"""
    orchestrator = get_orchestrator()
    
    # 進捗コールバック
    def progress_callback(project_id: str, task_id: str, progress_data: Dict[str, Any]):
        print(f"進捗通知: {progress_data}")
    
    orchestrator.add_progress_callback(progress_callback)
    
    # プロジェクト作成
    request = "電卓アプリを作成してください。基本的な四則演算と履歴機能が必要です。"
    project_id = orchestrator.create_project_from_request(request)
    
    print(f"プロジェクト作成: {project_id}")
    
    # プロジェクト実行
    success = await orchestrator.execute_project(project_id)
    
    if success:
        print("プロジェクト完了!")
        report = orchestrator.generate_project_report(project_id)
        print(report)
    else:
        print("プロジェクト失敗...")
    
    # ステータス確認
    status = orchestrator.get_project_status(project_id)
    print(f"最終ステータス: {json.dumps(status, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(demo_coding_orchestrator())
