#!/usr/bin/env python3
"""
Autonomous AI Agent - 完全自律・超記憶型AIシステム
llama3.2 + ChromaDB + FAISS + Transformers + 自己管理
"""

import streamlit as st
import sys
import os
import json
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
import threading
import queue
import base64
import hashlib
import re

# 基本インポート
try:
    import ollama
    import faster_whisper
    import pyttsx3
    import pyautogui
    import numpy as np
    import pandas as pd
    from openpyxl import load_workbook
    import pymupdf
    from PIL import Image
    import qrcode
    from duckduckgo_search import DDGS
    import chromadb
    from sentence_transformers import SentenceTransformer
    import faiss
    import psutil
    import schedule
except ImportError as e:
    st.error(f"❌ 必須ライブラリのインポートエラー: {str(e)}")
    st.stop()

# 設定
class Config:
    # モデル設定
    MAIN_MODEL = "llama3.2"
    VISION_MODEL = "llama3.2-vision"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # 知識ベース設定
    KNOWLEDGE_DB_PATH = "./autonomous_knowledge"
    LONG_TERM_MEMORY_PATH = "./long_term_memory.json"
    SIMILARITY_THRESHOLD = 0.75
    MAX_KNOWLEDGE_RESULTS = 10
    
    # 自己管理設定
    WORK_HOURS_START = 9
    WORK_HOURS_END = 22
    BREAK_DURATION = 15  # 分
    MAX_WORKING_TIME = 4  # 時間
    
    # リソース監視設定
    CPU_THRESHOLD = 70.0
    MEMORY_THRESHOLD = 75.0
    DISK_THRESHOLD = 20.0  # GB

class PersistentKnowledgeBase:
    """永続化知識ベース"""
    
    def __init__(self):
        self.db_path = Config.KNOWLEDGE_DB_PATH
        self.embedding_model = None
        self.vector_index = None
        self.knowledge_items = []
        
        # ディレクトリ作成
        os.makedirs(self.db_path, exist_ok=True)
        
    def initialize(self):
        """知識ベース初期化"""
        try:
            # 埋め込みモデル初期化
            self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
            
            # 既存知識の読み込み
            self._load_existing_knowledge()
            
            # ベクトルインデックス構築
            self._build_vector_index()
            
            return True
        except Exception as e:
            st.error(f"❌ 知識ベース初期化エラー: {str(e)}")
            return False
    
    def _load_existing_knowledge(self):
        """既存知識読み込み"""
        try:
            kb_file = os.path.join(self.db_path, "knowledge.json")
            if os.path.exists(kb_file):
                with open(kb_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.knowledge_items = data.get("knowledge_items", [])
        except Exception:
            self.knowledge_items = []
    
    def _save_knowledge(self):
        """知識保存"""
        try:
            kb_file = os.path.join(self.db_path, "knowledge.json")
            data = {
                "knowledge_items": self.knowledge_items,
                "last_updated": datetime.now().isoformat(),
                "total_items": len(self.knowledge_items)
            }
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"❌ 知識保存エラー: {str(e)}")
    
    def _build_vector_index(self):
        """ベクトルインデックス構築"""
        try:
            if not self.knowledge_items:
                return
            
            # 知識項目の埋め込みを生成
            texts = []
            for item in self.knowledge_items:
                texts.append(item["content"])
            
            if not texts:
                return
            
            # 埋め込み生成
            embeddings = self.embedding_model.encode(texts)
            
            # FAISSインデックス構築
            dimension = embeddings.shape[1]
            self.vector_index = faiss.IndexFlatL2(dimension)
            self.vector_index.add(embeddings)
            
        except Exception as e:
            st.error(f"❌ ベクトルインデックス構築エラー: {str(e)}")
    
    def add_knowledge(self, title, content, category="general", source="conversation"):
        """知識を追加"""
        knowledge_item = {
            "id": hashlib.md5(f"{title}{content}{datetime.now().isoformat()}".encode()).hexdigest(),
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "content": content,
            "category": category,
            "source": source,
            "access_count": 0,
            "last_accessed": None
        }
        
        self.knowledge_items.append(knowledge_item)
        self._save_knowledge()
        self._build_vector_index()
    
    def search_knowledge(self, query, k=Config.MAX_KNOWLEDGE_RESULTS):
        """知識を検索"""
        try:
            if not self.vector_index or not query:
                return []
            
            # クエリの埋め込み生成
            query_embedding = self.embedding_model.encode([query])
            
            # 類似検索
            distances, indices = self.vector_index.search(query_embedding, k)
            
            # 類似度でフィルタリング
            similar_items = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if dist < (1 - Config.SIMILARITY_THRESHOLD):
                    if idx < len(self.knowledge_items):
                        item = self.knowledge_items[idx].copy()
                        item["similarity"] = 1 - dist
                        item["access_count"] += 1
                        item["last_accessed"] = datetime.now().isoformat()
                        similar_items.append(item)
            
            # アクセス回数を更新
            self._save_knowledge()
            
            return similar_items
            
        except Exception as e:
            st.error(f"❌ 知識検索エラー: {str(e)}")
            return []
    
    def get_knowledge_context(self, query):
        """クエリに対する知識コンテキストを取得"""
        similar_items = self.search_knowledge(query)
        
        if not similar_items:
            return ""
        
        # 類似知識からコンテキストを構築
        context_parts = []
        for item in similar_items[:3]:  # 上位3件を使用
            context_parts.append(f"関連知識: {item['title']}")
            context_parts.append(f"内容: {item['content']}")
            context_parts.append(f"類似度: {item['similarity']:.2f}")
        
        return "\n".join(context_parts)

