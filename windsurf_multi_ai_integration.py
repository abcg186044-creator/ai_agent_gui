#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windsurf向けマルチAI統合システム - UI進捗表示付き
"""

import asyncio
import streamlit as st
import time
import json
from typing import Dict, List, Optional, Any
import threading
from datetime import datetime

from async_ollama_client import AsyncOllamaClient
from coding_task_runner import CodingTaskRunner, TaskPriority, TaskStatus
from local_llm_server import LocalLLMServer

class MultiAIOrchestrator:
    """マルチAIオーケストレーター"""
    
    def __init__(self):
        self.ollama_client = None
        self.task_runner = None
        self.local_server = None
        self.active_tasks = {}
        self.progress_history = []
        self.setup_complete = False
    
    async def setup(self):
        """セットアップ"""
        if self.setup_complete:
            return
        
        # 非同期Ollamaクライアントを初期化
        self.ollama_client = AsyncOllamaClient(
            ports=[11434, 11435, 11436],
            models=["llama3.2:3b", "llama3.1:8b"]
        )
        
        # タスクランナーを初期化
        self.task_runner = CodingTaskRunner(max_workers=3)
        self.task_runner.add_progress_callback(self.on_task_progress)
        
        # ローカルLLMサーバー（バックグラウンドで起動）
        self.local_server = LocalLLMServer(port=11437)
        
        self.setup_complete = True
    
    def on_task_progress(self, progress_info: Dict[str, Any]):
        """タスク進捗コールバック"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 進捗履歴に追加
        self.progress_history.append({
            **progress_info,
            "timestamp": timestamp
        })
        
        # 履歴を最新の50件に制限
        if len(self.progress_history) > 50:
            self.progress_history = self.progress_history[-50:]
        
        # アクティブタスクを更新
        task_id = progress_info["task_id"]
        self.active_tasks[task_id] = {
            **progress_info,
            "timestamp": timestamp
        }
    
    async def generate_coding_solutions(self, prompt: str, description: str) -> List[Dict[str, Any]]:
        """複数のコーディングソリューションを生成"""
        if not self.setup_complete:
            await self.setup()
        
        # 複数のプロンプトバリエーションを作成
        prompts = [
            f"{prompt}\n\n最適化されたPythonコードを生成してください。",
            f"{prompt}\n\nエラーハンドリングを含んだ堅牢なコードを生成してください。",
            f"{prompt}\n\nテスト可能なモジュール設計でコードを生成してください。"
        ]
        
        # 並列で生成
        async with self.ollama_client as client:
            def progress_callback_factory(solution_id):
                def callback(progress_info):
                    new_info = progress_info.copy()
                    new_info["solution_id"] = solution_id
                    new_info["type"] = "ai_generation"
                    self.on_task_progress(new_info)
                return callback
            
            results = await client.generate_parallel_responses(
                prompts, 
                progress_callback_factory("coding_solution")
            )
        
        # 成功した結果のみを返す
        successful_results = []
        for i, result in enumerate(results):
            if result["success"]:
                successful_results.append({
                    "id": f"solution_{i}",
                    "code": result["response"],
                    "model": result["model"],
                    "port": result["port"],
                    "elapsed_time": result["elapsed_time"]
                })
        
        return successful_results
    
    def add_coding_task(self, description: str, code: str, file_path: str = None, 
                       priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """コーディングタスクを追加"""
        if not self.setup_complete:
            raise Exception("System not setup. Call setup() first.")
        
        task_id = self.task_runner.add_task(
            description=description,
            code=code,
            file_path=file_path,
            priority=priority
        )
        
        return task_id
    
    def start_task_processing(self):
        """タスク処理を開始"""
        if self.task_runner:
            self.task_runner.start_processing()
    
    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスを取得"""
        status = {
            "setup_complete": self.setup_complete,
            "active_tasks": len(self.active_tasks),
            "progress_history_size": len(self.progress_history)
        }
        
        if self.task_runner:
            status.update({
                "task_runner_stats": self.task_runner.get_stats(),
                "all_tasks": len(self.task_runner.get_all_tasks())
            })
        
        return status

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Windsurf マルチAIコーディングシステム",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 Windsurf マルチAIコーディングシステム")
    st.markdown("---")
    
    # セッション状態の初期化
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = MultiAIOrchestrator()
        st.session_state.setup_done = False
    
    orchestrator = st.session_state.orchestrator
    
    # セットアップ
    if not st.session_state.setup_done:
        with st.spinner("🔧 マルチAIシステムをセットアップ中..."):
            asyncio.run(orchestrator.setup())
            st.session_state.setup_done = True
        st.success("✅ セットアップ完了！")
    
    # サイドバー - 進捗表示
    st.sidebar.title("📊 AIエージェント進捗")
    
    # アクティブタスク表示
    if orchestrator.active_tasks:
        st.sidebar.subheader("🔄 実行中タスク")
        for task_id, task_info in orchestrator.active_tasks.items():
            with st.sidebar.expander(f"タスク {task_id[:12]}...", expanded=False):
                st.write(f"**メッセージ**: {task_info['message']}")
                st.write(f"**進捗**: {task_info['progress']:.1f}%")
                st.write(f"**時刻**: {task_info['timestamp']}")
                
                # プログレスバー
                st.progress(task_info['progress'] / 100.0)
    
    # 進捗履歴
    if orchestrator.progress_history:
        st.sidebar.subheader("📜 進捗履歴")
        history_df = []
        for entry in orchestrator.progress_history[-10:]:  # 最新10件
            history_df.append({
                "時刻": entry["timestamp"],
                "タスク": entry["task_id"][:12] + "...",
                "メッセージ": entry["message"][:30] + "...",
                "進捗": f"{entry['progress']:.1f}%"
            })
        
        if history_df:
            import pandas as pd
            st.sidebar.dataframe(pd.DataFrame(history_df), use_container_width=True)
    
    # システムステータス
    st.sidebar.subheader("🖥️ システムステータス")
    status = orchestrator.get_system_status()
    st.sidebar.json(status)
    
    # メインコンテンツ
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 コーディングリクエスト")
        
        # 入力フォーム
        with st.form("coding_request"):
            prompt = st.text_area(
                "コーディング要件",
                height=150,
                placeholder="例: PythonでGUI電卓アプリを作成してください。ボタン操作で四則演算ができるようにしてください。"
            )
            
            description = st.text_input(
                "タスク説明",
                placeholder="例: Python GUI電卓アプリ開発"
            )
            
            file_path = st.text_input(
                "出力ファイルパス（任意）",
                placeholder="例: calculator.py"
            )
            
            priority = st.selectbox(
                "優先度",
                options=[("低", TaskPriority.LOW), ("中", TaskPriority.MEDIUM), 
                        ("高", TaskPriority.HIGH), ("緊急", TaskPriority.URGENT)],
                format_func=lambda x: x[0]
            )
            
            submitted = st.form_submit_button("🚀 AIでコード生成")
            
            if submitted and prompt:
                with st.spinner("🤖 複数AIでコード生成中..."):
                    # 非同期でコード生成
                    solutions = asyncio.run(orchestrator.generate_coding_solutions(prompt, description))
                    
                    if solutions:
                        st.success(f"✅ {len(solutions)}個のソリューションを生成しました！")
                        
                        # ソリューション表示
                        for i, solution in enumerate(solutions):
                            with st.expander(f"ソリューション {i+1} ({solution['model']})", expanded=i==0):
                                st.code(solution['code'], language='python')
                                
                                # タスクとして追加ボタン
                                if st.button(f"タスクとして追加 {i+1}", key=f"add_task_{i}"):
                                    task_id = orchestrator.add_coding_task(
                                        description=description,
                                        code=solution['code'],
                                        file_path=file_path,
                                        priority=priority[1]
                                    )
                                    st.success(f"✅ タスク {task_id} を追加しました！")
                    else:
                        st.error("❌ ソリューションの生成に失敗しました")
    
    with col2:
        st.header("🎯 タスク管理")
        
        # タスク処理開始ボタン
        if st.button("▶️ タスク処理を開始"):
            orchestrator.start_task_processing()
            st.success("✅ タスク処理を開始しました！")
        
        # タスク一覧
        if orchestrator.task_runner:
            all_tasks = orchestrator.task_runner.get_all_tasks()
            
            if all_tasks:
                st.subheader(f"📋 全タスク ({len(all_tasks)})")
                
                for task in all_tasks:
                    status_emoji = {
                        TaskStatus.PENDING: "⏳",
                        TaskStatus.RUNNING: "🔄",
                        TaskStatus.VALIDATING: "🔍",
                        TaskStatus.APPLYING: "📝",
                        TaskStatus.COMPLETED: "✅",
                        TaskStatus.FAILED: "❌",
                        TaskStatus.CANCELLED: "🚫"
                    }.get(task.status, "❓")
                    
                    with st.expander(f"{status_emoji} {task.description}", expanded=False):
                        st.write(f"**ステータス**: {task.status.value}")
                        st.write(f"**優先度**: {task.priority.name}")
                        st.write(f"**ファイル**: {task.file_path or 'なし'}")
                        
                        if task.error_message:
                            st.error(f"エラー: {task.error_message}")
                        
                        if task.code:
                            with st.expander("コードプレビュー"):
                                st.code(task.code[:500] + ("..." if len(task.code) > 500 else ""), language='python')
            else:
                st.info("📝 タスクがありません。コード生成してタスクを追加してください。")
    
    # リアルタイム更新
    if st.button("🔄 状態を更新"):
        st.rerun()

if __name__ == "__main__":
    main()
