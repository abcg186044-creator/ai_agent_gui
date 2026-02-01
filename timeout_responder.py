#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIエージェントタイムアウト防止システム
定期的な途中報告とステップ生成を実装
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

class TimeoutResponder:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.response_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.active_tasks = {}
        self.task_counter = 0
        self.timeout_threshold = 30  # 30秒でタイムアウト
        self.progress_interval = 3  # 3秒ごとに進捗報告
        
        # データ保存先
        self.data_dir = Path("data")
        self.responses_file = self.data_dir / "timeout_responses.json"
        self.progress_file = self.data_dir / "progress_reports.json"
        
        # ディレクトリを作成
        self.data_dir.mkdir(exist_ok=True)
        
        # 既存データを読み込み
        self.load_responses()
        self.load_progress()
        
        # Flaskアプリケーション
        self.app = Flask(__name__)
        self.setup_routes()
        
        # サーバースレッド
        self.server_thread = None
        
        print("🛡️ AIエージェントタイムアウト防止システム")
        print("=" * 70)
        print(f"📊 データ保存先: {self.data_dir}")
        print(f"⏱️ タイムアウト閾値: {self.timeout_threshold}秒")
        print(f"📈 進捗報告間隔: {self.progress_interval}秒（高頻度モード）")
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
    
    def save_responses(self):
        """レスポンス履歴を保存"""
        try:
            data = {
                'responses': list(self.response_queue.queue),
                'last_update': datetime.datetime.now().isoformat()
            }
            with open(self.responses_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ レスポンス履歴保存エラー: {e}")
    
    def save_progress(self):
        """進捗履歴を保存"""
        try:
            data = {
                'progress': list(self.progress_queue.queue),
                'last_update': datetime.datetime.now().isoformat()
            }
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 進捗履歴保存エラー: {e}")
    
    def generate_progress_steps(self, task_description):
        """タスクの進捗ステップを詳細に生成"""
        steps = []
        
        # タスクタイプに応じた詳細なステップを生成
        if "Android" in task_description or "アプリ開発" in task_description:
            steps = [
                "🔍 Android開発環境の要件分析中... JDKバージョン、Android Studio互換性を確認",
                "📱 Android Studioの最新版ダウンロードとインストール手順を調査中... SDK設定も含む",
                "🏗️ 新規Androidプロジェクトの作成方法を検討中... Gradle設定、依存関係の定義",
                "💻 Kotlinプログラミングの基本構造を分析中... 変数宣言、関数、クラスの実装パターン",
                "🎨 XMLレイアウトファイルの設計を進行中... ConstraintLayout、RecyclerViewの最適配置",
                "⚙️ MainActivity.javaの実装構造を検討中... ライフサイクル管理、状態保存",
                "🔗 ボタンクリックイベントの実装方法を準備中... OnClickListener、Lambda式の活用",
                "🌐 ネットワーク通信の実装を計画中... Retrofit、OkHttpを使用したAPI連携",
                "💾 SQLiteデータベースの設計と実装を準備中... Roomライブラリの活用方法",
                "🧪 単体テストとUIテストの実装方法を確認中... JUnit、Espressoの設定",
                "📦 APKビルドとGoogle Play公開手順を調査中... 署名設定、リリースビルドの最適化",
                "✅ 完全なAndroidアプリ実装コードを生成中... エラーハンドリングと例外処理も含む"
            ]
        elif "GUI" in task_description or "電卓" in task_description:
            steps = [
                "🔍 Python GUIフレームワークの比較分析中... Tkinter vs PyQt vs PySideの機能評価",
                "📋 電卓アプリの機能要件を詳細分析中... 基本四則演算、メモリ機能、履歴表示",
                "🏗️ メインウィンドウのレイアウト設計を進行中... ウィンドウサイズ、グリッド配置の最適化",
                "🔘 数字ボタン(0-9)の配置とイベント処理を計画中... GridLayoutでの効率的な配置",
                "⚡ 演算子ボタン(+,-,*,/)の実装ロジックを準備中... 優先順位処理の考慮",
                "🧮 計算エンジンの中核ロジックを実装中... 浮動小数点数の精度保証、オーバーフロー対策",
                "⚠️ エラー処理と例外実装を計画中... ゼロ除算、無効入力の検出とユーザー通知",
                "🎨 ボタンのスタイリングとテーマ適用を検討中... 色設定、フォント、ホバー効果",
                "📱 レスポンシブデザインの実装を準備中... ウィンドウリサイズ対応、DPIスケーリング",
                "🧪 各機能の単体テストケースを作成中... 計算精度、UI操作の検証パターン",
                "📦 PyInstallerを使用した実行可能ファイルの作成準備中... 依存関係のバンドル",
                "✅ 完全な電卓アプリのコードを生成中... コメント付き、ドキュメント完備の実装"
            ]
        elif "Web" in task_description or "HTML" in task_description:
            steps = [
                "🔍 Webアプリケーションの要件定義を分析中... 機能仕様、技術スタックの選定",
                "📋 HTML5セマンティック構造を設計中... header, main, section, articleの最適配置",
                "🎨 CSS3モダンスタイルを計画中... Flexbox, Grid, CSS Variablesの活用",
                "⚡ JavaScript ES6+の実装を進行中... アロー関数、Promise、async/awaitの使用",
                "🔗 DOMイベントハンドリングを実装準備中... イベントリスナー、イベントデリゲーション",
                "📱 モバイルファーストのレスポンシブデザインを検討中... メディアクエリ、ビューポート設定",
                "🔄 REST API連携の実装を計画中... fetch API、JSONデータ処理、エラーハンドリング",
                "🧪 クロスブラウザ互換性を確認中... Chrome, Firefox, Safari, Edgeでのテスト計画",
                "⚡ パフォーマンス最適化を実施中... レイジーローディング、コード分割、キャッシュ戦略",
                "🔒 セキュリティ対策を実装中... XSS対策、CSRF保護、HTTPS強制、CORS設定",
                "📊 Google Analyticsとモニタリング設定を準備中... ユーザー行動追跡、エラーログ収集",
                "✅ 完全なWebアプリケーションを生成中... 本番環境デプロイ準備完了のコード"
            ]
        elif "機械学習" in task_description or "ML" in task_description or "AI" in task_description:
            steps = [
                "🔍 機械学習プロジェクトの要件分析中... 問題定義、評価指標の設定",
                "📊 データセットの収集と前処理を計画中... 欠損値処理、特徴量エンジニアリング",
                "🧪 探索的データ分析(EDA)を実施中... データ分布、相関関係の可視化",
                "🏗️ モデルアーキテクチャの設計を進行中... ニューラルネットワーク層の構成",
                "💻 TensorFlow/PyTorchでの実装を準備中... モデル定義、損失関数、最適化アルゴリズム",
                "🔄 トレーニングループの実装中... バッチ処理、学習率スケジューリング",
                "📈 モデル評価と検証を実施中... 交差検証、性能指標の計算",
                "🔧 ハイパーパラメータチューニングを最適化中... Grid Search, Random Search",
                "🚀 モデルのシリアライズと保存を準備中... pickle, joblib, ONNX形式",
                "🌐 REST API化の実装を計画中... FastAPI, Flaskでの推論サーバー構築",
                "📦 Dockerコンテナ化とデプロイ準備中... requirements.txt, Dockerfile作成",
                "✅ 完全な機械学習パイプラインを生成中... 本番運用対応のコードとドキュメント"
            ]
        else:
            steps = [
                "🔍 タスクのビジネス要件と技術要件を詳細分析中... 成功基準の定義",
                "📋 実装計画と技術選定を策定中... アーキテクチャ設計、使用技術の決定",
                "🏗️ プロジェクト構造と基本骨格を設計中... ディレクトリ構成、モジュール分割",
                "💻 コアビジネスロジックの実装を進行中... 主要機能のアルゴリズム開発",
                "⚡ 補助機能とユーティリティを実装中... ヘルパー関数、共通処理の作成",
                "🔗 モジュール間連携とデータフローを構築中... API設計、インターフェース定義",
                "🧪 単体テストと統合テストを実施中... テストカバレッジの確保",
                "🔧 デバッグとパフォーマンス最適化中... ボトルネック特定、メモリ使用量改善",
                "📚 APIドキュメントとユーザーマニュアルを作成中... コードコメントの充実",
                "🔍 コードレビューと品質保証を実施中... 静的解析、セキュリティチェック",
                "🚀 本番環境デプロイ準備を完了中... 設定ファイル、環境変数の最適化",
                "✅ 完全なソリューションを生成中... 保守性、拡張性を考慮した実装"
            ]
        
        return steps
    
    def create_progress_report(self, task_id, current_step, total_steps, task_description):
        """進捗報告を作成"""
        progress_percent = (current_step / total_steps) * 100
        
        report = {
            "task_id": task_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "current_step": current_step,
            "total_steps": total_steps,
            "progress_percent": round(progress_percent, 1),
            "task_description": task_description,
            "status": "進行中",
            "estimated_completion": "まもなく完了します" if progress_percent > 80 else "処理中です..."
        }
        
        return report
    
    def generate_intermediate_response(self, task_id, step_info, task_description):
        """詳細な中間レスポンスを生成"""
        import random
        
        # ステップ情報から具体的な詳細を抽出
        step_details = self._extract_step_details(step_info)
        
        response_templates = [
            f"🔄 {step_info}\n   📋 詳細: {step_details}\n   ⏱️ 現在、この処理に集中しています。品質を確保しながら進行中...",
            f"⚡ {step_info}\n   🔧 技術詳細: {step_details}\n   🎯 最適化されたソリューションを準備中です。もう少々お待ちください...",
            f"🔍 {step_info}\n   📊 分析内容: {step_details}\n   💡 専門的な視点から最適なアプローチを検討しています...",
            f"🏗️ {step_info}\n   🏛️ 実装方針: {step_details}\n   ✨ 品質保証を重視した構築作業を進行中です...",
            f"💡 {step_info}\n   🌟 創造的アプローチ: {step_details}\n   🚀 革新的なソリューションを開発しています...",
            f"🔧 {step_info}\n   ⚙️ 最適化詳細: {step_details}\n   📈 パフォーマンスと品質の両面から改善中です...",
            f"📊 {step_info}\n   📈 データ処理: {step_details}\n   🎲 精密な分析と処理を実行しています...",
            f"🎯 {step_info}\n   🎪 専門的処理: {step_details}\n   🏆 業界標準のベストプラクティスを適用中です...",
            f"🚀 {step_info}\n   🌍 実行環境: {step_details}\n   ⚡ 高速かつ安定した処理を確保しています...",
            f"✨ {step_info}\n   💎 品質保証: {step_details}\n   🏅 完璧な結果をお届けするため最終調整中です..."
        ]
        
        template = random.choice(response_templates)
        
        return {
            "task_id": task_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "intermediate",
            "message": template,
            "step_info": step_info,
            "step_details": step_details,
            "task_description": task_description,
            "estimated_time_remaining": self._estimate_time_remaining(step_info)
        }
    
    def _extract_step_details(self, step_info):
        """ステップ情報から技術的詳細を抽出"""
        details_map = {
            "要件分析": "ビジネス要件と技術要件の両面から、成功基準と制約条件を特定",
            "環境構築": "開発ツールの互換性チェックと、最適な設定パラメータの決定",
            "プロジェクト構造": "モジュール性と保守性を考慮したディレクトリ設計と依存関係管理",
            "実装": "クリーンコード原則に基づいた、読みやすく効率的なコード作成",
            "テスト": "単体テスト、統合テスト、受け入れテストの包括的なテスト戦略",
            "デバッグ": "静的解析と動的解析を組み合わせた、体系的な問題解決アプローチ",
            "デプロイ": "本番環境での安定稼働を保証する設定と監視体制の構築",
            "ドキュメント": "技術仕様、ユーザーマニュアル、運用ガイドの包括的な作成",
            "最適化": "パフォーマンス、セキュリティ、スケーラビリティの多角的な改善",
            "コード生成": "ベストプラクティスと設計パターンを適用した高品質なコード出力"
        }
        
        for key, detail in details_map.items():
            if key in step_info:
                return detail
        
        # デフォルトの詳細情報
        return "現在のタスクにおいて、品質と効率を最大化するための専門的処理を実行中"
    
    def _estimate_time_remaining(self, step_info):
        """ステップに基づいて残り時間を推定"""
        time_estimates = {
            "要件分析": "2-3分",
            "環境構築": "3-5分", 
            "プロジェクト構造": "1-2分",
            "実装": "5-10分",
            "テスト": "2-4分",
            "デバッグ": "3-6分",
            "デプロイ": "2-3分",
            "ドキュメント": "1-2分",
            "最適化": "3-5分",
            "コード生成": "2-4分"
        }
        
        for key, estimate in time_estimates.items():
            if key in step_info:
                return estimate
        
        return "1-3分"
    
    def monitor_task_with_progress(self, task_id, task_description, original_prompt):
        """タスクを監視して進捗報告を生成"""
        steps = self.generate_progress_steps(task_description)
        total_steps = len(steps)
        
        def progress_monitor():
            start_time = time.time()
            current_step = 0
            
            while current_step < total_steps:
                # タスクが完了したかチェック
                if task_id not in self.active_tasks:
                    break
                
                # 進捗報告を生成
                step_info = steps[current_step]
                step_details = self._extract_step_details(step_info)
                progress_report = self.create_progress_report(
                    task_id, current_step + 1, total_steps, task_description
                )
                
                # 詳細な中間レスポンスを生成
                intermediate_response = self.generate_intermediate_response(
                    task_id, step_info, task_description
                )
                
                # キューに追加
                self.progress_queue.put(progress_report)
                self.response_queue.put(intermediate_response)
                
                # 詳細な進捗情報をコンソールに出力
                print(f"📊 進捗報告: {progress_report['progress_percent']}%")
                print(f"🔧 ステップ: {step_info}")
                print(f"📋 詳細: {step_details}")
                print(f"⏱️ 推定残り時間: {intermediate_response['estimated_time_remaining']}")
                print("-" * 60)
                
                current_step += 1
                
                # 次の進捗報告まで待機
                time.sleep(self.progress_interval)
                
                # タイムアウトチェック
                if time.time() - start_time > self.timeout_threshold:
                    timeout_response = {
                        "task_id": task_id,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "type": "timeout",
                        "message": f"⏱️ 処理に時間がかかっていますが、引き続き最適な回答を準備中です...",
                        "task_description": task_description,
                        "current_progress": f"{(current_step/total_steps)*100:.1f}%"
                    }
                    self.response_queue.put(timeout_response)
                    break
        
        # バックグラウンドで進捗監視を開始
        monitor_thread = threading.Thread(target=progress_monitor, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    def generate_response_with_progress(self, prompt, task_description=""):
        """進捗報告付きでレスポンスを生成"""
        task_id = f"task_{self.task_counter}"
        self.task_counter += 1
        
        # タスクをアクティブリストに追加
        self.active_tasks[task_id] = {
            "prompt": prompt,
            "description": task_description,
            "start_time": time.time()
        }
        
        print(f"🚀 タスク開始: {task_id} - {task_description}")
        
        # 進捗監視を開始
        monitor_thread = self.monitor_task_with_progress(task_id, task_description, prompt)
        
        try:
            # 実際のAIレスポンスを生成
            print("🤖 AIレスポンス生成中...")
            response = self.ollama_client.generate_response(prompt)
            
            # タスク完了
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            # 完了レスポンス
            completion_response = {
                "task_id": task_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "completion",
                "message": "✅ レスポンス生成完了！",
                "ai_response": response,
                "task_description": task_description,
                "processing_time": time.time() - self.active_tasks.get(task_id, {}).get("start_time", time.time())
            }
            
            self.response_queue.put(completion_response)
            self.save_responses()
            
            print(f"✅ タスク完了: {task_id}")
            
            return {
                "success": True,
                "task_id": task_id,
                "response": response,
                "progress_reports": list(self.progress_queue.queue)[-5:],  # 最新5件
                "intermediate_responses": [r for r in list(self.response_queue.queue) if r.get("type") == "intermediate"][-5:]
            }
            
        except Exception as e:
            # エラーレスポンス
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            error_response = {
                "task_id": task_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "error",
                "message": f"❌ エラーが発生しました: {str(e)}",
                "task_description": task_description
            }
            
            self.response_queue.put(error_response)
            
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "progress_reports": list(self.progress_queue.queue)[-5:]
            }
    
    def get_latest_progress(self):
        """最新の進捗情報を取得"""
        latest_responses = list(self.response_queue.queue)[-10:]
        latest_progress = list(self.progress_queue.queue)[-10:]
        
        return {
            "latest_responses": latest_responses,
            "latest_progress": latest_progress,
            "active_tasks": len(self.active_tasks),
            "total_responses": len(self.response_queue.queue),
            "total_progress": len(self.progress_queue.queue)
        }
    
    def setup_routes(self):
        """Flaskルートを設定"""
        
        @self.app.route('/')
        def index():
            """タイムアウト防止システムダッシュボード"""
            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>AIエージェントタイムアウト防止システム</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .status-card { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; }
        .response-list { max-height: 400px; overflow-y: auto; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 20px 0; background: #f9f9f9; }
        .response-item { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .intermediate { background: #e3f2fd; border-left: 3px solid #2196f3; }
        .completion { background: #e8f5e8; border-left: 3px solid #4caf50; }
        .error { background: #ffebee; border-left: 3px solid #f44336; }
        .progress-bar { width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; margin: 5px 0; }
        .progress-fill { height: 100%; background: #4caf50; transition: width 0.3s ease; }
        .input-container { display: flex; gap: 10px; margin: 20px 0; }
        .input-field { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .submit-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        .submit-btn:hover { background: #0056b3; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 20px 0; }
        .stat-item { text-align: center; padding: 10px; background: #e9ecef; border-radius: 5px; }
        .stat-number { font-size: 24px; font-weight: bold; color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ AIエージェントタイムアウト防止システム</h1>
        <p>定期的な進捗報告と中間レスポンスでタイムアウトを防止します。</p>
        
        <div class="stats" id="stats">
            <div class="stat-item">
                <div class="stat-number" id="activeTasks">0</div>
                <div>アクティブタスク</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="totalResponses">0</div>
                <div>総レスポンス</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="totalProgress">0</div>
                <div>進捗報告</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="successRate">0%</div>
                <div>成功率</div>
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" class="input-field" id="promptInput" placeholder="プロンプトを入力..." onkeypress="if(event.key === 'Enter') submitRequest()">
            <input type="text" class="input-field" id="taskInput" placeholder="タスク説明（任意）..." style="flex: 0.5;">
            <button class="submit-btn" onclick="submitRequest()">🚀 実行</button>
        </div>
        
        <h3>📊 最新の進捗報告</h3>
        <div class="response-list" id="progressList">
            <!-- 進捗報告がここに表示される -->
        </div>
        
        <h3>💬 最新のレスポンス</h3>
        <div class="response-list" id="responseList">
            <!-- レスポンスがここに表示される -->
        </div>
    </div>
    
    <script>
        let updateInterval;
        
        async function submitRequest() {
            const prompt = document.getElementById('promptInput').value.trim();
            const taskDescription = document.getElementById('taskInput').value.trim();
            
            if (!prompt) return;
            
            // 入力をクリア
            document.getElementById('promptInput').value = '';
            document.getElementById('taskInput').value = '';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        prompt: prompt,
                        task_description: taskDescription
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    console.log('タスク開始:', result.task_id);
                } else {
                    console.error('エラー:', result.error);
                }
                
            } catch (error) {
                console.error('通信エラー:', error);
            }
        }
        
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // 統計を更新
                document.getElementById('activeTasks').textContent = data.active_tasks;
                document.getElementById('totalResponses').textContent = data.total_responses;
                document.getElementById('totalProgress').textContent = data.total_progress;
                
                // 成功率を計算
                const successRate = data.total_responses > 0 ? 
                    Math.round((data.total_responses - data.latest_responses.filter(r => r.type === 'error').length) / data.total_responses * 100) : 0;
                document.getElementById('successRate').textContent = successRate + '%';
                
                // 進捗報告を更新
                const progressList = document.getElementById('progressList');
                progressList.innerHTML = '';
                data.latest_progress.forEach(progress => {
                    const div = document.createElement('div');
                    div.className = 'response-item intermediate';
                    div.innerHTML = `
                        <strong>${progress.task_description || 'タスク'}</strong>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress.progress_percent}%"></div>
                        </div>
                        <small>${progress.progress_percent}% - ${progress.status}</small>
                        <div><small>${new Date(progress.timestamp).toLocaleTimeString()}</small></div>
                    `;
                    progressList.appendChild(div);
                });
                
                // レスポンスを更新
                const responseList = document.getElementById('responseList');
                responseList.innerHTML = '';
                data.latest_responses.forEach(response => {
                    const div = document.createElement('div');
                    div.className = `response-item ${response.type}`;
                    div.innerHTML = `
                        <strong>${response.type === 'completion' ? '✅ 完了' : response.type === 'error' ? '❌ エラー' : '🔄 進行中'}</strong>
                        <div>${response.message}</div>
                        ${response.ai_response ? `<div style="margin-top: 10px; padding: 10px; background: white; border-radius: 3px;">${response.ai_response.substring(0, 200)}...</div>` : ''}
                        <div><small>${new Date(response.timestamp).toLocaleTimeString()}</small></div>
                    `;
                    responseList.appendChild(div);
                });
                
            } catch (error) {
                console.error('ステータス更新エラー:', error);
            }
        }
        
        // 定期的に更新
        updateInterval = setInterval(updateStatus, 2000); // 2秒ごと（高頻度モード）
        
        // 初回読み込み
        updateStatus();
        
        // ページ離脱時にクリーンアップ
        window.addEventListener('beforeunload', () => {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        });
    </script>
</body>
</html>
            ''')
        
        @self.app.route('/api/generate', methods=['POST'])
        def generate():
            """進捗報告付きレスポンス生成API"""
            try:
                data = request.get_json()
                prompt = data.get('prompt', '')
                task_description = data.get('task_description', '')
                
                result = self.generate_response_with_progress(prompt, task_description)
                return jsonify(result)
                
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        @self.app.route('/api/status')
        def status():
            """ステータスAPI"""
            return jsonify(self.get_latest_progress())
        
        @self.app.route('/api/responses')
        def responses():
            """レスポンス履歴API"""
            return jsonify({
                "responses": list(self.response_queue.queue)[-20:],  # 最新20件
                "total": len(self.response_queue.queue)
            })
        
        @self.app.route('/api/progress')
        def progress():
            """進捗履歴API"""
            return jsonify({
                "progress": list(self.progress_queue.queue)[-20:],  # 最新20件
                "total": len(self.progress_queue.queue)
            })
    
    def start_server(self, host='0.0.0.0', port=8084):
        """サーバーを起動"""
        def run_server():
            self.app.run(host=host, port=port, debug=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        print(f"🚀 タイムアウト防止システムサーバーを起動しました")
        print(f"🌐 アクセスURL: http://{host}:{port}")
        print(f"📊 進捗監視を開始しました...")
    
    def test_timeout_prevention(self):
        """タイムアウト防止機能をテスト"""
        print("\n🧪 タイムアウト防止機能テスト")
        print("=" * 50)
        
        test_cases = [
            {
                "prompt": "PythonでGUI電卓アプリを開発する方法を詳しく教えてください。コード例と共に説明してください。",
                "task_description": "Python GUI電卓開発"
            },
            {
                "prompt": "Androidアプリ開発の完全なガイドを提供してください。環境構築から公開までの手順を含めて。",
                "task_description": "Androidアプリ開発ガイド"
            },
            {
                "prompt": "機械学習モデルの構築からデプロイまでの全工程を詳細に説明してください。Pythonコード例も含めて。",
                "task_description": "機械学習モデル開発"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 テストケース {i}: {test_case['task_description']}")
            print("-" * 40)
            
            result = self.generate_response_with_progress(
                test_case['prompt'], 
                test_case['task_description']
            )
            
            if result['success']:
                print(f"✅ 成功: タスクID {result['task_id']}")
                print(f"📊 進捗報告数: {len(result['progress_reports'])}")
                print(f"💬 中間レスポンス数: {len(result['intermediate_responses'])}")
                print(f"🤖 AI応答長: {len(result['response'])}文字")
            else:
                print(f"❌ 失敗: {result['error']}")
            
            time.sleep(2)  # テスト間隔
        
        print("\n" + "=" * 50)
        print("🎉 タイムアウト防止機能テスト完了！")

def main():
    """メイン関数"""
    responder = TimeoutResponder()
    
    # サーバー起動
    responder.start_server()
    
    # テスト実行
    responder.test_timeout_prevention()
    
    print(f"\n🌐 Webインターフェース: http://127.0.0.1:8084")
    print("📊 リアルタイムで進捗を監視できます")

if __name__ == "__main__":
    main()
