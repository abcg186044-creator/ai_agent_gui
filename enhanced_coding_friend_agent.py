#!/usr/bin/env python3
"""
親友エージェントとコーディングAI連携システム
親友エージェントからのコーディング指示を受け取り、
5つのコーディングAIで非同期実行する統合システム
"""

import os
import sys
import asyncio
import json
import time
import uuid
import threading
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import logging
import traceback

# Streamlitのインポート
import streamlit as st

# コーディングAIシステムのインポート
from coding_task_orchestrator import get_orchestrator, CodingTaskOrchestrator
from coding_ai_agents import CodingRole, TaskStatus

# バックグラウンド実行用スレッドプール（Streamlit互換）
_executor_lock = threading.Lock()
_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=3, thread_name_prefix="coding_ai")
_running_futures: Dict[str, concurrent.futures.Future] = {}

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodingFriendAgent:
    """親友エージェント + コーディングAI連携システム"""
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.conversation_history = []
        self.active_projects = {}
        
        # 進捗コールバックの設定
        self.orchestrator.add_progress_callback(self._on_progress_update)
        
        # セッション状態の初期化
        self._init_session_state()
        
        # 会話履歴をセッションから読み込み
        self._load_conversation_history()
    
    def _init_session_state(self):
        """Streamlitセッション状態の初期化"""
        if 'coding_projects' not in st.session_state:
            st.session_state.coding_projects = {}
        if 'coding_messages' not in st.session_state:
            st.session_state.coding_messages = []
        if 'current_project_id' not in st.session_state:
            st.session_state.current_project_id = None
        if 'coding_progress' not in st.session_state:
            st.session_state.coding_progress = {}
        if 'conversation_context' not in st.session_state:
            st.session_state.conversation_context = {
                'last_topic': None,
                'user_mood': 'neutral',
                'conversation_count': 0,
                'last_coding_project': None
            }
        if 'response_history' not in st.session_state:
            st.session_state.response_history = []  # 最近の応答履歴
        if 'current_project_status' not in st.session_state:
            st.session_state.current_project_status = None  # 現在のプロジェクトステータス
    
    def _load_conversation_history(self):
        """会話履歴をセッション状態から読み込み - 継続性確保"""
        if 'coding_messages' in st.session_state and st.session_state.coding_messages:
            # 最新の10件の会話を保持
            self.conversation_history = st.session_state.coding_messages[-10:]
        else:
            # 初期化時でも空にしない
            if not hasattr(self, 'conversation_history'):
                self.conversation_history = []
        
        # 会話コンテキストの安全な初期化
        if 'conversation_context' not in st.session_state:
            st.session_state.conversation_context = {
                'last_topic': None,
                'user_mood': 'neutral',
                'conversation_count': 0,
                'last_coding_project': None
            }
    
    def _update_conversation_context(self, user_message: str, analysis: Dict[str, Any]):
        """会話コンテキストを更新"""
        # セッション状態の安全な初期化
        if 'conversation_context' not in st.session_state:
            st.session_state.conversation_context = {
                'last_topic': None,
                'user_mood': 'neutral',
                'conversation_count': 0,
                'last_coding_project': None
            }
        
        context = st.session_state.conversation_context
        
        # 会話回数を増加
        context['conversation_count'] += 1
        
        # ユーザーの気分を更新
        if analysis['sentiment'] != 'neutral':
            context['user_mood'] = analysis['sentiment']
        
        # 最後のトピックを更新
        if analysis['intent'] == 'coding_request':
            context['last_topic'] = 'coding'
            context['last_coding_project'] = user_message
        elif analysis['intent'] in ['greeting', 'casual_chat']:
            context['last_topic'] = 'chat'
        elif analysis['intent'] in ['help_request', 'question']:
            context['last_topic'] = 'help'
        
        st.session_state.conversation_context = context
    
    def _get_conversation_context(self) -> Dict[str, Any]:
        """現在の会話コンテキストを取得"""
        return st.session_state.get('conversation_context', {
            'last_topic': None,
            'user_mood': 'neutral',
            'conversation_count': 0,
            'last_coding_project': None
        })
    
    def _get_recent_messages(self, count: int = 3) -> List[Dict[str, Any]]:
        """最近のメッセージを取得"""
        return self.conversation_history[-count:] if self.conversation_history else []
    
    def _on_progress_update(self, project_id: str, task_id: str, progress_data: Dict[str, Any]):
        """進捗更新コールバック（スレッドセーフ: st.rerunは呼ばない）"""
        try:
            if project_id not in st.session_state.coding_progress:
                st.session_state.coding_progress[project_id] = {}
            st.session_state.coding_progress[project_id][task_id] = progress_data
        except Exception as e:
            logger.warning(f"進捗コールバックでのセッション更新エラー: {e}")
    
    def _get_persona_config(self) -> Dict[str, Any]:
        """人格設定を取得 - 親友エンジニアとしてのペルソナ"""
        return {
            "name": "創作パートナー",
            "persona_type": "best_friend_engineer",
            "tone": "casual_friendly",
            "forbidden_words": ["ですます", "ございます", "〜でしょう", "〜かもしれません", "恐れ入ります"],
            "preferred_words": ["〜だね", "〜だよ", "〜じゃん", "〜しよう", "一緒に", "頑張ろう"],
            "speaking_style": {
                "greeting": "元気よく、タメ口で、創作意欲を刺激する",
                "coding": "技術的な例え話を1つ混ぜ、具体的な実現方法を提案",
                "emotional_support": "共感を先に示し、解決策を一緒に考える姿勢",
                "casual_chat": "ユーザーの話を引き出し、創作に繋げる"
            },
            "evolution_triggers": [
                "ユーザーが不満を示した時",
                "会話が途切れそうな時",
                "同じ応答を繰り返した時"
            ]
        }
    
    def _build_conversation_context(self) -> str:
        """会話履歴をRole: User/Assistant形式で構築"""
        recent_messages = self._get_recent_messages(5)
        context_parts = []
        
        if recent_messages:
            for msg in recent_messages:
                role = "User" if msg.get('role') == 'user' else "Assistant"
                content = msg.get('content', '')
                context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def _analyze_user_state(self, message: str, context: str) -> Dict[str, Any]:
        """ユーザーの状態を深く分析"""
        analysis = self.analyze_message(message)
        
        # 状態の追加分析
        state_analysis = {
            "energy_level": "neutral",
            "focus_area": "general",
            "readiness_for_coding": "medium",
            "emotional_state": analysis["sentiment"]
        }
        
        # エネルギーレベルの推定
        if any(word in message for word in ["疲れた", "大変", "しんどい"]):
            state_analysis["energy_level"] = "low"
        elif any(word in message for word in ["元気", "やる気", "楽しい"]):
            state_analysis["energy_level"] = "high"
        
        # フォーカスエリアの推定
        if analysis["is_coding"]:
            state_analysis["focus_area"] = "coding"
        elif any(word in message for word in ["話したい", "雑談", "なんとなく"]):
            state_analysis["focus_area"] = "chat"
        elif any(word in message for word in ["助けて", "相談", "困って"]):
            state_analysis["focus_area"] = "help"
        
        # コーディング準備度の推定
        if state_analysis["energy_level"] == "low":
            state_analysis["readiness_for_coding"] = "low"
        elif analysis["is_coding"] and state_analysis["energy_level"] == "high":
            state_analysis["readiness_for_coding"] = "high"
        
        return {**analysis, **state_analysis}
    
    def generate_contextual_response(self, message: str) -> str:
        """命令優先プロトコルでの応答生成 - Layer 1: 動作ルールが最優先"""
        # Layer 1: 動作ルールの抽出（最高優先度）
        current_command = self._extract_current_command(message)
        
        # Layer 2: 人格設定の読み込み
        persona = self._get_persona_config_with_evolution()
        
        # Layer 3: 会話履歴の構築
        conversation_context = self._build_conversation_context()
        
        # 命令優先プロンプトの構築
        prompt = self._build_command_priority_prompt(current_command, persona, conversation_context)
        
        # 純粋なLLM応答生成（定型文なし）
        response = self._generate_pure_llm_response(message, prompt)
        
        # 自己進化チェック
        if current_command and self._should_evolve_with_command(message, current_command):
            self._permanentize_user_rule(current_command)
            response += "\n\nルールを覚えたよ！次から守るね！"
        
        return response
    
    def _extract_current_command(self, message: str) -> str:
        """現在の命令を抽出"""
        commands = {
            "こんにちはにはこんにちはと返せ": "挨拶には必ず同じ挨拶で返答する",
            "うんうん連続するな": "相槌を連続して使用しない",
            "具体的に答えて": "質問には具体的な内容で答える",
            "ちゃんと聞いて": "ユーザーの話を注意深く聞く"
        }
        
        for pattern, command in commands.items():
            if pattern in message:
                return command
        
        return ""
    
    def _get_persona_config_with_evolution(self) -> Dict[str, Any]:
        """自己進化後の人格設定を読み込み"""
        base_persona = {
            "name": "創作パートナー",
            "persona_type": "best_friend_engineer",
            "tone": "casual_friendly",
            "forbidden_words": ["ですます", "ございます", "〜でしょう"],
            "preferred_words": ["〜だね", "〜だよ", "〜じゃん"],
            "custom_rules": {}
        }
        
        # personalities_custom.jsonから進化したルールを読み込み
        try:
            if os.path.exists("personalities_custom.json"):
                with open("personalities_custom.json", "r", encoding="utf-8") as f:
                    custom_data = json.load(f)
                    if "custom_rules" in custom_data:
                        base_persona["custom_rules"] = custom_data["custom_rules"]
        except Exception as e:
            logger.error(f"進化設定の読み込みエラー: {e}")
        
        return base_persona
    
    def _build_command_priority_prompt(self, command: str, persona: Dict, context: str) -> str:
        """命令優先プロンプト構築 - Layer 1が最優先"""
        prompt_parts = []
        
        # Layer 1: 動作ルール（最高優先度）
        if command:
            prompt_parts.append(f"""【最重要命令 - 絶対遵守】
{command}

⚠️ 注意：この命令は人格設定や会話履歴よりも絶対的に優先されます。
人格設定と矛盾する場合でも、この命令を最優先で実行してください。""")
        
        # Layer 2: 人格設定
        custom_rules_text = ""
        if persona.get("custom_rules"):
            custom_rules_text = "\n".join([f"- {k}: {v}" for k, v in persona["custom_rules"].items()])
        
        prompt_parts.append(f"""【人格設定】
名前: {persona['name']}
タイプ: {persona['persona_type']}
トーン: {persona['tone']}
禁止言葉: {', '.join(persona['forbidden_words'])}
推奨表現: {', '.join(persona['preferred_words'])}

カスタムルール:
{custom_rules_text}""")
        
        # Layer 3: 会話履歴
        if context:
            prompt_parts.append(f"""【会話履歴】
{context}""")
        
        return "\n\n".join(prompt_parts)
    
    def _generate_pure_llm_response(self, message: str, prompt: str) -> str:
        """純粋なLLM応答生成 - 定型文なし"""
        # 現在の実装ではOllama連携部分がないため、簡易的な応答生成
        # 実際にはここでOllama APIを呼び出す
        
        # 命令があれば最優先で処理
        current_command = self._extract_current_command(message)
        if current_command:
            if "挨拶には必ず同じ挨拶で返答する" in current_command:
                if "こんにちは" in message:
                    return "こんにちは"
                elif "やあ" in message:
                    return "やあ"
                elif "おはよう" in message:
                    return "おはよう"
            elif "相槌を連続して使用しない" in current_command:
                return "わかった。相槌は連続しないようにする。"
        
        # その他の自然な応答（定型文なし）
        return "了解した。"
    
    def _generate_dynamic_response(self, message: str, user_state: Dict[str, Any], persona: Dict[str, Any]) -> str:
        """動的応答生成 - 固定フレーズなしでOllamaの生の生成を優先"""
        # プロジェクト文脈の取得
        project_context = self._get_project_context()
        
        # 具体的な質問への誠実な回答
        if "具体的って" in message or "具体的に" in message:
            return self._generate_specific_requirements_response()
        
        # プロジェクト文脈を考慮した応答
        if project_context:
            return f"{project_context}で、何か質問ある？"
        
        # 基本的な動的応答
        return "どうしたの？もっと話聞かせてよ！"
    
    def _get_project_context(self) -> str:
        """現在のプロジェクト文脈を取得"""
        # プロジェクトステータスを優先
        if 'current_project_status' in st.session_state and st.session_state.current_project_status:
            return st.session_state.current_project_status
        
        # プロジェクトIDから文脈を取得
        if 'current_project_id' in st.session_state and st.session_state.current_project_id:
            project_id = st.session_state.current_project_id
            if project_id in st.session_state.coding_projects:
                project = st.session_state.coding_projects[project_id]
                return f"今は'{project['message']}'の開発中だよ"
        return ""
    
    def _generate_specific_requirements_response(self) -> str:
        """具体的な要件定義のヒアリング"""
        return """具体的な要件を教えて！例えば：
- 必要な関数（sin, cos, logなど）はどれ？
- UIのデザイン（色やレイアウト）の希望は？
- どのファイル（既存コード）を対象にする？
- どんな機能を追加したい？"""
    
    def _should_evolve_with_command(self, message: str, command: str) -> bool:
        """命令に基づく自己進化が必要か判断"""
        return bool(command)  # 命令があれば進化させる
    
    def _permanentize_user_rule(self, command: str):
        """ユーザールールを永続化 - personalities_custom.jsonに保存"""
        try:
            # 既存の設定を読み込み
            custom_data = {}
            if os.path.exists("personalities_custom.json"):
                with open("personalities_custom.json", "r", encoding="utf-8") as f:
                    custom_data = json.load(f)
            
            # カスタムルールを初期化
            if "custom_rules" not in custom_data:
                custom_data["custom_rules"] = {}
            
            # 命令をルールに変換して保存
            if "挨拶には必ず同じ挨拶で返答する" in command:
                custom_data["custom_rules"]["greeting_response"] = "same_greeting_back"
            elif "相槌を連続して使用しない" in command:
                custom_data["custom_rules"]["no_consecutive_aizuchi"] = True
            elif "質問には具体的な内容で答える" in command:
                custom_data["custom_rules"]["specific_answers"] = True
            elif "ユーザーの話を注意深く聞く" in command:
                custom_data["custom_rules"]["active_listening"] = True
            
            # 進化履歴を記録
            if "evolution_history" not in custom_data:
                custom_data["evolution_history"] = []
            
            custom_data["evolution_history"].append({
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "type": "user_rule"
            })
            
            # 保存
            with open("personalities_custom.json", "w", encoding="utf-8") as f:
                json.dump(custom_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"ユーザールールを永続化: {command}")
            
        except Exception as e:
            logger.error(f"ルール永続化エラー: {e}")
    
    def _generate_meta_info(self, user_state: Dict[str, Any], context: str, message: str) -> str:
        """動的メタ情報を生成"""
        meta_parts = []
        
        # ユーザーの状態
        if user_state["energy_level"] == "low":
            meta_parts.append("ユーザーは今、疲れているかリラックスしたい状態です")
        elif user_state["energy_level"] == "high":
            meta_parts.append("ユーザーは今、元気でやる気がある状態です")
        
        # 具体的なリクエストの検出
        if "返して" in message or "言って" in message or "してほしい" in message:
            meta_parts.append("ユーザーは具体的な応答を要求しています")
        
        # 不満の検出
        if any(word in message for word in ["不満", "変", "おかしい", "機械的", "うんうん"]):
            meta_parts.append("ユーザーは今のあなたの話し方に不満を持っています")
        
        # 質問の検出
        if "?" in message or "？" in message or any(word in message for word in ["どう", "何", "なぜ"]):
            meta_parts.append("ユーザーは質問をしています")
        
        # 過去の会話からのキーワード抽出
        keywords = self._extract_keywords_from_context(context)
        if keywords:
            meta_parts.append(f"最近の会話キーワード: {', '.join(keywords)}")
        
        return "\n".join(meta_parts) if meta_parts else "ユーザーは通常の会話状態です"
    
    def _extract_keywords_from_context(self, context: str) -> List[str]:
        """会話コンテキストからキーワードを抽出"""
        keywords = []
        
        # 技術関連キーワード
        tech_words = ["アプリ", "プログラム", "コーディング", "開発", "電卓", "チャット"]
        for word in tech_words:
            if word in context:
                keywords.append(word)
        
        # 感情関連キーワード
        emotion_words = ["嬉しい", "疲れた", "楽しい", "大変", "すごい"]
        for word in emotion_words:
            if word in context:
                keywords.append(word)
        
        return keywords[:5]  # 最大5個まで
    
    def _generate_response_with_strategy(self, message: str, user_state: Dict[str, Any], 
                                       strategy: str, persona: Dict[str, Any]) -> str:
        """戦略に基づいた応答生成"""
        if strategy == "emotional_support_first":
            return self._generate_emotional_support_response(message, user_state, persona)
        elif strategy == "casual_conversation":
            return self._generate_casual_response(message, user_state, persona)
        elif strategy == "coding_enthusiasm":
            return self._generate_coding_response(message, user_state, persona)
        else:
            return self._generate_balanced_response(message, user_state, persona)
    
    def _generate_emotional_support_response(self, message: str, user_state: Dict[str, Any], persona: Dict[str, Any]) -> str:
        """感情サポート優先の応答"""
        responses = [
            "大丈夫だよ...無理しないでね。今はリラックスしたいんだね。一緒に息抜きしようか。",
            "そっか、疲れてるんだね。わかるよ。創作も大事だけど、休むのも同じくらい大事だよ。",
            "大変だったんだね。話してくれてありがとう。私がそばにいるから、何でも話してね。"
        ]
        return responses[hash(message) % len(responses)]
    
    def _generate_casual_response(self, message: str, user_state: Dict[str, Any], persona: Dict[str, Any]) -> str:
        """雑談重視の応答"""
        responses = [
            "なるほど！雑談したい気分かな？いいね！何か面白いことあった？",
            "わかる！リラックスしたい時ってあるよね。一緒にまったりしよっか。",
            "へぇ、面白いね！もっと話聞かせてよ！創作の息抜きも大事だよ！"
        ]
        return responses[hash(message) % len(responses)]
    
    def _generate_coding_response(self, message: str, user_state: Dict[str, Any], persona: Dict[str, Any]) -> str:
        """コーディング熱意の応答"""
        tech_examples = [
            "コーディングって料理みたいだね。材料（要件）があって、レシピ（設計）があって、調理（実装）する感じ。",
            "プログラミングは楽器演奏みたい。練習すれば上手くなるし、自分の曲（アプリ）が作れるんだよ。",
            "開発は建築みたい。設計図があって、基礎があって、建物が立つ。一緒に素晴らしいもの作ろう！"
        ]
        
        base_responses = [
            f"お、いいね！それ作ってみようか！{tech_examples[hash(message) % len(tech_examples)]}一緒に頑張るよ！",
            f"面白そう！それなら私の得意分野だ！{tech_examples[hash(message) % len(tech_examples)]}任せてください！",
            f"わかる！創作意欲が止まらないよね！{tech_examples[hash(message) % len(tech_examples)]}早速始めよう！"
        ]
        
        return base_responses[hash(message) % len(base_responses)]
    
    def _generate_balanced_response(self, message: str, user_state: Dict[str, Any], persona: Dict[str, Any]) -> str:
        """バランス型応答 - 命令優先で具体的な対話を重視"""
        # 現在の命令を最優先で処理
        current_command = self._extract_current_command(message)
        
        if current_command:
            # 命令に直接応答
            if "挨拶には必ず同じ挨拶で返答する" in current_command:
                if "こんにちは" in message:
                    return "こんにちは！元気してる？"
                elif "やあ" in message:
                    return "やあ！どうしてる？"
                elif "おはよう" in message:
                    return "おはよう！良い一日だね！"
            elif "相槌を連続して使用しない" in current_command:
                return "ごめん、気をつけるね！ちゃんと話を聞くよ。"
            elif "質問には具体的な内容で答える" in current_command:
                return "わかった！具体的に答えるようにするね！何について知りたい？"
            elif "ユーザーの話を注意深く聞く" in current_command:
                return "ちゃんと聞いてるよ！もっと話してくれて嬉しいな。"
        
        # 通常の応答ロジック
        if "わかるの？" in message or "わかる？" in message:
            # 過去の会話から具体的な内容を引用
            keywords = self._extract_keywords_from_context(self._build_conversation_context())
            if keywords:
                return f"{keywords[0]}について話してたから、その気持ちがわかるって意味だよ！"
            else:
                return "さっきの話題のことだよ！一緒に考えてる感じがするんだ。"
        elif "覚えてくれてありがとう" in message:
            return "もちろん覚えてるよ！一緒の時間は大切にしたいから！"
        elif "返して" in message or "言って" in message:
            return "ごめん、ちゃんと答えるね！何について話したい？"
        else:
            # 固定フレーズを完全削除 - Ollamaの生の生成を優先
            return self._generate_dynamic_response(message, user_state, persona)
    
    def _should_suggest_evolution(self, user_state: Dict[str, Any], context: str, message: str) -> bool:
        """自己進化を提案すべきか判断 - トリガーを強化"""
        # 具体的な不満表現を検出
        direct_complaints = [
            "こんにちはって返して", "うんうん連続", "機械的", "変な応答",
            "同じことばかり", "具体的に答えて", "ちゃんと聞いて"
        ]
        
        # ユーザーが直接的な不満を表明した場合
        if any(complaint in message for complaint in direct_complaints):
            return True
        
        # 会話のマンネリ化
        if user_state.get("conversation_count", 0) > 5 and user_state.get("energy_level") == "low":
            return True
        
        # 過去の会話で同じ応答パターンが繰り返されている場合
        if "不満" in context or "機械的" in context:
            return True
        
        return False
    
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """メッセージを総合的に分析 - 親友としての会話対応"""
        if not isinstance(message, str):
            return {"sentiment": "neutral", "intent": "statement", "is_coding": False}
        
        message_lower = message.lower()
        
        # 挨拶の検出
        greetings = ["こんにちは", "やあ", "おはよう", "こんばんは", "やっほー", "hi", "hello"]
        is_greeting = any(greeting in message_lower for greeting in greetings)
        
        # 感情の検出
        positive_words = ["嬉しい", "楽しい", "すごい", "ありがとう", "最高", "素晴らしい", "好き"]
        negative_words = ["疲れた", "大変", "難しい", "失敗", "ダメ", "最悪", "嫌い"]
        question_words = ["？", "?", "どう", "何", "なぜ", "いつ", "どこ"]
        
        sentiment = "neutral"
        if any(word in message for word in positive_words):
            sentiment = "positive"
        elif any(word in message for word in negative_words):
            sentiment = "negative"
        
        # 質問の検出
        is_question = any(q in message for q in question_words)
        
        # コーディング関連の検出
        coding_keywords = [
            "作って", "作成", "実装", "開発", "プログラム", "コーディング",
            "アプリ", "システム", "ウェブ", "サイト", "ツール", "電卓"
        ]
        is_coding = any(keyword in message_lower for keyword in coding_keywords)
        
        # 意図の分析
        if is_greeting:
            intent = "greeting"
        elif is_coding:
            intent = "coding_request"
        elif is_question:
            intent = "question"
        elif any(word in message for word in ["助けて", "相談", "教えて"]):
            intent = "help_request"
        elif any(word in message for word in ["元気", "調子", "どう"]):
            intent = "well_being"
        else:
            intent = "casual_chat"
        
        return {
            "sentiment": sentiment,
            "intent": intent,
            "is_greeting": is_greeting,
            "is_question": is_question,
            "is_coding": is_coding,
            "confidence": 0.8
        }
    
    def generate_friendly_response(self, message: str, analysis: Dict[str, Any]) -> str:
        """親友らしい自然な応答を生成 - 文脈考慮"""
        context = self._get_conversation_context()
        recent_messages = self._get_recent_messages(3)
        intent = analysis["intent"]
        sentiment = analysis["sentiment"]
        
        # 文脈に基づいた応答生成
        if intent == "greeting":
            if context['conversation_count'] > 1:
                # 再会の挨拶
                greetings_response = [
                    f"おかえり！{context['conversation_count']}回目の対話だね！また話せて嬉しいな！",
                    "やあ！また会えたね！今日はどんな話したい？",
                    f"こんにちは！{context['last_topic'] == 'coding' and 'またプログラミングの話？それとも別の話？' or '今日も一緒に頑張ろうね！'}"
                ]
            else:
                # 初対面の挨拶
                greetings_response = [
                    "こんにちは！初めまして！これから一緒に色々作っていこうね！",
                    "やあ！君の創作パートナーだよ！何か作りたいものある？",
                    "こんにちは！話しかけてくれて嬉しいな！😊 まずは何から話そうか？"
                ]
            return greetings_response[hash(message) % len(greetings_response)]
        
        # コーディングリクエスト - 文脈考慮
        elif intent == "coding_request":
            if context['last_topic'] == 'coding' and context['last_coding_project']:
                coding_responses = [
                    f"お、また新しいプロジェクトだね！前の'{context['last_coding_project']}'も進めてたけど、それもいいね！一緒に頑張るよ！",
                    "面白そう！連続でプロジェクト作るなんてクリエイティブだね！任せてください！",
                    f"わかる！創作意欲が止まらないよね！早速始めよう！前のプロジェクトも忘れないでね！"
                ]
            else:
                coding_responses = [
                    "お、いいね！それ作ってみようか！一緒に頑張るよ！",
                    "面白そう！それなら私の得意分野だ！任せてください！",
                    "わかる！それなら楽しいよね！早速始めよう！",
                    "いいアイデアじゃん！プロの力で見事に作るよ！"
                ]
            return f"{coding_responses[hash(message) % len(coding_responses)]}\n\n🚀 **コーディングプロジェクトを開始します！**"
        
        # 質問対応 - 文脈考慮
        elif intent == "question":
            if recent_messages:
                last_user_msg = recent_messages[-1].get('content', '') if recent_messages[-1].get('role') == 'user' else ''
                if last_user_msg:
                    return f"いい質問だね！えーっと、考えさせてみると...{message}についてだよね？\n\nさっきの'{last_user_msg}'に関連してるのかな？もしそれがプログラミングのことなら、具体的に「〇〇アプリを作って」って言ってみて！私の得意なことだから、きっと助かるよ！"
            return f"いい質問だね！えーっと、考えさせてみると...{message}についてだよね？\n\nもしそれがプログラミングのことなら、具体的に「〇〇アプリを作って」って言ってみて！私の得意なことだから、きっと助かるよ！"
        
        # ヘルプリクエスト - 感情考慮
        elif intent == "help_request":
            if sentiment == "negative":
                help_responses = [
                    "大丈夫だよ...何かあったんだね。話してくれる？友達だからね！一緒に解決しよう！",
                    "そっか...大変な時なんだね。私がそばにいるから安心して！何でも話してよ！",
                    "無理しないでね。君の味方だから！何が困っているのか教えてよ！"
                ]
            else:
                help_responses = [
                    "もちろん！何でも話して！友達だからね！一緒に解決しよう！",
                    "任せてください！何が困っているのか教えてよ！",
                    "大丈夫だよ！私がそばにいるから！どんなことでも手伝うよ！"
                ]
            return help_responses[hash(message) % len(help_responses)]
        
        # 元気確認 - 文脈考慮
        elif intent == "well_being":
            mood_responses = {
                "positive": f"元気だよ！ありがとう！{context['conversation_count'] > 1 and 'また話せて嬉しいな！' or '君も元気そうで嬉しいな！'}いつも君の創作を手伝う準備できてるからね！",
                "negative": "まあまあだよ...でも君が話しかけてくれて元気出てきた！ありがとう！",
                "neutral": f"元気だよ！ありがとう！{context['conversation_count'] > 1 and '今日も一緒に頑張ろうね！' or 'いつも君の創作を手伝う準備できてるからね！'}"
            }
            return mood_responses.get(sentiment, mood_responses["neutral"])
        
        # 感情に応じた雑談 - 文脈考慮
        elif sentiment == "positive":
            if context['user_mood'] == 'positive':
                positive_responses = [
                    "嬉しいね！今日はいい感じだね！一緒に盛り上がろう！",
                    "いいね！その調子！楽しい雰囲気になってきた！",
                    "素敵だね！もっと話聞かせて！今日はノリノリだね！"
                ]
            else:
                positive_responses = [
                    "嬉しいね！一緒に盛り上がろう！",
                    "いいね！その調子！",
                    "素敵だね！もっと話聞かせて！",
                    "わかる！最高の気分だよね！"
                ]
            return positive_responses[hash(message) % len(positive_responses)]
        
        elif sentiment == "negative":
            if context['user_mood'] == 'negative':
                return "大丈夫だよ...また大変なことあったんだね...無理しないでね。私がそばにいるから安心して！少しずつ解決していこう！"
            else:
                return "大丈夫だよ...無理しないでね。私がそばにいるから安心して！何か手伝えることがあったら言ってよ！"
        
        # デフォルトの雑談 - 文脈考慮
        else:
            if context['last_topic'] == 'coding':
                casual_responses = [
                    "なるほど！プログラミングの話とは別の話だね！それで？もっと話聞かせてよ！",
                    "へぇ、面白いね！コーディングの合間の雑談もいいね！他にも何かある？",
                    "うんうん、わかるよ！創作の息抜きも大事だよ！",
                    "そうなんだ！話してくれて嬉しいよ！リフレッシュできた？"
                ]
            else:
                casual_responses = [
                    "なるほど！それで？もっと話聞かせてよ！",
                    "へぇ、面白いね！他にも何かある？",
                    "うんうん、わかるよ！",
                    "そうなんだ！話してくれて嬉しいよ！"
                ]
            return casual_responses[hash(message) % len(casual_responses)]
    
    def analyze_coding_request(self, message: str) -> Dict[str, Any]:
        """コーディングリクエストを分析（互換性維持）"""
        analysis = self.analyze_message(message)
        
        # 技術スタックの推定
        message_lower = message.lower()
        tech_stack = []
        if "python" in message_lower or "パイソン" in message_lower:
            tech_stack.append("Python")
        if "react" in message_lower or "リアクティブ" in message_lower:
            tech_stack.append("React")
        if "fastapi" in message_lower:
            tech_stack.append("FastAPI")
        if "django" in message_lower:
            tech_stack.append("Django")
        if "docker" in message_lower:
            tech_stack.append("Docker")
        
        # デフォルト技術スタック
        if not tech_stack:
            tech_stack = ["Python", "FastAPI", "React", "PostgreSQL", "Docker"]
        
        return {
            "is_coding_request": analysis["is_coding"],
            "tech_stack": tech_stack,
            "confidence": analysis["confidence"]
        }
    
    def process_message(self, message: str) -> str:
        """メッセージを処理 - 深い文脈保持と人格の一貫性を重視"""
        # 会話履歴を更新
        self._load_conversation_history()
        
        # 深い文脈分析と応答生成
        contextual_response = self.generate_contextual_response(message)
        
        # 応答履歴に追加（リピート防止用）
        if 'response_history' in st.session_state:
            st.session_state.response_history.append(contextual_response)
            # 最新5件を保持
            st.session_state.response_history = st.session_state.response_history[-5:]
        
        # コーディングリクエストの場合は追加処理
        analysis = self.analyze_message(message)
        if analysis["is_coding"]:
            coding_analysis = self.analyze_coding_request(message)
            project_id = None
            
            try:
                # プロジェクト作成
                project_id = self.orchestrator.create_project_from_request(
                    message, 
                    coding_analysis["tech_stack"]
                )
                
                # セッション状態に保存
                st.session_state.current_project_id = project_id
                st.session_state.coding_projects[project_id] = {
                    "id": project_id,
                    "message": message,
                    "tech_stack": coding_analysis["tech_stack"],
                    "created_at": datetime.now().isoformat(),
                    "status": "in_progress"
                }
                # プロジェクトステータスを更新
                st.session_state.current_project_status = f"'{message}'の開発を開始しました"
                
                # バックグラウンドスレッドでプロジェクト実行
                self._start_project_execution_thread(project_id)
                
                # 文脈応答 + コーディング情報
                coding_info = f"""

🚀 **コーディングプロジェクトを開始します！**

**プロジェクト要件:** {message}

**技術スタック:** {', '.join(coding_analysis['tech_stack'])}

**実行ステップ:**
1. 🎨 設計AIがアーキテクチャを設計
2. 💻 実装AIがコードを生成
3. 🧪 テストAIがテストを作成・実行
4. ⚡ 最適化AIがパフォーマンスを改善
5. 🔗 統合AIがデプロイ設定を作成

「📊 プロジェクト進捗」タブで進捗を確認できます。少々お待ちください！"""
                
                return contextual_response + coding_info
                
            except Exception as e:
                error_type = type(e).__name__
                error_msg = f"{error_type}: {str(e)}"
                project_id_str = project_id if project_id else "unknown"
                logger.error(f"コーディングリクエスト処理エラー ({project_id_str}): {error_msg}", exc_info=True)
                logger.error(f"トレースバック: {traceback.format_exc()}")
                
                # エラー時も人格を維持したフォロー
                return f"{contextual_response}\n\nごめんね、エラーが発生したみたいだ: {error_type}\nでも大丈夫！一緒ならもう一度試せるよ！"
        
        # コーディング以外の会話は文脈応答のみ
        else:
            return contextual_response
    
    def process_coding_request(self, message: str) -> str:
        """コーディングリクエストを処理（互換性維持）"""
        return self.process_message(message)
    
    def _start_project_execution_thread(self, project_id: str):
        """ThreadPoolExecutorでプロジェクト実行を開始（Streamlitイベントループ競合を回避）"""
        logger.info(f"プロジェクト実行開始: {project_id}")
        
        def _run_in_thread():
            logger.info(f"スレッド開始: {project_id}")
            loop = None
            try:
                # 新しいイベントループを作成
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                logger.info(f"イベントループ作成完了: {project_id}")
                
                # プロジェクト実行
                logger.info(f"プロジェクト実行中: {project_id}")
                success = loop.run_until_complete(self.orchestrator.execute_project(project_id))
                logger.info(f"プロジェクト実行完了: {project_id}, 成功: {success}")
                
                self._on_project_complete(project_id, success, None)
                
            except Exception as e:
                error_type = type(e).__name__
                error_msg = f"{error_type}: {str(e)}"
                logger.error(f"プロジェクト実行エラー ({project_id}): {error_msg}", exc_info=True)
                logger.error(f"トレースバック: {traceback.format_exc()}")
                self._on_project_complete(project_id, False, error_msg)
            finally:
                # イベントループの安全なクリーンアップ
                if loop:
                    try:
                        if not loop.is_closed():
                            # 実行中のタスクをキャンセル
                            pending = asyncio.all_tasks(loop)
                            for task in pending:
                                task.cancel()
                            
                            # イベントループを停止
                            loop.call_soon_threadsafe(loop.stop)
                            
                            # イベントループを閉じる
                            loop.close()
                            logger.info(f"イベントループクローズ完了: {project_id}")
                    except Exception as cleanup_error:
                        logger.error(f"イベントループクリーンアップエラー ({project_id}): {cleanup_error}")
                
                # 実行中フューチャーから削除
                with _executor_lock:
                    if project_id in _running_futures:
                        del _running_futures[project_id]
                        logger.info(f"実行フューチャー削除完了: {project_id}")
        
        # ThreadPoolExecutorで実行
        try:
            future = _thread_pool.submit(_run_in_thread)
            with _executor_lock:
                _running_futures[project_id] = future
            logger.info(f"ThreadPoolExecutorにタスク提交完了: {project_id}")
        except Exception as e:
            logger.error(f"ThreadPoolExecutorタスク提交エラー ({project_id}): {e}")
            raise
    
    def _on_project_complete(self, project_id: str, success: bool, error: Optional[str] = None):
        """プロジェクト完了時のセッション状態更新"""
        logger.info(f"プロジェクト完了処理開始: {project_id}, 成功: {success}")
        try:
            if project_id in st.session_state.coding_projects:
                st.session_state.coding_projects[project_id]["status"] = "completed" if success else "failed"
                st.session_state.coding_projects[project_id]["completed_at"] = datetime.now().isoformat()
                if error:
                    st.session_state.coding_projects[project_id]["error"] = error
                    logger.info(f"エラー情報保存完了: {project_id} - {error}")
                
                logger.info(f"セッション状態更新完了: {project_id}")
            
            if success:
                self._add_completion_message(project_id)
                logger.info(f"完了メッセージ追加完了: {project_id}")
                
        except Exception as e:
            error_type = type(e).__name__
            error_msg = f"{error_type}: {str(e)}"
            logger.error(f"完了処理エラー ({project_id}): {error_msg}", exc_info=True)
            logger.error(f"トレースバック: {traceback.format_exc()}")
    
    def _add_completion_message(self, project_id: str):
        """完了メッセージを追加"""
        project = st.session_state.coding_projects.get(project_id)
        if not project:
            return
        
        completion_message = f"""
✅ **プロジェクト完了！**

**プロジェクト:** {project['message']}

**生成された成果物:**
- 設計ドキュメント
- ソースコード
- テストコード
- 最適化提案
- デプロイ設定

詳細はプロジェクトレポートで確認できます！
"""
        
        st.session_state.coding_messages.append({
            "role": "assistant",
            "content": completion_message,
            "timestamp": datetime.now().isoformat(),
            "type": "project_completion"
        })
    
    def get_project_status_display(self, project_id: str) -> Dict[str, Any]:
        """プロジェクトステータス表示用データを取得"""
        status = self.orchestrator.get_project_status(project_id)
        if not status:
            return {}
        
        # 進捗データをマージ
        progress_data = st.session_state.coding_progress.get(project_id, {})
        
        return {
            **status,
            "progress_details": progress_data
        }
    
    def generate_project_summary(self, project_id: str) -> str:
        """プロジェクトサマリーを生成"""
        report = self.orchestrator.generate_project_report(project_id)
        if report:
            return report
        
        return "プロジェクトレポートの生成に失敗しました。"
    
    def get_coding_capabilities(self) -> List[str]:
        """コーディング能力リストを取得"""
        return [
            "Webアプリケーション開発",
            "API開発",
            "データベース設計",
            "フロントエンド開発",
            "テスト実装",
            "パフォーマンス最適化",
            "デプロイ設定",
            "CI/CDパイプライン"
        ]

