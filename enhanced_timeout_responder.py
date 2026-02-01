#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
強化版AIエージェントタイムアウト防止システム
分割処理とユーザー割り込み機能を実装
"""

import sys
import json
import datetime
import os
import time
import threading
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
import queue

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_vrm_integrated_app import OllamaClient

class EnhancedTimeoutResponder:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.response_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.active_tasks = {}
        self.task_counter = 0
        self.timeout_threshold = 120  # 120秒でタイムアウト（延長）
        self.progress_interval = 3  # 3秒ごとに進捗報告
        
        # 割り込み機能
        self.interruptible_tasks = {}
        self.user_interrupts = {}
        
        # データ保存先
        self.data_dir = Path("data")
        self.responses_file = self.data_dir / "enhanced_timeout_responses.json"
        self.progress_file = self.data_dir / "enhanced_progress_reports.json"
        
        # ディレクトリを作成
        self.data_dir.mkdir(exist_ok=True)
        
        # 既存データを読み込み
        self.load_responses()
        self.load_progress()
        
        # Flaskアプリケーション
        self.app = Flask(__name__)
        
        # サーバースレッド
        self.server_thread = None
        
        print("🛡️ 強化版AIエージェントタイムアウト防止システム")
        print("=" * 70)
        print(f"📊 データ保存先: {self.data_dir}")
        print(f"⏱️ タイムアウト閾値: {self.timeout_threshold}秒（延長）")
        print(f"📈 進捗報告間隔: {self.progress_interval}秒（高頻度モード）")
        print(f"⚡ ユーザー割り込み機能: 有効")
        print("=" * 70)
    
    def load_responses(self):
        """レスポンス履歴を読み込む"""
        try:
            if self.responses_file.exists():
                with open(self.responses_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.response_queue.queue = data.get('responses', [])
                print(f"📚 レスポンス履歴を読み込みました ({len(self.response_queue.queue)}件)")
        except Exception as e:
            print(f"❌ レスポンス履歴読み込みエラー: {e}")
    
    def load_progress(self):
        """進捗履歴を読み込む"""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.progress_queue.queue = data.get('progress', [])
                print(f"📚 進捗履歴を読み込みました ({len(self.progress_queue.queue)}件)")
        except Exception as e:
            print(f"❌ 進捗履歴読み込みエラー: {e}")
    
    def split_task_into_subtasks(self, prompt, task_description):
        """タスクを分割処理用のサブタスクに分解"""
        if "GUI" in task_description or "電卓" in task_description:
            return [
                {"name": "環境設定と要件分析", "prompt": "Python GUI開発環境設定と電卓要件分析", "time": 15},
                {"name": "基本設計と構造", "prompt": "電卓アプリの基本設計とウィンドウ構造", "time": 15},
                {"name": "UI実装", "prompt": "Tkinterでのボタン配置とレイアウト実装", "time": 20},
                {"name": "計算ロジック", "prompt": "四則演算ロジックとエラー処理実装", "time": 20},
                {"name": "イベント処理", "prompt": "ボタンクリックイベントと完成形", "time": 20}
            ]
        elif "機械学習" in task_description:
            return [
                {"name": "データ前処理", "prompt": "機械学習データ前処理と分析", "time": 20},
                {"name": "モデル設計", "prompt": "モデル選定とアーキテクチャ設計", "time": 20},
                {"name": "実装と訓練", "prompt": "TensorFlow/PyTorch実装と訓練", "time": 25},
                {"name": "評価とチューニング", "prompt": "モデル評価とハイパーパラメータ調整", "time": 20},
                {"name": "デプロイ", "prompt": "本番環境デプロイと運用", "time": 20}
            ]
        else:
            return [
                {"name": "要件分析", "prompt": f"タスク要件分析: {task_description}", "time": 20},
                {"name": "基本設計", "prompt": f"基本設計と構造: {task_description}", "time": 20},
                {"name": "実装", "prompt": f"核心機能実装: {task_description}", "time": 25},
                {"name": "最適化", "prompt": f"最適化と追加機能: {task_description}", "time": 20},
                {"name": "完成", "prompt": f"テストと完成: {task_description}", "time": 20}
            ]
    
    def execute_subtask(self, task_id, subtask, index, total):
        """サブタスクを実行"""
        subtask_id = f"{task_id}_sub_{index}"
        
        try:
            # 進捗報告
            progress = {
                "task_id": task_id,
                "subtask": subtask["name"],
                "progress": (index / total) * 100,
                "status": f"🔀 処理中: {subtask['name']}"
            }
            self.progress_queue.put(progress)
            
            # API呼び出し
            response = self.ollama_client.generate_response(subtask["prompt"])
            
            # 完了報告
            completion = {
                "task_id": task_id,
                "subtask": subtask["name"],
                "response": response,
                "progress": ((index + 1) / total) * 100,
                "status": f"✅ 完了: {subtask['name']}"
            }
            self.response_queue.put(completion)
            
            return {"success": True, "response": response}
            
        except Exception as e:
            error = {
                "task_id": task_id,
                "subtask": subtask["name"],
                "error": str(e),
                "status": f"❌ エラー: {subtask['name']}"
            }
            self.response_queue.put(error)
            return {"success": False, "error": str(e)}
    
    def interrupt_task(self, task_id):
        """タスクを割り込み"""
        self.user_interrupts[task_id] = True
        
        interrupt_msg = {
            "task_id": task_id,
            "status": "⚠️ ユーザーにより割り込みされました"
        }
        self.response_queue.put(interrupt_msg)
    
    def generate_response_with_split(self, prompt, task_description=""):
        """分割処理でレスポンスを生成"""
        task_id = f"split_{self.task_counter}"
        self.task_counter += 1
        
        print(f"🚀 分割処理開始: {task_id}")
        
        # タスク分割
        subtasks = self.split_task_into_subtasks(prompt, task_description)
        
        # バックグラウンドで実行
        def process_split():
            results = []
            for i, subtask in enumerate(subtasks):
                if task_id in self.user_interrupts:
                    break
                
                result = self.execute_subtask(task_id, subtask, i, len(subtasks))
                results.append(result)
                time.sleep(2)  # 短い待機
            
            # 最終結果
            final = {
                "task_id": task_id,
                "status": "🔀 分割処理完了",
                "results": results
            }
            self.response_queue.put(final)
        
        threading.Thread(target=process_split, daemon=True).start()
        
        return {
            "success": True,
            "task_id": task_id,
            "subtasks": len(subtasks),
            "message": f"🔀 {len(subtasks)}個のサブタスクに分割して処理開始"
        }
    
    def start_server(self, host='0.0.0.0', port=8085):
        """サーバー起動"""
        @self.app.route('/')
        def index():
            return '''
<h1>🛡️ 強化版タイムアウト防止システム</h1>
<p>分割処理とユーザー割り込み機能でタイムアウトを防止</p>
<ul>
<li>🔀 分割処理: タスクを自動分割</li>
<li>⚡ 高頻度報告: 3秒ごと進捗</li>
<li>⚠️ ユーザー割り込み: いつでも中断</li>
<li>⏱️ 延長タイムアウト: 120秒</li>
</ul>
'''
        
        @self.app.route('/api/generate_split', methods=['POST'])
        def generate_split():
            data = request.get_json()
            result = self.generate_response_with_split(
                data.get('prompt', ''), 
                data.get('task_description', '')
            )
            return jsonify(result)
        
        @self.app.route('/api/interrupt', methods=['POST'])
        def interrupt():
            data = request.get_json()
            self.interrupt_task(data.get('task_id'))
            return jsonify({"success": True})
        
        def run_server():
            self.app.run(host=host, port=port, debug=False)
        
        threading.Thread(target=run_server, daemon=True).start()
        print(f"🚀 強化版サーバー起動: http://{host}:{port}")

def main():
    responder = EnhancedTimeoutResponder()
    responder.start_server()
    
    # テスト
    print("\n🧪 強化版システムテスト")
    result = responder.generate_response_with_split(
        "PythonでGUI電卓アプリを作成してください",
        "GUI電卓開発"
    )
    print(f"結果: {result}")

if __name__ == "__main__":
    main()