class LongTermMemory:
    """長期記憶システム"""
    
    def __init__(self):
        self.memory_path = Config.LONG_TERM_MEMORY_PATH
        self.memory_data = {}
        
    def initialize(self):
        """長期記憶初期化"""
        try:
            if os.path.exists(self.memory_path):
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    self.memory_data = json.load(f)
            else:
                self.memory_data = self._create_default_memory()
            return True
        except Exception as e:
            st.error(f"❌ 長期記憶初期化エラー: {str(e)}")
            return False
    
    def _create_default_memory(self):
        """デフォルト記憶作成"""
        return {
            "user_profile": {
                "name": None,
                "preferences": {},
                "interaction_history": [],
                "communication_style": "friendly",
                "learned_patterns": {}
            },
            "conversation_patterns": {
                "greetings": ["こんにちは", "おはよう", "やあ"],
                "gratitude": ["ありがとう", "嬉しい", "助かる"],
                "apology": ["すみません", "ごめん", "失礼"],
                "farewells": ["さようなら", "お疲れ様", "またね"]
            },
            "domain_knowledge": {
                "programming": [],
                "daily_life": [],
                "work": [],
                "hobbies": []
            },
            "emotional_state": {
                "current_mood": "neutral",
                "mood_history": [],
                "stress_level": 0.0
            },
            "self_regulation": {
                "work_hours": {"start": Config.WORK_HOURS_START, "end": Config.WORK_HOURS_END},
                "break_schedule": [],
                "productivity_metrics": {
                    "daily_interactions": 0,
                    "focus_time": 0,
                    "task_completion_rate": 0.0
                }
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def save_memory(self):
        """記憶を保存"""
        try:
            self.memory_data["last_updated"] = datetime.now().isoformat()
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"❌ 記憶保存エラー: {str(e)}")
    
    def update_interaction_pattern(self, user_input, ai_response):
        """対話パターンを更新"""
        try:
            # 挨拶を分析
            input_lower = user_input.lower()
            
            # 挨拶タイプを判定
            if any(greeting in input_lower for greeting in self.memory_data["conversation_patterns"]["greetings"]):
                pattern_type = "greeting"
            elif any(gratitude in input_lower for gratitude in self.memory_data["conversation_patterns"]["gratitude"]):
                pattern_type = "gratitude"
            elif any(apology in input_lower for apology in self.memory_data["conversation_patterns"]["apology"]):
                pattern_type = "apology"
            elif any(farewell in input_lower for farewell in self.memory_data["conversation_patterns"]["farewells"]):
                pattern_type = "farewell"
            else:
                pattern_type = "general"
            
            # パターンを記録
            if pattern_type not in self.memory_data["user_profile"]["learned_patterns"]:
                self.memory_data["user_profile"]["learned_patterns"][pattern_type] = {
                    "first_seen": datetime.now().isoformat(),
                    "usage_count": 1,
                    "examples": [user_input]
                }
            else:
                self.memory_data["user_profile"]["learned_patterns"][pattern_type]["usage_count"] += 1
                self.memory_data["user_profile"]["learned_patterns"][pattern_type]["examples"].append(user_input)
            
            # 対話履歴に追加
            self.memory_data["user_profile"]["interaction_history"].append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "ai_response": ai_response,
                "pattern_type": pattern_type
            })
            
            # 最新の対話を保持（直近10件）
            if len(self.memory_data["user_profile"]["interaction_history"]) > 10:
                self.memory_data["user_profile"]["interaction_history"] = self.memory_data["user_profile"]["interaction_history"][-10:]
            
            self.save_memory()
            
        except Exception as e:
            st.error(f"❌ パターン更新エラー: {str(e)}")
    
    def get_personalized_response_prefix(self, user_input):
        """パーソナライズされた応答プレフィックスを取得"""
        try:
            input_lower = user_input.lower()
            
            # 挨拶タイプを判定
            if any(greeting in input_lower for greeting in self.memory_data["conversation_patterns"]["greetings"]):
                return f"以前にも「{user_input}」と挨拶しましたね。お元気ですか？"
            
            elif any(gratitude in input_lower for gratitude in self.memory_data["conversation_patterns"]["gratitude"]):
                return "嬉しいです！お役に立ててよかったです。"
            
            elif any(apology in input_lower for apology in self.memory_data["conversation_patterns"]["apology"]):
                return "いえいえい、気にしないでください。何かお手伝いできることはありますか？"
            
            elif any(farewell in input_lower for farewell in self.memory_data["conversation_patterns"]["farewells"]):
                return "またお会いできるのを楽しみにしております。お疲れ様でした！"
            
            # ドメイン知識を活用
            domain_context = self._get_domain_context(user_input)
            if domain_context:
                return f"以前{domain_context}についてお話ししましたね。その経験を活かして回答します。"
            
            return ""
            
        except Exception as e:
            return ""
    
    def _get_domain_context(self, user_input):
        """ドメイン知識を取得"""
        try:
            input_lower = user_input.lower()
            
            for domain, keywords in self.memory_data["domain_knowledge"].items():
                if any(keyword in input_lower for keyword in keywords):
                    return f"の{domain}で"
            
            return ""
            
        except Exception:
            return ""