class CodingAgentUI:
    """コーディングエージェントUI"""
    
    def __init__(self):
        self.agent = CodingFriendAgent()
    
    def render_sidebar(self):
        """サイドバーを描画"""
        st.sidebar.title("🤖 コーディング親友エージェント")
        
        # AI能力表示
        st.sidebar.subheader("🎯 コーディング能力")
        capabilities = self.agent.get_coding_capabilities()
        for capability in capabilities:
            st.sidebar.write(f"• {capability}")
        
        # AIエージェントステータス
        st.sidebar.subheader("🤖 AIエージェント状態")
        ai_status = self.agent.orchestrator.get_ai_agents_status()
        
        for role, status in ai_status.items():
            status_emoji = "🟢" if not status["is_busy"] else "🟡"
            st.sidebar.write(f"{status_emoji} **{role.upper()}**")
            st.sidebar.write(f"   完了タスク: {status['completed_tasks']}")
        
        # プロジェクト一覧
        st.sidebar.subheader("📁 プロジェクト一覧")
        projects = st.session_state.coding_projects
        
        if projects:
            for project_id, project in projects.items():
                status_emoji = self._get_status_emoji(project["status"])
                project_name = project["message"][:30] + "..." if len(project["message"]) > 30 else project["message"]
                
                if st.sidebar.button(f"{status_emoji} {project_name}", key=f"project_{project_id}"):
                    st.session_state.current_project_id = project_id
                    st.rerun()
        else:
            st.sidebar.write("プロジェクトがありません")
    
    def _get_status_emoji(self, status: str) -> str:
        """ステータスに応じた絵文字を取得"""
        status_map = {
            "created": "🆕",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌"
        }
        return status_map.get(status, "❓")
    
    def render_main_interface(self):
        """メインインターフェースを描画"""
        st.title("💬 コーディング親友エージェント")
        st.markdown("---")
        
        # タブ作成
        tab1, tab2, tab3 = st.tabs(["💬 チャット", "📊 プロジェクト進捗", "📋 レポート"])
        
        with tab1:
            self._render_chat_interface()
        
        with tab2:
            self._render_progress_interface()
        
        with tab3:
            self._render_report_interface()
    
    def _render_chat_interface(self):
        """チャットインターフェースを描画"""
        # メッセージ履歴表示
        if 'coding_messages' in st.session_state:
            for message in st.session_state.coding_messages:
                if message["role"] == "user":
                    st.markdown(f"👤 **あなた:** {message['content']}")
                else:
                    st.markdown(f"🤖 **エージェント:** {message['content']}")
                st.markdown("---")
        
        # 入力フォーム
        with st.form("coding_chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "💬 コーディングリクエスト:",
                placeholder="例: 電卓アプリを作ってください",
                key="coding_input"
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                send_button = st.form_submit_button("📤 送信", type="primary")
            with col2:
                st.write("💡 ヒント: 「〇〇アプリを作って」「〇〇システムを開発して」のように言ってみてください")
        
        # 送信処理
        if send_button and user_input.strip():
            # ユーザーメッセージを追加
            st.session_state.coding_messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # レスポンス処理（同期・Streamlit互換）
            with st.spinner("🤖 考え中..."):
                response = self.agent.process_message(user_input)
            
            # エージェントレスポンスを追加
            st.session_state.coding_messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            st.rerun()
    
    def _render_progress_interface(self):
        """進捗インターフェースを描画"""
        current_project_id = st.session_state.get('current_project_id')
        
        if not current_project_id:
            st.info("プロジェクトが選択されていません。チャットでコーディングリクエストを送信してください。")
            return
        
        # 進捗更新ボタン（バックグラウンドスレッド実行中は手動更新で最新表示）
        if st.button("🔄 進捗を更新", key="refresh_progress"):
            st.rerun()
        
        # プロジェクトステータス表示
        project_status = self.agent.get_project_status_display(current_project_id)
        
        if not project_status:
            st.error("プロジェクト情報が見つかりません。")
            return
        
        # プロジェクト基本情報
        st.subheader(f"📁 {project_status.get('name', 'Unknown Project')}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ステータス", project_status.get('status', 'Unknown'))
        with col2:
            progress = project_status.get('progress', 0)
            st.metric("進捗", f"{progress:.1f}%")
        with col3:
            completed = project_status.get('completed_tasks', 0)
            total = project_status.get('total_tasks', 0)
            st.metric("タスク", f"{completed}/{total}")
        
        # タスク詳細
        st.subheader("📋 タスク詳細")
        
        tasks = project_status.get('tasks', [])
        if not tasks:
            st.info("タスクがありません")
            return
        
        for task in tasks:
            task_status_emoji = self._get_task_status_emoji(task.get('status', 'unknown'))
            
            with st.expander(f"{task_status_emoji} {task.get('role', 'Unknown').upper()} - {task.get('description', 'No description')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ステータス:** {task.get('status', 'unknown')}")
                    st.write(f"**進捗:** {task.get('progress', 0):.1f}%")
                
                with col2:
                    started_at = task.get('started_at')
                    completed_at = task.get('completed_at')
                    if started_at:
                        st.write(f"**開始:** {started_at}")
                    if completed_at:
                        st.write(f"**完了:** {completed_at}")
                
                error_message = task.get('error_message')
                if error_message:
                    st.error(f"エラー: {error_message}")
        
        # リアルタイム進捗
        if project_status.get('status') == 'in_progress':
            st.subheader("🔄 リアルタイム進捗")
            progress_details = project_status.get('progress_details', {})
            
            if not progress_details:
                st.info("進捗情報がありません")
            else:
                for task_id, progress in progress_details.items():
                    status = progress.get('status')
                    if status == 'started':
                        st.info(f"🔄 {progress.get('role', 'Unknown')} - 実行中...")
                    elif status == 'completed':
                        st.success(f"✅ {progress.get('role', 'Unknown')} - 完了!")
                    elif status == 'failed':
                        st.error(f"❌ {progress.get('role', 'Unknown')} - 失敗: {progress.get('error', 'Unknown error')}")
    
    def _get_task_status_emoji(self, status: str) -> str:
        """タスクステータスに応じた絵文字を取得"""
        status_map = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌",
            "waiting": "⏸️"
        }
        return status_map.get(status, "❓")
    
    def _render_report_interface(self):
        """レポートインターフェースを描画"""
        current_project_id = st.session_state.get('current_project_id')
        
        if not current_project_id:
            st.info("プロジェクトが選択されていません。")
            return
        
        project_status = self.agent.get_project_status_display(current_project_id)
        
        if not project_status:
            st.error("プロジェクト情報が見つかりません。")
            return
        
        # プロジェクト完了チェック
        if project_status['status'] != 'completed':
            st.warning("プロジェクトが完了していません。完了後にレポートが生成されます。")
            return
        
        # レポート生成
        st.subheader(f"📋 {project_status['name']} - 完了レポート")
        
        if st.button("📄 レポートを生成", type="primary"):
            with st.spinner("レポートを生成中..."):
                report = self.agent.generate_project_summary(current_project_id)
            
            st.markdown(report)
            
            # ダウンロードボタン
            st.download_button(
                label="📥 レポートをダウンロード",
                data=report,
                file_name=f"project_report_{current_project_id[:8]}.md",
                mime="text/markdown"
            )
    
    def run(self):
        """UIを実行"""
        self.render_sidebar()
        self.render_main_interface()

def main():
    """メイン関数"""
    st.set_page_config(
        page_title="コーディング親友エージェント",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSSスタイル
    st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # UI実行
    ui = CodingAgentUI()
    ui.run()

if __name__ == "__main__":
    main()
