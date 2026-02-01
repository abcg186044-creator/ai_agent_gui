#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
240秒タイムアウトで電卓アプリを作成するデモ
"""

import asyncio
import time
from typing import Dict, List, Any

from async_ollama_client import AsyncOllamaClient
from coding_task_runner import CodingTaskRunner, TaskPriority, TaskStatus

class CalculatorDemo240s:
    """電卓アプリ作成デモ（240秒タイムアウト）"""
    
    def __init__(self):
        self.ollama_client = None
        self.task_runner = None
        self.progress_log = []
        self.timeout = 240  # 240秒タイムアウト
    
    def log_progress(self, progress_info: Dict[str, Any]):
        """進捗をログ記録"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {progress_info.get('task_id', 'SYSTEM')}: {progress_info.get('message', 'No message')} ({progress_info.get('progress', 0):.1f}%)"
        self.progress_log.append(log_entry)
        print(log_entry)
    
    async def setup(self):
        """システムセットアップ"""
        print("🚀 240秒タイムアウト 電卓アプリ作成デモ開始")
        print("=" * 60)
        print(f"⏱️ タイムアウト設定: {self.timeout}秒")
        
        # 非同期Ollamaクライアントをセットアップ（240秒タイムアウト）
        self.ollama_client = AsyncOllamaClient(
            ports=[11434, 11435, 11436],
            models=["llama3.2:3b", "llama3.1:8b", "qwen2.5:7b"]
        )
        
        # タスクランナーをセットアップ
        self.task_runner = CodingTaskRunner(max_workers=3)
        self.task_runner.add_progress_callback(self.log_progress)
        
        print("✅ セットアップ完了！")
    
    async def generate_calculator_solutions(self):
        """電卓アプリのソリューションを生成"""
        print("\n🤖 電卓アプリソリューション生成中...")
        print("-" * 40)
        
        # 詳細な電卓アプリ要件
        calculator_prompts = [
            """
            詳細なGUI電卓アプリをPythonで作成してください。
            
            要件：
            - tkinterを使用したGUIインターフェース
            - 数字ボタン（0-9）
            - 演算子ボタン（+, -, *, /）
            - イコールボタンとクリアボタン
            - 小数点対応
            - 履歴表示機能
            - キーボード入力対応
            - エラーハンドリング（ゼロ除算など）
            - 美しいデザインとアニメーション効果
            
            完全な動作するコードを生成してください。
            """,
            
            """
            高機能な電卓アプリをPythonで作成してください。
            
            機能要件：
            - 基本四則演算
            - メモリ機能（M+, M-, MR, MC）
            - パーセント計算
            - 平方根計算
            - 履歴機能（計算結果の保存と表示）
            - テーマ切り替え（ライト/ダーク）
            - レスポンシブデザイン
            - コピー＆ペースト機能
            
            オブジェクト指向設計で実装してください。
            """,
            
            """
            プロフェッショナルな電卓アプリをPythonで作成してください。
            
            高度な機能：
            - 科学計算モード（三角関数、対数、指数）
            - プログラマーモード（16進数、2進数変換）
            - 単位変換機能
            - グラフ表示機能
            - 計算のエクスポート（CSV, JSON）
            - プラグイン機能拡張
            - 多言語対応
            - 設定保存機能
            
            モジュール化されたアーキテクチャで実装してください。
            """,
            
            """
            Webベースの電卓アプリを作成してください。
            
            技術要件：
            - HTML5 + CSS3 + JavaScript
            - レスポンシブデザイン
            - タッチデバイス対応
            - アニメーション効果
            - ローカルストレージで履歴保存
            - PWA対応（オフライン動作）
            - テーマ切り替え
            - キーボードショートカット
            
            モダンなフレームワーク（React/Vue）を使用してください。
            """
        ]
        
        print(f"📝 {len(calculator_prompts)}個の詳細な電卓アプリ要件を処理中...")
        
        # 並列で生成実行
        async with self.ollama_client as client:
            def progress_callback_factory(solution_id):
                def callback(progress_info):
                    new_info = progress_info.copy()
                    new_info["solution_id"] = solution_id
                    new_info["type"] = "calculator_generation"
                    self.log_progress(new_info)
                return callback
            
            results = await client.generate_parallel_responses(
                calculator_prompts,
                progress_callback_factory("calculator_solution")
            )
        
        print(f"\n📊 生成結果:")
        successful_results = []
        for i, result in enumerate(results):
            if result["success"]:
                successful_results.append(result)
                print(f"   ✅ ソリューション{i+1}: {result['model']} (ポート: {result['port']}, 時間: {result['elapsed_time']:.2f}秒)")
                print(f"      コード長: {len(result['response'])} 文字")
            else:
                print(f"   ❌ ソリューション{i+1}: 失敗 - {result['error']}")
        
        print(f"\n🎯 成功率: {len(successful_results)}/{len(calculator_prompts)} ({len(successful_results)/len(calculator_prompts)*100:.1f}%)")
        
        return successful_results
    
    def process_calculator_tasks(self, calculator_results: List[Dict[str, Any]]):
        """電卓タスクを処理"""
        print("\n📋 電卓アプリタスク処理中...")
        print("-" * 40)
        
        # 各ソリューションをタスクとして追加
        task_ids = []
        file_names = [
            "basic_calculator.py",
            "advanced_calculator.py", 
            "professional_calculator.py",
            "web_calculator.html"
        ]
        
        descriptions = [
            "基本GUI電卓アプリ",
            "高機能電卓アプリ",
            "プロフェッショナル電卓アプリ",
            "Webベース電卓アプリ"
        ]
        
        for i, result in enumerate(calculator_results):
            file_ext = "py" if i < 3 else "html"
            file_path = file_names[i] if i < len(file_names) else f"calculator_{i+1}.{file_ext}"
            
            task_id = self.task_runner.add_task(
                description=descriptions[i] if i < len(descriptions) else f"電卓アプリ{i+1}",
                code=result["response"],
                file_path=file_path,
                priority=TaskPriority.HIGH
            )
            task_ids.append(task_id)
            print(f"   📝 タスク追加: {task_id} -> {file_path}")
        
        print(f"\n🔄 タスク処理を開始...")
        self.task_runner.start_processing()
        
        # 処理完了を待機（最大240秒）
        max_wait_time = self.timeout
        wait_time = 0
        check_interval = 5
        
        print(f"⏱️ 最大{self.timeout}秒間処理を監視...")
        
        while wait_time < max_wait_time:
            # すべてのタスクを取得してステータスをチェック
            all_tasks = self.task_runner.get_all_tasks()
            completed_tasks = [task for task in all_tasks if task.status == TaskStatus.COMPLETED]
            failed_tasks = [task for task in all_tasks if task.status == TaskStatus.FAILED]
            
            progress = (len(completed_tasks) + len(failed_tasks)) / len(task_ids) * 100
            print(f"   📊 進捗: {len(completed_tasks)}/{len(task_ids)} 完了 ({progress:.1f}%)")
            
            if len(completed_tasks) + len(failed_tasks) >= len(task_ids):
                print("   ✅ すべてのタスクが完了しました")
                break
            
            time.sleep(check_interval)
            wait_time += check_interval
        
        if wait_time >= max_wait_time:
            print(f"   ⏰ {self.timeout}秒経過。処理を中断します。")
        
        # 結果表示
        print(f"\n📊 最終処理結果:")
        for i, task_id in enumerate(task_ids):
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
        print(f"   処理時間: {wait_time}秒")
        
        self.task_runner.stop_processing()
        
        return task_ids
    
    def show_generated_files(self):
        """生成されたファイルを表示"""
        print("\n📁 生成されたファイル:")
        print("-" * 40)
        
        import os
        import glob
        
        calculator_files = glob.glob("calculator*.py") + glob.glob("calculator*.html")
        
        if calculator_files:
            for file_path in calculator_files:
                try:
                    file_size = os.path.getsize(file_path)
                    print(f"   📄 {file_path} ({file_size} バイト)")
                    
                    # ファイルの先頭部分を表示
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if content:
                            lines = content.split('\n')[:10]
                            print("      先頭10行:")
                            for j, line in enumerate(lines, 1):
                                print(f"        {j:2d}: {line[:80]}")
                            if len(content.split('\n')) > 10:
                                print(f"        ... (全{len(content.split())}行)")
                        print()
                        
                except Exception as e:
                    print(f"   ❌ {file_path}: 読み込みエラー - {e}")
        else:
            print("   📝 生成されたファイルがありません")
    
    def show_progress_summary(self):
        """進捗サマリー表示"""
        print("\n📜 240秒タイムアウト処理ログ")
        print("-" * 40)
        
        if self.progress_log:
            print(f"総ログエントリ: {len(self.progress_log)}")
            
            # 重要なイベントを抽出
            important_events = [
                log for log in self.progress_log 
                if any(keyword in log for keyword in ["完了", "失敗", "エラー", "開始"])
            ]
            
            if important_events:
                print("\n重要なイベント:")
                for log in important_events:
                    print(f"   {log}")
        else:
            print("進捗ログはありません")
    
    async def run_calculator_demo(self):
        """電卓アプリ作成デモを実行"""
        try:
            # セットアップ
            await self.setup()
            
            # 電卓ソリューション生成
            calculator_results = await self.generate_calculator_solutions()
            
            if calculator_results:
                # タスク処理
                task_ids = self.process_calculator_tasks(calculator_results)
                
                # 生成されたファイルを表示
                self.show_generated_files()
            else:
                print("❌ 電卓ソリューションの生成に失敗しました")
            
            # 進捗サマリー
            self.show_progress_summary()
            
            print(f"\n🎉 240秒タイムアウト 電卓アプリ作成デモ完了！")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ デモ実行中にエラーが発生: {e}")
            import traceback
            traceback.print_exc()

# メイン実行
if __name__ == "__main__":
    demo = CalculatorDemo240s()
    asyncio.run(demo.run_calculator_demo())
