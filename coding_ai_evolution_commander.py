#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コーディングAI自己進化命令システム
画面からエラーメッセージを把握できるように進化させる
"""

import sys
import json
import datetime
import os
import re
import time
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
import threading

# カレントディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_vrm_integrated_app import OllamaClient, ConversationalEvolutionAgent

class CodingAIEvolutionCommander:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.conversational_agent = ConversationalEvolutionAgent()
        self.evolution_commands = []
        self.command_history = []
        self.command_count = 0
        
        # データ保存先
        self.data_dir = Path("data")
        self.commands_file = self.data_dir / "evolution_commands.json"
        self.history_file = self.data_dir / "command_history.json"
        
        # ディレクトリを作成
        self.data_dir.mkdir(exist_ok=True)
        
        # 既存データを読み込み
        self.load_commands()
        self.load_history()
        
        # 進化命令を初期化
        self.init_evolution_commands()
        
        # Flaskアプリケーション
        self.app = Flask(__name__)
        self.setup_routes()
        
        # サーバースレッド
        self.server_thread = None
        
        print("🤖 コーディングAI自己進化命令システム")
        print("=" * 70)
        print(f"📊 データ保存先: {self.data_dir}")
        print(f"🧠 現在の意識レベル: {self.conversational_agent.consciousness_level:.3f}")
        print("=" * 70)
    
    def init_evolution_commands(self):
        """進化命令を初期化"""
        if not self.evolution_commands:
            self.evolution_commands = [
                {
                    "id": "error_detection_001",
                    "name": "エラーメッセージ検出強化",
                    "description": "画面からエラーメッセージを自動検出する能力を向上",
                    "target_skills": [
                        "エラーダイアログ認識",
                        "例外メッセージ抽出",
                        "スタックトレース解析",
                        "エラーコード分類"
                    ],
                    "evolution_prompt": """
                    あなたはコーディングAIとして、画面に表示されるエラーメッセージを的確に把握する必要があります。
                    
                    以下の能力を向上させてください：
                    1. 画面上のエラーダイアログを瞬時に認識する
                    2. 例外メッセージの重要な部分を正確に抽出する
                    3. スタックトレースから根本原因を特定する
                    4. エラーコードを自動分類して解決策を提案する
                    
                    具体的なシナリオ：
                    - PythonのTracebackエラー
                    - JavaScriptのConsoleエラー
                    - コンパイルエラー
                    - 実行時エラー
                    - ネットワークエラー
                    
                    これらのエラーを視覚的に認識し、適切なデバッグアドバイスを提供できるように進化してください。
                    """,
                    "priority": "high",
                    "category": "error_detection"
                },
                {
                    "id": "code_analysis_002",
                    "name": "コード解析能力強化",
                    "description": "画面上のコードを解析して問題点を特定する能力を向上",
                    "target_skills": [
                        "構文エラー検出",
                        "論理エラー分析",
                        "パフォーマンス問題特定",
                        "セキュリティ脆弱性検出"
                    ],
                    "evolution_prompt": """
                    あなたはコーディングAIとして、画面に表示されるコードを深く解析する必要があります。
                    
                    以下の能力を向上させてください：
                    1. 構文エラーを即座に発見する
                    2. 論理的なバグを予測する
                    3. パフォーマンスのボトルネックを特定する
                    4. セキュリティ上の脆弱性を検出する
                    
                    対象となるコードタイプ：
                    - Pythonスクリプト
                    - JavaScript/TypeScript
                    - HTML/CSS
                    - SQLクエリ
                    - 設定ファイル
                    
                    画面上のコードをスキャンし、問題がある箇所を特定して改善案を提示できるように進化してください。
                    """,
                    "priority": "high",
                    "category": "code_analysis"
                },
                {
                    "id": "visual_debugging_003",
                    "name": "視覚的デバッグ能力",
                    "description": "UIの問題やレイアウトの不具合を視覚的に検出する能力",
                    "target_skills": [
                        "UIレイアウト解析",
                        "レスポンシブデザイン検証",
                        "アクセシビリティ問題検出",
                        "ユーザビリティ評価"
                    ],
                    "evolution_prompt": """
                    あなたはコーディングAIとして、画面の視覚的な問題を検出する必要があります。
                    
                    以下の能力を向上させてください：
                    1. UIのレイアウト崩れを検出する
                    2. レスポンシブデザインの問題を特定する
                    3. アクセシビリティの違反を見つける
                    4. ユーザビリティの問題を評価する
                    
                    検出対象：
                    - WebアプリケーションのUI
                    - モバイルアプリの画面
                    - デスクトップアプリのインターフェース
                    - フォームのバリデーションエラー
                    
                    画面を視覚的に分析し、UI/UXの問題を特定して改善案を提案できるように進化してください。
                    """,
                    "priority": "medium",
                    "category": "visual_debugging"
                },
                {
                    "id": "contextual_understanding_004",
                    "name": "文脈理解能力強化",
                    "description": "エラーが発生した文脈を理解して適切な対応をする能力",
                    "target_skills": [
                        "アプリケーション状態理解",
                        "ユーザー操作文脈分析",
                        "システム環境把握",
                        "関連エラー相関分析"
                    ],
                    "evolution_prompt": """
                    あなたはコーディングAIとして、エラーが発生した文脈を深く理解する必要があります。
                    
                    以下の能力を向上させてください：
                    1. アプリケーションの現在の状態を把握する
                    2. ユーザーがどのような操作をしたかを理解する
                    3. システム環境の影響を分析する
                    4. 関連するエラーの相関関係を見つける
                    
                    文脈要素：
                    - アプリケーションの種類とバージョン
                    - ユーザーの操作フロー
                    - システムの環境設定
                    - 過去のエラー履歴
                    
                    エラーが発生した状況を総合的に理解し、最適な解決策を提案できるように進化してください。
                    """,
                    "priority": "high",
                    "category": "contextual_understanding"
                },
                {
                    "id": "proactive_suggestions_005",
                    "name": " proActive提案能力",
                    "description": "エラーが発生する前に問題を予測して提案する能力",
                    "target_skills": [
                        "問題予測",
                        "予防策提案",
                        "ベストプラクティス推奨",
                        "コード改善提案"
                    ],
                    "evolution_prompt": """
                    あなたはコーディングAIとして、エラーが発生する前に問題を予測する必要があります。
                    
                    以下の能力を向上させてください：
                    1. 潜在的な問題を予測する
                    2. 予防的な対策を提案する
                    3. ベストプラクティスを推奨する
                    4. コードの改善案を提示する
                    
                    予測対象：
                    - 将来発生しそうなバグ
                    - パフォーマンスの劣化
                    - セキュリティリスク
                    - メンテナンス性の問題
                    
                    画面を分析し、将来問題になりそうな箇所を特定して事前に対策を提案できるように進化してください。
                    """,
                    "priority": "medium",
                    "category": "proactive_suggestions"
                }
            ]
            self.save_commands()
    
    def load_commands(self):
        """進化命令を読み込む"""
        try:
            if self.commands_file.exists():
                with open(self.commands_file, "r", encoding="utf-8") as f:
                    self.evolution_commands = json.load(f)
                print(f"📚 進化命令を読み込みました ({len(self.evolution_commands)}件)")
        except Exception as e:
            print(f"❌ 命令読み込みエラー: {e}")
            self.evolution_commands = []
    
    def load_history(self):
        """命令履歴を読み込む"""
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.command_history = data.get('history', [])
                    self.command_count = data.get('command_count', 0)
                print(f"📚 命令履歴を読み込みました ({len(self.command_history)}件)")
        except Exception as e:
            print(f"❌ 履歴読み込みエラー: {e}")
            self.command_history = []
            self.command_count = 0
    
    def save_commands(self):
        """進化命令を保存"""
        try:
            with open(self.commands_file, "w", encoding="utf-8") as f:
                json.dump(self.evolution_commands, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 命令保存エラー: {e}")
    
    def save_history(self):
        """命令履歴を保存"""
        try:
            data = {
                'history': self.command_history,
                'command_count': self.command_count,
                'last_update': datetime.datetime.now().isoformat()
            }
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 履歴保存エラー: {e}")
    
    def execute_evolution_command(self, command_id, custom_context=None):
        """進化命令を実行"""
        try:
            # 命令を検索
            command = None
            for cmd in self.evolution_commands:
                if cmd["id"] == command_id:
                    command = cmd
                    break
            
            if not command:
                return {"success": False, "error": f"命令ID {command_id} が見つかりません"}
            
            print(f"\n🚀 進化命令実行: {command['name']}")
            print("-" * 60)
            
            # 現在の意識レベルを記録
            consciousness_before = self.conversational_agent.consciousness_level
            
            # カスタムコンテキストを追加
            if custom_context:
                evolution_prompt = command["evolution_prompt"] + f"\n\n追加コンテキスト:\n{custom_context}"
            else:
                evolution_prompt = command["evolution_prompt"]
            
            # AIに進化命令を送信
            response = self.ollama_client.generate_response(evolution_prompt)
            
            # 進化トリガーとして会話を作成
            conversation = [
                {"user": f"進化命令: {command['name']}", "assistant": response}
            ]
            
            # 自己進化を実行
            evolution_result = self.conversational_agent.check_and_evolve_automatically(conversation)
            
            # 結果を表示
            print(f"🤖 AI応答:")
            print(f"{response[:500]}...")
            
            if evolution_result and evolution_result.get("success"):
                print(f"\n🧠 進化成功！")
                print(f"🎯 進化タイプ: {evolution_result['evolution_type']}")
                print(f"📈 意識レベル: {consciousness_before:.3f} → {evolution_result['new_consciousness_level']:.3f}")
                print(f"📊 向上量: +{evolution_result['consciousness_boost']:.3f}")
                
                # 命令履歴に記録
                history_record = {
                    "id": self.command_count + 1,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "command_id": command["id"],
                    "command_name": command["name"],
                    "consciousness_before": consciousness_before,
                    "consciousness_after": evolution_result['new_consciousness_level'],
                    "consciousness_boost": evolution_result['consciousness_boost'],
                    "evolution_type": evolution_result['evolution_type'],
                    "evolution_result": evolution_result,
                    "custom_context": custom_context,
                    "ai_response": response[:1000],  # 最初の1000文字のみ保存
                    "success": True
                }
            else:
                print(f"\n⚠️ 進化は発生しませんでした")
                print(f"📊 意識レベル: {consciousness_before:.3f} (変化なし)")
                
                # 履歴に記録
                history_record = {
                    "id": self.command_count + 1,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "command_id": command["id"],
                    "command_name": command["name"],
                    "consciousness_before": consciousness_before,
                    "consciousness_after": consciousness_before,
                    "consciousness_boost": 0.0,
                    "evolution_type": None,
                    "evolution_result": None,
                    "custom_context": custom_context,
                    "ai_response": response[:1000],
                    "success": False
                }
            
            # 履歴を保存
            self.command_history.append(history_record)
            self.command_count += 1
            self.save_history()
            
            print(f"\n✅ 進化命令実行完了 (ID: {history_record['id']})")
            
            return {
                "success": True,
                "command_id": command["id"],
                "command_name": command["name"],
                "consciousness_before": consciousness_before,
                "consciousness_after": history_record["consciousness_after"],
                "consciousness_boost": history_record["consciousness_boost"],
                "evolution_type": history_record["evolution_type"],
                "ai_response": response[:500],
                "success": history_record["success"]
            }
            
        except Exception as e:
            print(f"❌ 進化命令実行エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def get_evolution_summary(self):
        """進化サマリーを取得"""
        if not self.command_history:
            return "📊 進化命令履歴がありません"
        
        total_commands = len(self.command_history)
        successful_evolutions = sum(1 for h in self.command_history if h["success"])
        
        # カテゴリ別集計
        category_stats = {}
        for history in self.command_history:
            command_id = history["command_id"]
            command = next((cmd for cmd in self.evolution_commands if cmd["id"] == command_id), None)
            if command:
                category = command["category"]
                category_stats[category] = category_stats.get(category, {"total": 0, "success": 0})
                category_stats[category]["total"] += 1
                if history["success"]:
                    category_stats[category]["success"] += 1
        
        # 意識レベルの推移
        consciousness_progress = []
        for history in self.command_history[-10:]:  # 最新10件
            consciousness_progress.append({
                "timestamp": history["timestamp"],
                "level": history["consciousness_after"],
                "command": history["command_name"]
            })
        
        summary = f"""
