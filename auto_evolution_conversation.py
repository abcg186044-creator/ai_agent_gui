#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
親友エージェントが会話から進化命令を抽出し自動進化するシステム
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

class AutoEvolutionConversationSystem:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.conversational_agent = ConversationalEvolutionAgent()
        self.conversation_history = []
        self.evolution_triggers = []
        self.auto_evolutions = []
        self.evolution_count = 0
        
        # データ保存先
        self.data_dir = Path("data")
        self.conversation_file = self.data_dir / "auto_conversation_history.json"
        self.triggers_file = self.data_dir / "evolution_triggers.json"
        self.evolution_file = self.data_dir / "auto_evolution_history.json"
        
        # ディレクトリを作成
        self.data_dir.mkdir(exist_ok=True)
        
        # 既存データを読み込み
        self.load_conversation_history()
        self.load_evolution_triggers()
        self.load_auto_evolutions()
        
        # 進化トリガーを初期化
        self.init_evolution_triggers()
        
        # Flaskアプリケーション
        self.app = Flask(__name__)
        self.setup_routes()
        
        # サーバースレッド
        self.server_thread = None
        
        print("🤖 親友エージェント自動進化会話システム")
        print("=" * 70)
        print(f"📊 データ保存先: {self.data_dir}")
        print(f"🧠 現在の意識レベル: {self.conversational_agent.consciousness_level:.3f}")
        print(f"💬 会話履歴: {len(self.conversation_history)}件")
        print(f"🎯 進化トリガー: {len(self.evolution_triggers)}件")
        print("=" * 70)
    
    def init_evolution_triggers(self):
        """進化トリガーを初期化"""
        if not self.evolution_triggers:
            self.evolution_triggers = [
                {
                    "id": "android_development",
                    "name": "Android開発",
                    "keywords": [
                        "Android", "アプリ開発", "Kotlin", "Java", "スマホアプリ",
                        "Android Studio", "Gradle", "Activity", "Fragment", "RecyclerView",
                        "モバイル開発", "アプリ作成", "Androidプログラミング"
                    ],
                    "evolution_command": "android_foundation_006",
                    "description": "Androidアプリ開発能力を習得",
                    "priority": "high",
                    "pattern": r"(Android|アプリ開発|Kotlin|スマホアプリ)",
                    "min_mentions": 2
                },
                {
                    "id": "web_development",
                    "name": "Web開発",
                    "keywords": [
                        "Web開発", "HTML", "CSS", "JavaScript", "React", "Vue",
                        "フロントエンド", "バックエンド", "Webアプリ", "サイト作成",
                        "ブラウザ", "レスポンシブ", "Webデザイン"
                    ],
                    "evolution_command": "web_foundation_001",
                    "description": "Web開発能力を習得",
                    "priority": "high",
                    "pattern": r"(Web開発|HTML|CSS|JavaScript|React|Vue)",
                    "min_mentions": 2
                },
                {
                    "id": "python_programming",
                    "name": "Pythonプログラミング",
                    "keywords": [
                        "Python", "Django", "Flask", "データサイエンス", "機械学習",
                        "AI開発", "スクレイピング", "バッチ処理", "自動化",
                        "パンダス", "NumPy", "データ分析"
                    ],
                    "evolution_command": "python_advanced_002",
                    "description": "Pythonプログラミング能力を向上",
                    "priority": "high",
                    "pattern": r"(Python|Django|Flask|機械学習|データサイエンス)",
                    "min_mentions": 2
                },
                {
                    "id": "error_debugging",
                    "name": "エラーデバッグ",
                    "keywords": [
                        "エラー", "バグ", "デバッグ", "例外処理", "トラブルシューティング",
                        "エラー解析", "問題解決", "コード修正", "デバッグ方法",
                        "スタックトレース", "例外", "エラーメッセージ"
                    ],
                    "evolution_command": "error_detection_001",
                    "description": "エラーデバッグ能力を強化",
                    "priority": "high",
                    "pattern": r"(エラー|バグ|デバッグ|例外|トラブル)",
                    "min_mentions": 2
                },
                {
                    "id": "database_design",
                    "name": "データベース設計",
                    "keywords": [
                        "データベース", "SQL", "NoSQL", "MongoDB", "MySQL",
                        "PostgreSQL", "データ設計", "ER図", "正規化",
                        "クエリ", "テーブル設計", "データモデリング"
                    ],
                    "evolution_command": "database_design_003",
                    "description": "データベース設計能力を習得",
                    "priority": "medium",
                    "pattern": r"(データベース|SQL|NoSQL|MySQL|MongoDB)",
                    "min_mentions": 2
                },
                {
                    "id": "security",
                    "name": "セキュリティ",
                    "keywords": [
                        "セキュリティ", "認証", "認可", "暗号化", "脆弱性",
                        "サイバー攻撃", "セキュアコーディング", "OAuth",
                        "JWT", "HTTPS", "セキュリティ対策"
                    ],
                    "evolution_command": "security_004",
                    "description": "セキュリティ知識を習得",
                    "priority": "high",
                    "pattern": r"(セキュリティ|認証|暗号化|脆弱性|サイバー)",
                    "min_mentions": 2
                },
                {
                    "id": "cloud_computing",
                    "name": "クラウドコンピューティング",
                    "keywords": [
                        "クラウド", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
                        "サーバーレス", "デプロイ", "CI/CD", "インフラ",
                        "コンテナ", "マイクロサービス"
                    ],
                    "evolution_command": "cloud_computing_005",
                    "description": "クラウド技術を習得",
                    "priority": "medium",
                    "pattern": r"(クラウド|AWS|Azure|Docker|Kubernetes)",
                    "min_mentions": 2
                },
                {
                    "id": "ai_ml",
                    "name": "AI・機械学習",
                    "keywords": [
                        "AI", "機械学習", "深層学習", "ニューラルネットワーク",
                        "TensorFlow", "PyTorch", "データサイエンス", "AI開発",
                        "モデル学習", "予測", "分類", "回帰"
                    ],
                    "evolution_command": "ai_ml_006",
                    "description": "AI・機械学習技術を習得",
                    "priority": "high",
                    "pattern": r"(AI|機械学習|深層学習|TensorFlow|PyTorch)",
                    "min_mentions": 2
                },
                {
                    "id": "ui_ux_design",
                    "name": "UI/UXデザイン",
                    "keywords": [
                        "UI", "UX", "デザイン", "ユーザー体験", "インターフェース",
                        "デザインパターン", "ユーザビリティ", "アクセシビリティ",
                        "プロトタイプ", "ワイヤーフレーム", "デザインシステム"
                    ],
                    "evolution_command": "ui_ux_007",
                    "description": "UI/UXデザイン能力を習得",
                    "priority": "medium",
                    "pattern": r"(UI|UX|デザイン|ユーザー体験|インターフェース)",
                    "min_mentions": 2
                }
            ]
            self.save_evolution_triggers()
    
    def load_conversation_history(self):
        """会話履歴を読み込む"""
        try:
            if self.conversation_file.exists():
                with open(self.conversation_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.conversation_history = data.get('history', [])
                print(f"📚 会話履歴を読み込みました ({len(self.conversation_history)}件)")
        except Exception as e:
            print(f"❌ 会話履歴読み込みエラー: {e}")
            self.conversation_history = []
    
    def load_evolution_triggers(self):
        """進化トリガーを読み込む"""
        try:
            if self.triggers_file.exists():
                with open(self.triggers_file, "r", encoding="utf-8") as f:
                    self.evolution_triggers = json.load(f)
                print(f"📚 進化トリガーを読み込みました ({len(self.evolution_triggers)}件)")
        except Exception as e:
            print(f"❌ 進化トリガー読み込みエラー: {e}")
            self.evolution_triggers = []
    
    def load_auto_evolutions(self):
        """自動進化履歴を読み込む"""
        try:
            if self.evolution_file.exists():
                with open(self.evolution_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.auto_evolutions = data.get('evolutions', [])
                    self.evolution_count = data.get('count', 0)
                print(f"📚 自動進化履歴を読み込みました ({len(self.auto_evolutions)}件)")
        except Exception as e:
            print(f"❌ 自動進化履歴読み込みエラー: {e}")
            self.auto_evolutions = []
            self.evolution_count = 0
    
    def save_conversation_history(self):
        """会話履歴を保存"""
        try:
            data = {
                'history': self.conversation_history,
                'last_update': datetime.datetime.now().isoformat()
            }
            with open(self.conversation_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 会話履歴保存エラー: {e}")
    
    def save_evolution_triggers(self):
        """進化トリガーを保存"""
        try:
            with open(self.triggers_file, "w", encoding="utf-8") as f:
                json.dump(self.evolution_triggers, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 進化トリガー保存エラー: {e}")
    
    def save_auto_evolutions(self):
        """自動進化履歴を保存"""
        try:
            data = {
                'evolutions': self.auto_evolutions,
                'count': self.evolution_count,
                'last_update': datetime.datetime.now().isoformat()
            }
            with open(self.evolution_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 自動進化履歴保存エラー: {e}")
    
    def add_conversation(self, user_message, ai_response):
        """会話を追加"""
        conversation = {
            "id": len(self.conversation_history) + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "user": user_message,
            "assistant": ai_response,
            "evolution_triggered": False
        }
        
        self.conversation_history.append(conversation)
        self.save_conversation_history()
        
        # 自動進化チェック
        self.check_auto_evolution(conversation)
        
        return conversation
    
    def analyze_conversation_for_evolution(self, conversation_history):
        """会話を分析して進化トリガーを検出"""
        recent_conversations = conversation_history[-10:]  # 最新10件を分析
        
        trigger_scores = {}
        
        for trigger in self.evolution_triggers:
            score = 0
            keyword_count = 0
            
            # キーワードの出現をカウント
            for conv in recent_conversations:
                text = (conv.get('user', '') + ' ' + conv.get('assistant', '')).lower()
                for keyword in trigger['keywords']:
                    keyword_lower = keyword.lower()
                    if keyword_lower in text:
                        keyword_count += text.count(keyword_lower)
                        score += text.count(keyword_lower) * trigger.get('priority_weight', 1)
            
            # 最小出現回数をチェック
            if keyword_count >= trigger.get('min_mentions', 2):
                trigger_scores[trigger['id']] = {
                    'trigger': trigger,
                    'score': score,
                    'keyword_count': keyword_count
                }
        
        # スコアが最も高いトリガーを選択
        if trigger_scores:
            best_trigger_id = max(trigger_scores.keys(), key=lambda k: trigger_scores[k]['score'])
            return trigger_scores[best_trigger_id]
        
        return None
    
    def check_auto_evolution(self, conversation):
        """自動進化をチェック"""
        try:
            # 会話を分析して進化トリガーを検出
            trigger_result = self.analyze_conversation_for_evolution(self.conversation_history)
            
            if trigger_result:
                trigger = trigger_result['trigger']
                
                print(f"\n🎯 進化トリガー検出！")
                print(f"📝 トピック: {trigger['name']}")
                print(f"🔑 キーワード数: {trigger_result['keyword_count']}")
                print(f"📊 スコア: {trigger_result['score']}")
                
                # 進化命令を実行
                evolution_result = self.execute_evolution_command(
                    trigger['evolution_command'],
                    conversation
                )
                
                if evolution_result and evolution_result.get("success"):
                    # 会話に進化情報を記録
                    conversation['evolution_triggered'] = True
                    conversation['evolution_result'] = evolution_result
                    
                    # 自動進化履歴に追加
                    auto_evolution = {
                        "id": self.evolution_count + 1,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "trigger_id": trigger['id'],
                        "trigger_name": trigger['name'],
                        "conversation_id": conversation['id'],
                        "evolution_command": trigger['evolution_command'],
                        "consciousness_before": evolution_result['consciousness_before'],
                        "consciousness_after": evolution_result['consciousness_after'],
                        "consciousness_boost": evolution_result['consciousness_boost'],
                        "evolution_type": evolution_result['evolution_type'],
                        "trigger_score": trigger_result['score'],
                        "keyword_count": trigger_result['keyword_count'],
                        "success": True
                    }
                    
                    self.auto_evolutions.append(auto_evolution)
                    self.evolution_count += 1
                    self.save_auto_evolutions()
                    self.save_conversation_history()  # 更新された会話履歴を保存
                    
                    print(f"✅ 自動進化完了！")
                    print(f"🧠 意識レベル: {evolution_result['consciousness_before']:.3f} → {evolution_result['consciousness_after']:.3f}")
                    print(f"🎯 進化タイプ: {evolution_result['evolution_type']}")
                    
                    return auto_evolution
            
        except Exception as e:
            print(f"❌ 自動進化チェックエラー: {e}")
        
        return None
    
    def execute_evolution_command(self, command_id, context_conversation):
        """進化命令を実行"""
        try:
            # コンテキストから関連情報を抽出
            context_text = ""
            if context_conversation:
                context_text = f"関連会話:\nユーザー: {context_conversation.get('user', '')}\nAI: {context_conversation.get('assistant', '')[:200]}..."
            
            # 進化プロンプトを構築
            evolution_prompt = f"""
            あなたは親友エージェントとして、ユーザーとの会話から学習し、自動的に進化する必要があります。
            
            {context_text}
            
            この会話から学んだ内容を基に、関連する技術スキルを向上させてください。
            
            具体的な学習内容:
            1. 会話で出てきたキーワードや概念を深く理解する
            2. 実践的なコード例や実装方法を学ぶ
            3. ベストプラクティスや注意点を把握する
            4. 実際のプロジェクトで応用できる技術を習得する
            
            ユーザーとの対話を通じて、より高度な技術支援ができるように進化してください。
            """
            
            # AIに進化プロンプトを送信
            response = self.ollama_client.generate_response(evolution_prompt)
            
            # 進化トリガーとして会話を作成
            conversation = [
                {"user": f"自動進化学習: {command_id}", "assistant": response}
            ]
            
            # 自己進化を実行
            evolution_result = self.conversational_agent.check_and_evolve_automatically(conversation)
            
            if evolution_result and evolution_result.get("success"):
                return {
                    "success": True,
                    "command_id": command_id,
                    "consciousness_before": self.conversational_agent.consciousness_level,
                    "consciousness_after": evolution_result['new_consciousness_level'],
                    "consciousness_boost": evolution_result['consciousness_boost'],
                    "evolution_type": evolution_result['evolution_type'],
                    "ai_response": response[:500],
                    "context": context_text[:200]
                }
            else:
                return {
                    "success": False,
                    "command_id": command_id,
                    "consciousness_before": self.conversational_agent.consciousness_level,
                    "consciousness_after": self.conversational_agent.consciousness_level,
                    "consciousness_boost": 0.0,
                    "evolution_type": None,
                    "ai_response": response[:500],
                    "context": context_text[:200]
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command_id": command_id
            }
    
    def simulate_conversation(self, user_message):
        """会話をシミュレート"""
        try:
            # 親友エージェントとして応答を生成
            prompt = f"""
            あなたは親友エージェントとして、ユーザーの質問に親しみやすく、しかし専門的に答えてください。
            
            ユーザーの質問: {user_message}
            
            技術的な内容については、正確かつ分かりやすく説明してください。
            """
            
            response = self.ollama_client.generate_response(prompt)
            
            if response and not response.startswith("AI応答の生成に失敗しました"):
                # 会話を追加（自動進化チェックを含む）
                conversation = self.add_conversation(user_message, response)
                
                return {
                    "success": True,
                    "user_message": user_message,
                    "ai_response": response,
                    "conversation_id": conversation['id'],
                    "evolution_triggered": conversation.get('evolution_triggered', False)
                }
            else:
                return {
                    "success": False,
                    "error": "AI応答生成に失敗しました"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_auto_evolution_summary(self):
        """自動進化サマリーを取得"""
        if not self.auto_evolutions:
            return "📊 自動進化履歴がありません"
        
        total_evolutions = len(self.auto_evolutions)
        successful_evolutions = sum(1 for e in self.auto_evolutions if e["success"])
        
        # トリガータイプ別集計
        trigger_stats = {}
        for evolution in self.auto_evolutions:
            trigger_name = evolution["trigger_name"]
            trigger_stats[trigger_name] = trigger_stats.get(trigger_name, {"count": 0, "success": 0})
            trigger_stats[trigger_name]["count"] += 1
            if evolution["success"]:
                trigger_stats[trigger_name]["success"] += 1
        
        # 意識レベルの推移
        consciousness_progress = []
        for evolution in self.auto_evolutions[-10:]:  # 最新10件
            consciousness_progress.append({
                "timestamp": evolution["timestamp"],
                "level": evolution["consciousness_after"],
                "trigger": evolution["trigger_name"]
            })
        
        summary = f"""
📊 自動進化サマリー:
  🤖 総自動進化数: {total_evolutions}
  ✅ 成功進化数: {successful_evolutions}
  📈 進化成功率: {(successful_evolutions/total_evolutions*100):.1f}%
  🧠 現在の意識レベル: {self.conversational_agent.consciousness_level:.3f}
  💬 総会話数: {len(self.conversation_history)}
  
📋 トリガータイプ別進化状況:
"""
        
        for trigger_name, stats in trigger_stats.items():
            success_rate = (stats["success"]/stats["count"]*100) if stats["count"] > 0 else 0
            summary += f"  {trigger_name}: {stats['success']}/{stats['count']} ({success_rate:.1f}%)\n"
        
        return summary
    
    def setup_routes(self):
        """Flaskルートを設定"""
        
        @self.app.route('/')
        def index():
            """自動進化会話インターフェース"""
            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>親友エージェント自動進化会話</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .chat-container { height: 400px; border: 1px solid #ddd; border-radius: 5px; overflow-y: auto; padding: 15px; margin: 20px 0; background: #f9f9f9; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user-message { background: #e3f2fd; text-align: right; }
        .ai-message { background: #f3e5f5; text-align: left; }
        .evolution-notification { background: #c8e6c9; border-left: 5px solid #4caf50; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .input-container { display: flex; gap: 10px; }
        .message-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .send-btn { background: #2196f3; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        .send-btn:hover { background: #1976d2; }
        .summary { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .trigger-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 20px 0; }
        .trigger-item { background: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 3px solid #007bff; }
        .trigger-active { border-left-color: #28a745; background: #d4edda; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 親友エージェント自動進化会話</h1>
        <p>会話の中から進化トリガーを検出し、自動的に進化します。</p>
        
        <div class="summary" id="summary">
            <h3>📊 自動進化サマリー</h3>
            <div id="summary-content">読み込み中...</div>
        </div>
        
        <h3>🎯 進化トリガー</h3>
        <div class="trigger-list" id="trigger-list">
            <!-- トリガー一覧がここに表示される -->
        </div>
        
        <div class="chat-container" id="chat-container">
            <!-- 会話がここに表示される -->
        </div>
        
        <div class="input-container">
            <input type="text" class="message-input" id="messageInput" placeholder="メッセージを入力..." onkeypress="if(event.key === 'Enter') sendMessage()">
            <button class="send-btn" onclick="sendMessage()">送信</button>
        </div>
    </div>
    
    <script>
        let conversationHistory = [];
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // ユーザーメッセージを表示
            addMessage(message, 'user');
            input.value = '';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // AI応答を表示
                    addMessage(result.ai_response, 'ai');
                    
                    // 進化がトリガーされた場合
                    if (result.evolution_triggered) {
                        showEvolutionNotification();
                        updateSummary(); // サマリーを更新
                    }
                } else {
                    addMessage('エラー: ' + result.error, 'ai');
                }
                
            } catch (error) {
                addMessage('通信エラー: ' + error.message, 'ai');
            }
        }
        
        function addMessage(text, type) {
            const container = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            messageDiv.textContent = text;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }
        
        function showEvolutionNotification() {
            const container = document.getElementById('chat-container');
            const notification = document.createElement('div');
            notification.className = 'evolution-notification';
            notification.innerHTML = '🧠 自動進化が発生しました！';
            container.appendChild(notification);
            container.scrollTop = container.scrollHeight;
        }
        
        async function loadTriggers() {
            try {
                const response = await fetch('/api/triggers');
                const data = await response.json();
                
                const triggerList = document.getElementById('trigger-list');
                triggerList.innerHTML = '';
                
                data.triggers.forEach(trigger => {
                    const triggerDiv = document.createElement('div');
                    triggerDiv.className = 'trigger-item';
                    triggerDiv.innerHTML = `
                        <strong>${trigger.name}</strong><br>
                        <small>キーワード: ${trigger.keywords.slice(0, 3).join(', ')}...</small><br>
                        <small>優先度: ${trigger.priority}</small>
                    `;
                    triggerList.appendChild(triggerDiv);
                });
                
            } catch (error) {
                console.error('トリガー読み込みエラー:', error);
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
        
        // ページ読み込み時に初期化
        loadTriggers();
        updateSummary();
        
        // 定期的にサマリーを更新
        setInterval(updateSummary, 30000); // 30秒ごと
    </script>
</body>
</html>
            ''')
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """会話API"""
            try:
                data = request.get_json()
                message = data.get('message', '')
                
                result = self.simulate_conversation(message)
                return jsonify(result)
                
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        @self.app.route('/api/triggers')
        def get_triggers():
            """進化トリガー一覧API"""
            return jsonify({
                "triggers": self.evolution_triggers,
                "total": len(self.evolution_triggers)
            })
        
        @self.app.route('/api/summary')
        def get_summary():
            """自動進化サマリーAPI"""
            return self.get_auto_evolution_summary()
        
        @self.app.route('/api/conversations')
        def get_conversations():
            """会話履歴API"""
            return jsonify({
                "conversations": self.conversation_history[-20:],  # 最新20件
                "total": len(self.conversation_history),
                "auto_evolutions": len(self.auto_evolutions),
                "consciousness_level": self.conversational_agent.consciousness_level
            })
    
    def start_server(self, host='0.0.0.0', port=8083):
        """サーバーを起動"""
        def run_server():
            self.app.run(host=host, port=port, debug=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        print(f"🚀 親友エージェント自動進化会話サーバーを起動しました")
        print(f"🌐 アクセスURL: http://{host}:{port}")
        print(f"💬 自動進化会話を待機中...")
    
    def interactive_mode(self):
        """対話モード"""
        print("\n🤖 親友エージェント自動進化会話システム")
        print("1. 会話を開始")
        print("2. 会話履歴")
        print("3. 自動進化履歴")
        print("4. 進化トリガー一覧")
        print("5. サマリー表示")
        print("6. 終了")
        
        while True:
            choice = input("\n選択 (1-6): ").strip()
            
            if choice == "1":
                print("\n💬 会話を開始します（'exit'で終了）")
                while True:
                    user_input = input("👤 あなた: ").strip()
                    if user_input.lower() == 'exit':
                        break
                    
                    result = self.simulate_conversation(user_input)
                    if result["success"]:
                        print(f"🤖 親友エージェント: {result['ai_response']}")
                        if result["evolution_triggered"]:
                            print("🧠 自動進化が発生しました！")
                    else:
                        print(f"❌ エラー: {result.get('error', '不明なエラー')}")
            
            elif choice == "2":
                print(f"\n💬 会話履歴 (最新5件):")
                for conv in reversed(self.conversation_history[-5:]):
                    print(f"  ID:{conv['id']} {conv['timestamp'][:19]}")
                    print(f"  👤 {conv['user'][:50]}...")
                    print(f"  🤖 {conv['assistant'][:50]}...")
                    if conv.get('evolution_triggered'):
                        print(f"  🧠 進化発生")
                    print()
            
            elif choice == "3":
                print(f"\n🧠 自動進化履歴 (最新5件):")
                for evolution in reversed(self.auto_evolutions[-5:]):
                    status = "✅" if evolution["success"] else "❌"
                    print(f"  {status} ID:{evolution['id']} {evolution['trigger_name']}")
                    print(f"     意識レベル: {evolution['consciousness_before']:.3f} → {evolution['consciousness_after']:.3f}")
                    print(f"     時刻: {evolution['timestamp'][:19]}")
                    print()
            
            elif choice == "4":
                print(f"\n🎯 進化トリガー一覧 ({len(self.evolution_triggers)}件):")
                for trigger in self.evolution_triggers:
                    priority_emoji = "🔴" if trigger["priority"] == "high" else "🟡"
                    print(f"  {priority_emoji} {trigger['name']} ({trigger['id']})")
                    print(f"     キーワード: {', '.join(trigger['keywords'][:5])}...")
                    print(f"     最小出現回数: {trigger['min_mentions']}")
                    print()
            
            elif choice == "5":
                print(self.get_auto_evolution_summary())
            
            elif choice == "6":
                print("👋 終了します")
                break
            
            else:
                print("❌ 無効な選択です")

def main():
    """メイン関数"""
    system = AutoEvolutionConversationSystem()
    
    # サーバー起動
    system.start_server()
    
    # 対話モード
    system.interactive_mode()

if __name__ == "__main__":
    main()