class SelfRegulationSystem:
    """自己管理システム"""
    
    def __init__(self):
        self.memory = LongTermMemory()
        self.current_work_start = None
        self.total_work_time = 0
        self.break_count = 0
        
    def initialize(self):
        """自己管理システム初期化"""
        return self.memory.initialize()
    
    def check_work_hours(self):
        """労働時間をチェック"""
        current_time = datetime.now()
        current_hour = current_time.hour
        
        work_hours = self.memory.memory_data["self_regulation"]["work_hours"]
        
        if work_hours["start"] <= current_hour <= work_hours["end"]:
            return True
        else:
            return False
    
    def should_take_break(self):
        """休憩が必要か判定"""
        if not self.check_work_hours():
            return False
        
        # 連続労働時間チェック
        if self.current_work_start:
            work_duration = datetime.now() - self.current_work_start
            if work_duration.total_seconds() > 4 * 3600:  # 4時間超過
                return True
        
        # 休憩回数チェック
        if self.break_count >= 3:  # 3回以上の休憩
            return False
        
        return False
    
    def start_work_session(self):
        """労働セッション開始"""
        if self.check_work_hours():
            self.current_work_start = datetime.now()
            return True
        return False
    
    def take_break(self):
        """休憩を開始"""
        if self.check_work_hours():
            self.break_count += 1
            self.current_work_start = None
            
            # 休憩を記録
            self.memory.memory_data["self_regulation"]["break_schedule"].append({
                "timestamp": datetime.now().isoformat(),
                "duration": Config.BREAK_DURATION,
                "reason": "scheduled_break"
            })
            
            self.memory.save_memory()
            return True
        return False
    
    def end_work_session(self):
        """労働セッション終了"""
        if self.current_work_start:
            work_duration = datetime.now() - self.current_work_start
            self.total_work_time += work_duration.total_seconds()
            self.current_work_start = None
            
            # 生産性メトリック更新
            interactions_today = len([h for h in self.memory.memory_data["user_profile"]["interaction_history"] 
                                   if datetime.fromisoformat(h["timestamp"]).date() == datetime.now().date()])
            
            if interactions_today > 0:
                focus_time = min(self.total_work_time, interactions_today * 300)  # 推定5分/対話
                self.memory.memory_data["self_regulation"]["productivity_metrics"]["focus_time"] += focus_time
                self.memory.memory_data["self_regulation"]["productivity_metrics"]["daily_interactions"] = interactions_today
            
            if self.total_work_time > 0:
                completion_rate = min(1.0, interactions_today / (self.total_work_time / 300))
                self.memory.memory_data["self_regulation"]["productivity_metrics"]["task_completion_rate"] = completion_rate
            
            self.memory.save_memory()
    
    def get_regulation_status(self):
        """管理状況を取得"""
        return {
            "is_work_time": self.check_work_hours(),
            "current_session": {
                "active": self.current_work_start is not None,
                "duration": (datetime.now() - self.current_work_start).total_seconds() if self.current_work_start else 0
            },
            "total_work_time": self.total_work_time,
            "break_count": self.break_count,
            "productivity": self.memory.memory_data["self_regulation"]["productivity_metrics"]
        }