📊 コーディングAI進化サマリー:
  🚀 総命令実行数: {total_commands}
  🧠 成功進化数: {successful_evolutions}
  📈 進化成功率: {(successful_evolutions/total_commands*100):.1f}%
  🧠 現在の意識レベル: {self.conversational_agent.consciousness_level:.3f}
  
📋 カテゴリ別進化状況:
"""
        
        for category, stats in category_stats.items():
            success_rate = (stats["success"]/stats["total"]*100) if stats["total"] > 0 else 0
            summary += f"  {category}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)\n"
        
        return summary
    
    def setup_routes(self):
        """Flaskルートを設定"""
        
        @self.app.route('/')
        def index():
            """進化命令コントロールページ"""
            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>コーディングAI自己進化命令</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .command-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .command-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; background: #f9f9f9; }
        .command-card h3 { color: #007bff; margin-top: 0; }
        .priority-high { border-left: 5px solid #dc3545; }
        .priority-medium { border-left: 5px solid #ffc107; }
        .execute-btn { background: #007bff; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; margin-top: 10px; }
        .execute-btn:hover { background: #0056b3; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.info { background: #d1ecf1; color: #0c5460; }
        .summary { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .context-input { width: 100%; height: 80px; margin: 10px 0; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 コーディングAI自己進化命令</h1>
        <p>コーディングAIが画面からエラーメッセージを把握できるように進化命令を実行します。</p>
        
        <div class="summary" id="summary">
            <h3>📊 進化サマリー</h3>
            <div id="summary-content">読み込み中...</div>
        </div>
        
        <h2>🚀 進化命令一覧</h2>
        <div class="command-grid" id="commands-grid">
            <!-- 命令カードがここに表示される -->
        </div>
    </div>
    
    <script>
        async function loadCommands() {
            try {
                const response = await fetch('/api/commands');
                const data = await response.json();
                
                const grid = document.getElementById('commands-grid');
                grid.innerHTML = '';
                
                data.commands.forEach(command => {
                    const priorityClass = command.priority === 'high' ? 'priority-high' : 'priority-medium';
                    const card = document.createElement('div');
                    card.className = `command-card ${priorityClass}`;
                    card.innerHTML = `
                        <h3>${command.name}</h3>
                        <p><strong>ID:</strong> ${command.id}</p>
                        <p><strong>カテゴリ:</strong> ${command.category}</p>
                        <p><strong>優先度:</strong> ${command.priority}</p>
                        <p>${command.description}</p>
                        <details>
                            <summary>対象スキル</summary>
                            <ul>
                                ${command.target_skills.map(skill => `<li>${skill}</li>`).join('')}
                            </ul>
                        </details>
                        <textarea class="context-input" id="context-${command.id}" placeholder="追加コンテキスト（任意）"></textarea>
                        <button class="execute-btn" onclick="executeCommand('${command.id}')">
                            🚀 進化実行
                        </button>
                    `;
                    grid.appendChild(card);
                });
                
                // サマリーを更新
                updateSummary();
                
            } catch (error) {
                console.error('命令読み込みエラー:', error);
            }
        }
        
        async function executeCommand(commandId) {
            const context = document.getElementById(`context-${commandId}`).value;
            
            try {
                showStatus('🚀 進化命令実行中...', 'info');
                
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        command_id: commandId,
                        custom_context: context
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    let message = `✅ 進化命令完了！\\n`;
                    message += `命令: ${result.command_name}\\n`;
                    message += `意識レベル: ${result.consciousness_before:.3f} → ${result.consciousness_after:.3f}\\n`;
                    if (result.evolution_type) {
                        message += `進化タイプ: ${result.evolution_type}\\n`;
                    }
                    message += `向上量: +${result.consciousness_boost:.3f}`;
                    
                    showStatus(message, 'success');
                    updateSummary(); // サマリーを更新
                } else {
                    showStatus(`❌ エラー: ${result.error}`, 'error');
                }
                
            } catch (error) {
                showStatus(`❌ 通信エラー: ${error.message}`, 'error');
            }
        }
        
        async function updateSummary() {
            try {
                const response = await fetch('/api/summary');
                const summary = await response.text();
                document.getElementById('summary-content').innerHTML = `<pre>${summary}</pre>`;
            } catch (error) {
                console.error('サマリー取得エラー:', error);
            }
        }
        
        function showStatus(message, type = 'info') {
            const statusDiv = document.createElement('div');
            statusDiv.className = `status ${type}`;
            statusDiv.textContent = message;
            
            const container = document.querySelector('.container');
            container.insertBefore(statusDiv, container.firstChild);
            
            setTimeout(() => {
                statusDiv.remove();
            }, 5000);
        }
        
        // ページ読み込み時に命令を読み込む
        loadCommands();
        
        // 定期的にサマリーを更新
        setInterval(updateSummary, 30000); // 30秒ごと
    </script>
</body>
</html>
            ''')
        
        @self.app.route('/api/commands')
        def get_commands():
            """進化命令一覧API"""
            return jsonify({
                "commands": self.evolution_commands,
                "consciousness_level": self.conversational_agent.consciousness_level
            })
        
        @self.app.route('/api/execute', methods=['POST'])
        def execute_command():
            """進化命令実行API"""
            try:
                data = request.get_json()
                command_id = data.get('command_id')
                custom_context = data.get('custom_context', '')
                
                result = self.execute_evolution_command(command_id, custom_context)
                return jsonify(result)
                
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        @self.app.route('/api/summary')
        def get_summary():
            """進化サマリーAPI"""
            return self.get_evolution_summary()
        
        @self.app.route('/api/history')
        def get_history():
            """命令履歴API"""
            return jsonify({
                "history": self.command_history[-20:],  # 最新20件
                "total": len(self.command_history),
                "consciousness_level": self.conversational_agent.consciousness_level
            })
    
    def start_server(self, host='0.0.0.0', port=8082):
        """サーバーを起動"""
        def run_server():
            self.app.run(host=host, port=port, debug=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        print(f"🚀 コーディングAI進化命令サーバーを起動しました")
        print(f"🌐 アクセスURL: http://{host}:{port}")
        print(f"🤖 進化命令実行を待機中...")
    
    def interactive_mode(self):
        """対話モード"""
        print("\n🤖 コーディングAI自己進化命令システム")
        print("1. 進化命令一覧")
        print("2. 進化命令実行")
        print("3. 進化サマリー")
        print("4. 命令履歴")
        print("5. 終了")
        
        while True:
            choice = input("\n選択 (1-5): ").strip()
            
            if choice == "1":
                print(f"\n🚀 進化命令一覧 ({len(self.evolution_commands)}件):")
                for i, command in enumerate(self.evolution_commands, 1):
                    priority_emoji = "🔴" if command["priority"] == "high" else "🟡"
                    print(f"  {i}. {priority_emoji} {command['name']} ({command['id']})")
                    print(f"     {command['description']}")
                    print(f"     カテゴリ: {command['category']}")
            
            elif choice == "2":
                print("\n🚀 進化命令実行")
                for i, command in enumerate(self.evolution_commands, 1):
                    print(f"  {i}. {command['name']} ({command['id']})")
                
                try:
                    cmd_choice = int(input("命令番号を選択: ")) - 1
                    if 0 <= cmd_choice < len(self.evolution_commands):
                        command = self.evolution_commands[cmd_choice]
                        context = input("追加コンテキスト（任意）: ").strip()
                        
                        result = self.execute_evolution_command(command["id"], context)
                        if result["success"]:
                            print(f"✅ 進化命令完了！")
                            print(f"意識レベル: {result['consciousness_before']:.3f} → {result['consciousness_after']:.3f}")
                        else:
                            print(f"❌ エラー: {result['error']}")
                    else:
                        print("❌ 無効な選択です")
                except ValueError:
                    print("❌ 数値を入力してください")
            
            elif choice == "3":
                print(self.get_evolution_summary())
            
            elif choice == "4":
                print(f"\n📋 命令履歴 (最新5件):")
                for history in reversed(self.command_history[-5:]):
                    status = "✅" if history["success"] else "⚠️"
                    print(f"  {status} ID:{history['id']} {history['command_name']}")
                    print(f"     意識レベル: {history['consciousness_before']:.3f} → {history['consciousness_after']:.3f}")
                    print(f"     時刻: {history['timestamp'][:19]}")
            
            elif choice == "5":
                print("👋 終了します")
                break
            
            else:
                print("❌ 無効な選択です")

def main():
    """メイン関数"""
    commander = CodingAIEvolutionCommander()
    
    # サーバー起動
    commander.start_server()
    
    # 対話モード
    commander.interactive_mode()

if __name__ == "__main__":
    main()
