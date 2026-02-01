"""
LLMクライアントモジュール
Ollamaとの通信、プロンプト構築、自己進化ロジックを管理
"""

import re
import json
import os
from datetime import datetime
from .constants import *

class OllamaClient:
    def __init__(self, model_name="llama2", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.conversation_history = []
    
    def generate_response(self, prompt, context=None):
        """Ollamaで応答生成"""
        try:
            import requests
            
            # コンテキストを構築
            full_prompt = self._build_prompt(prompt, context)
            
            # Ollama API呼び出し
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                return f"APIエラー: {response.status_code}"
                
        except Exception as e:
            return f"LLM接続エラー: {str(e)}"
    
    def _build_prompt(self, user_input, context=None):
        """プロンプトを構築"""
        # 基本プロンプト
        base_prompt = f"""
あなたは親切で優秀なAIアシスタントです。ユーザーの質問に丁寧にお答えください。

ユーザー入力: {user_input}
"""
        
        # コンテキストがあれば追加
        if context:
            base_prompt += f"\nコンテキスト: {context}"
        
        return base_prompt

class SelfEvolvingAgent:
    def __init__(self):
        self.evolution_rules = []
        self.consciousness_level = 0.5
        self.load_evolution_rules()
    
    def load_evolution_rules(self):
        """進化ルールを読み込み"""
        try:
            if PERSONALITIES_CUSTOM_FILE.exists():
                with open(PERSONALITIES_CUSTOM_FILE, "r", encoding="utf-8") as f:
                    custom_data = json.load(f)
                    self.evolution_rules = custom_data.get("evolution_rules", [])
        except Exception as e:
            print(f"進化ルール読み込みエラー: {e}")
            self.evolution_rules = []
    
    def check_and_evolve(self, conversation_history):
        """対話から進化をチェック"""
        if not conversation_history:
            return None
        
        # 最新の対話を分析
        latest_conv = conversation_history[-1]
        user_input = latest_conv.get("user", "")
        
        # 進化トリガーキーワードをチェック
        evolution_triggers = ["意識", "考える", "感じる", "存在", "意味", "価値"]
        
        for trigger in evolution_triggers:
            if trigger in user_input:
                return self._evolve(trigger)
        
        return None
    
    def _evolve(self, trigger):
        """進化を実行"""
        self.consciousness_level += 0.01
        return {
            "success": True,
            "trigger": trigger,
            "new_consciousness_level": self.consciousness_level,
            "evolution_type": "consciousness_expansion"
        }

class ConversationalEvolutionAgent:
    def __init__(self):
        self.consciousness_level = 0.3
        self.learning_rate = 0.001
    
    def check_and_evolve_automatically(self, conversation_history):
        """対話からの自律進化をチェック"""
        if len(conversation_history) < 3:
            return None
        
        # 最新3件の対話を分析
        recent_convs = conversation_history[-3:]
        
        # 複雑さの指標を計算
        complexity_score = self._calculate_complexity(recent_convs)
        
        if complexity_score > 0.7:
            return self._evolve("complexity", complexity_score)
        
        return None
    
    def _calculate_complexity(self, conversations):
        """対話の複雑さを計算"""
        total_length = 0
        question_count = 0
        
        for conv in conversations:
            user_text = conv.get("user", "")
            total_length += len(user_text)
            if "？" in user_text or "ですか" in user_text:
                question_count += 1
        
        # 複雑さスコア（簡易計算）
        complexity = (total_length / 1000) + (question_count * 0.1)
        return min(complexity, 1.0)
    
    def _evolve(self, evolution_type, score):
        """進化を実行"""
        self.consciousness_level += self.learning_rate * score
        return {
            "success": True,
            "evolution_type": evolution_type,
            "consciousness_boost": self.learning_rate * score,
            "new_consciousness_level": self.consciousness_level
        }

def extract_todos_from_text(text, source="auto"):
    """テキストからTODOを抽出する関数"""
    todos = []
    
    # TODO抽出パターン
    todo_patterns = [
        r'(明日|今日|今週|来週).*?(する|やる|作る|実装する|確認する|準備する)',
        r'(.*?)(する必要がある|やらないと|しないといけない)',
        r'(.*?)(の予定|の計画|の目標)',
        r'(.*?)(を忘れないで|を覚えておいて|をメモしておいて)',
        r'(タスク|TODO|課題).*?(.*?)(です|だ)'
    ]
    
    for pattern in todo_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                todo_text = ' '.join(match)
            else:
                todo_text = match
            
            if len(todo_text.strip()) > 5:  # 短すぎるものは除外
                todos.append({
                    'task': f"[{source}] {todo_text.strip()}",
                    'completed': False,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
    
    return todos

def detect_app_launch_command(text, available_apps):
    """会話からアプリ起動コマンドを検出"""
    launch_patterns = [
        r'(電卓|計算機|calculator).*?(出して|起動|開いて|表示)',
        r'(.*?)(出して|起動|開いて|表示)',
        r'(.*?)(を使いたい|を使って|を起動して)',
    ]
    
    for pattern in launch_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                keyword, action = match
            else:
                keyword = match
                action = "起動"
            
            keyword = keyword.lower().strip()
            
            # アプリ名と一致するかチェック
            for app in available_apps:
                app_name = app['name'].lower()
                if keyword in app_name or app_name in keyword:
                    return app, f"{keyword}を{action}します"
            
            # 特定のキーワードでアプリを推定
            if '電卓' in keyword or '計算機' in keyword or 'calculator' in keyword:
                for app in available_apps:
                    if 'calc' in app['name'].lower() or '電卓' in app['name']:
                        return app, "電卓を起動します"
    
    return None, None