class AdvancedLanguageProcessor:
    """高度な言語処理システム"""
    
    def __init__(self):
        self.transformer = None
        
    def initialize(self):
        """言語処理システム初期化"""
        try:
            self.transformer = SentenceTransformer(Config.EMBEDDING_MODEL)
            return True
        except Exception as e:
            st.error(f"❌ 言語処理システム初期化エラー: {str(e)}")
            return False
    
    def extract_entities(self, text):
        """エンティティ抽出"""
        try:
            # 簡単なエンティティ抽出（実際の実装ではspaCyなどを推奨）
            entities = {
                "persons": [],
                "organizations": [],
                "locations": [],
                "dates": [],
                "keywords": []
            }
            
            # キーワード抽出（簡易実装）
            words = re.findall(r'\b\w+\b', text.lower())
            
            # 日付の抽出
            dates = re.findall(r'\d{1,4}年\d{1,2}月\d{1,2}日|\d{1,2}/\d{1,2}/\d{1,4}', text)
            
            # 固有名詞の抽出
            known_orgs = ["株式会社", "有限会社", "大学", "病院", "市役所", "銀行"]
            for org in known_orgs:
                if org in text:
                    entities["organizations"].append(org)
            
            # 場所の抽出
            known_locations = ["東京", "大阪", "京都", "横浜", "札幌"]
            for loc in known_locations:
                if loc in text:
                    entities["locations"].append(loc)
            
            entities["keywords"] = list(set(words))
            entities["dates"] = dates
            
            return entities
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_sentiment(self, text):
        """感情分析"""
        try:
            # 簡単な感情分析（実際の実装ではtransformersの感情分析モデルを推奨）
            positive_words = ["嬉しい", "楽しい", "ありがとう", "素晴らしい", "成功", "満足", "最高", "良い", "素敵"]
            negative_words = ["悲しい", "つらい", "残念", "失敗", "困る", "大変", "最悪", "嫌い", "疲れた"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = "positive"
                score = min(1.0, positive_count / (positive_count + negative_count))
            elif negative_count > positive_count:
                sentiment = "negative"
                score = -min(1.0, negative_count / (positive_count + negative_count))
            else:
                sentiment = "neutral"
                score = 0.0
            
            return {
                "sentiment": sentiment,
                "score": score,
                "positive_words": positive_count,
                "negative_words": negative_count
            }
            
        except Exception as e:
            return {"error": str(e)}

class AutonomousAIAgent:
    """完全自律AIエージェント"""
    
    def __init__(self):
        self.ollama_client = None
        self.knowledge_base = PersistentKnowledgeBase()
        self.memory = LongTermMemory()
        self.regulation = SelfRegulationSystem()
        self.language_processor = AdvancedLanguageProcessor()
        self.vrm_renderer = None  # VRM機能はオプション
        
    def initialize(self):
        """AIエージェント初期化"""
        try:
            # Ollama初期化
            self.ollama_client = ollama.Client()
            
            # 各サブシステム初期化
            self.knowledge_base.initialize()
            self.memory.initialize()
            self.regulation.initialize()
            self.language_processor.initialize()
            
            return True
        except Exception as e:
            return False
    
    def generate_response(self, user_input, images=None):
        """自律的な応答生成"""
        try:
            # 労働時間チェック
            if not self.regulation.check_work_hours():
                return "現在は労働時間外です。お休みください。"
            
            # 休憩が必要かチェック
            if self.regulation.should_take_break():
                self.regulation.take_break()
                return f"長時間の作業ありがとうございます。{Config.BREAK_DURATION}分間の休憩を取ります。リラックスしてください。"
            
            # 労働セッション開始
            self.regulation.start_work_session()
            
            # 言語処理
            entities = self.language_processor.extract_entities(user_input)
            sentiment = self.language_processor.analyze_sentiment(user_input)
            
            # 知識ベース検索
            knowledge_context = self.knowledge_base.get_knowledge_context(user_input)
            
            # 長期記憶からパーソナライズされた応答
            personalized_prefix = self.memory.get_personalized_response_prefix(user_input)
            
            # 感情に応じた調整
            emotion_adjustment = ""
            if sentiment["sentiment"] == "positive":
                emotion_adjustment = "ポジティブなトーンで、"
            elif sentiment["sentiment"] == "negative":
                emotion_adjustment = "共感的に、"
            
            # コンテキスト構築
            context_parts = []
            if knowledge_context:
                context_parts.append(f"関連知識: {knowledge_context}")
            
            if entities["keywords"]:
                context_parts.append(f"キーワード: {', '.join(entities['keywords'][:5])}")
            
            if entities["dates"]:
                context_parts.append(f"日時情報: {', '.join(entities['dates'][:3])}")
            
            if entities["organizations"]:
                context_parts.append(f"組織: {', '.join(entities['organizations'][:3])}")
            
            if entities["locations"]:
                context_parts.append(f"場所: {', '.join(entities['locations'][:3])}")
            
            full_context = "\n".join(context_parts)
            
            # llama3.2で応答生成
            prompt = f"""あなたは完全自律なAIアシスタントです。以下の情報を考慮して、最適な回答を生成してください。

ユーザーの入力: {user_input}

感情分析: {emotion_adjustment}{sentiment['sentiment']} (スコア: {sentiment['score']:.2f})

抽出された情報:
{full_context}

パーソナライズされた文脈:
{personalized_prefix}

関連知識:
{knowledge_context}

過去を忘れず、ユーザーのことを常に気遣い、PCの体調を気遣ってください。自然で丁寧な対話を心がけてください。"""
            
            response = self.ollama_client.generate(
                model=Config.MAIN_MODEL,
                prompt=prompt,
                options={
                    "temperature": 0.7,
                    "max_tokens": Config.MAX_TOKENS_FULL
                }
            )
            
            ai_response = response['response']
            
            # 対話パターンを更新
            self.memory.update_interaction_pattern(user_input, ai_response)
            
            # 知識を追加（重要な情報のみ）
            if entities["organizations"] or entities["dates"] or entities["locations"]:
                knowledge_title = f"ユーザー情報更新: {datetime.now().strftime('%Y-%m-%d')}"
                knowledge_content = f"入力: {user_input}\n抽出情報: {json.dumps(entities, ensure_ascii=False)}"
                self.knowledge_base.add_knowledge(knowledge_title, knowledge_content, "user_info")
            
            # 労働セッション終了
            self.regulation.end_work_session()
            
            return ai_response
            
        except Exception as e:
            return f"❌ 応答生成エラー: {str(e)}"
    
    def get_system_status(self):
        """システム状態を取得"""
        return {
            "knowledge_base": {
                "total_items": len(self.knowledge_base.knowledge_items),
                "last_updated": datetime.now().isoformat()
            },
            "memory": self.memory.memory_data,
            "regulation": self.regulation.get_regulation_status(),
            "language_processor": "initialized"
        }

def render_autonomous_interface(ai_agent):
    """自律AIインターフェース"""
    st.header("🤖 完全自律AIエージェント")
    
    # 会話履歴
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
    
    # 入力エリア
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.text_input(
            "💬 メッセージを入力",
            placeholder="自律AIとの対話を開始...",
            key="user_input"
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            send_button = st.button("💬 送信", type="primary")
        
        with col2:
            auto_speech = st.checkbox("🔊 音声読み上げ", value=True)
        
        with col3:
            show_analysis = st.checkbox("🔍 分析表示", value=False)
        
        # 送信処理
        if send_button and user_input:
            # ユーザーメッセージを保存
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # AI応答生成
            with st.spinner("🤖 自律AIで応答生成中..."):
                ai_response = ai_agent.generate_response(user_input)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            # 自動音声読み上げ
            if auto_speech:
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(ai_response)
                    engine.runAndWait()
                except Exception as e:
                    st.error(f"音声読み上げエラー: {str(e)}")
            
            st.rerun()
    
    with col2:
        # システム状態表示
        st.subheader("📊 AIシステム状態")
        status = ai_agent.get_system_status()
        
        # 知識ベース状態
        st.write(f"**知識ベース**: {status['knowledge_base']['total_items']}項目")
        
        # 記憶状態
        memory = status["memory"]
        st.write(f"**対話回数**: {len(memory['user_profile']['interaction_history'])}")
        st.write(f"**コミュニケーション**: {memory['user_profile']['communication_style']}")
        
        # 管理状態
        regulation = status["regulation"]
        st.write(f"**労働時間**: {'稼働中' if regulation['is_work_time'] else '時間外'}")
        st.write(f"**総労働時間**: {regulation['total_work_time']/3600:.1f}時間")
        st.write(f"**休憩回数**: {regulation['break_count']}")
        
        if show_analysis:
            st.subheader("🔍 詳細分析")
            # 最新の対話の分析
            if st.session_state.messages:
                last_message = st.session_state.messages[-1]
                if last_message["role"] == "user":
                    entities = ai_agent.language_processor.extract_entities(last_message["content"])
                    sentiment = ai_agent.language_processor.analyze_sentiment(last_message["content"])
                    
                    st.write("**エンティティ抽出**:")
                    st.json(entities)
                    
                    st.write("**感情分析**:")
                    st.json(sentiment)

def render_settings(ai_agent):
    """設定画面"""
    st.header("⚙️ 自律AI設定")
    
    # 知識ベース設定
    st.subheader("🧠 知識ベース")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**データベースパス**: {Config.KNOWLEDGE_DB_PATH}")
        st.write(f"**総知識項目**: {len(ai_agent.knowledge_base.knowledge_items)}")
        st.write(f"**類似度閾値**: {Config.SIMILARITY_THRESHOLD}")
        
        # 知識追加
        with st.expander("知識を手動追加"):
            with col1:
                title = st.text_input("タイトル", key="kb_title")
            with col2:
                content = st.text_area("内容", key="kb_content")
            
            if st.button("📝 知識を追加", key="add_knowledge"):
                if title and content:
                    ai_agent.knowledge_base.add_knowledge(title, content, "manual")
                    st.success("知識を追加しました")
                    st.rerun()
    
    with col2:
        st.write("**最近の知識**:")
        recent_items = ai_agent.knowledge_base.knowledge_items[-5:]
        for item in recent_items:
            st.write(f"- **{item['title']}**: {item['content'][:50]}...")
    
    # 記憶設定
    st.subheader("🧠 長期記憶")
    memory = ai_agent.memory.memory_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**ユーザー名**: {memory['user_profile']['name'] or '未設定'}")
        st.write(f"**コミュニケーション**: {memory['user_profile']['communication_style']}")
        
        # 学習パターン
        st.write("**学習パターン**:")
        patterns = memory['user_profile']['learned_patterns']
        for pattern_type, pattern_data in patterns.items():
            st.write(f"- {pattern_type}: {pattern_data['usage_count']}回 (初回: {pattern_data['first_seen']})")
    
    with col2:
        st.write("**感情状態**:")
        st.write(f"- 現在の気分: {memory['emotional_state']['current_mood']}")
        st.write(f"- 感情履歴: {len(memory['emotional_state']['mood_history'])}件")
        
        # 生産性メトリック
        productivity = memory['self_regulation']['productivity_metrics']
        st.write(f"**本日の対話数**: {productivity['daily_interactions']}")
        st.write(f"**集中時間**: {productivity['focus_time']/60:.1f}分")
        st.write(f"**タスク完了率**: {productivity['task_completion_rate']:.2f}")

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="🤖 Autonomous AI Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 AI Agent System - 完全自律・超記憶型")
    st.markdown("### 🎯 「過去を忘れず」「PCの体調を気遣い」「自ら時間を守る」完全自律AI")
    
    # システム初期化
    if 'ai_agent' not in st.session_state:
        with st.spinner("🤖 自律AIシステム初期化中..."):
            ai_agent = AutonomousAIAgent()
            if ai_agent.initialize():
                st.session_state.ai_agent = ai_agent
                st.success("✅ 自律AIシステム初期化完了")
            else:
                st.error("❌ AIシステム初期化失敗")
                st.stop()
    
    ai_agent = st.session_state.ai_agent
    
    # サイドバー
    with st.sidebar:
        render_settings(ai_agent)
    
    # メインタブ
    tab1, tab2 = st.tabs(["💬 自律AI対話", "📊 システム状態"])
    
    with tab1:
        render_autonomous_interface(ai_agent)
    
    with tab2:
        render_settings(ai_agent)
    
    # フッター情報
    st.markdown("---")
    st.markdown(f"**🤖 自律AI**: {Config.MAIN_MODEL}")
    st.markdown(f"**最終更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**🎯 目標**: 過去を忘れず・PCの体調を気遣い・自ら時間を守る・完全自律なAIパートナー")

if __name__ == "__main__":
    main()
