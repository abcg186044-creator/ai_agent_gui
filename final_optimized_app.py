#!/usr/bin/env python3
"""
AI Agent System - Final Optimized Version
llama3.2 + VRM + RAG + Resource Monitoring + Scheduled Tasks
完全な最適化AIシステム
"""

import streamlit as st
import sys
import os
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path
import threading
import queue
import base64
import hashlib

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

# 最新llama3.2設定
class Config:
    # モデル設定
    MAIN_MODEL = "llama3.2"
    VISION_MODEL = "llama3.2-vision"
    EMBEDDING_MODEL = "nomic-embed-text:latest"
    
    # Ollama設定
    OLLAMA_HOST = "localhost"
    OLLAMA_PORT = 11434
    
    # 音声設定
    VOICE_RATE = 200
    VOICE_VOLUME = 0.9
    
    # VRM設定
    VRM_MODELS_PATH = "./vrm_models"
    DEFAULT_VRM = "default_avatar.vrm"
    VRM_ANIMATIONS = ["idle", "talking", "thinking", "happy", "sad"]
    
    # 高速応答設定
    STREAMING_ENABLED = True
    FAST_RESPONSE_TIMEOUT = 2.0
    MAX_TOKENS_FAST = 512
    MAX_TOKENS_FULL = 4096
    
    # RAG設定
    RAG_DB_PATH = "./rag_database"
    SIMILARITY_THRESHOLD = 0.7
    MAX_RAG_RESULTS = 5
    
    # リソース監視設定
    CPU_THRESHOLD = 80.0
    MEMORY_THRESHOLD = 80.0
    DISK_THRESHOLD = 10.0  # GB
    
    # スケジュール設定
    SCHEDULED_TASKS = [
        ("09:00", "daily_system_check"),
        ("12:00", "daily_summary"),
        ("18:00", "evening_cleanup"),
        ("22:00", "night_backup")
    ]

class RAGSystem:
    """RAG (Retrieval-Augmented Generation) システム"""
    
    def __init__(self):
        self.db_path = Config.RAG_DB_PATH
        self.embedding_model = None
        self.vector_index = None
        self.conversation_history = []
        
        # RAGデータベースディレクトリ作成
        os.makedirs(self.db_path, exist_ok=True)
        
    def initialize(self):
        """RAGシステム初期化"""
        try:
            # 埋め込みモデル初期化
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # 既存データの読み込み
            self._load_existing_data()
            
            # ベクトルインデックス構築
            self._build_vector_index()
            
            return True
        except Exception as e:
            st.error(f"❌ RAGシステム初期化エラー: {str(e)}")
            return False
    
    def _load_existing_data(self):
        """既存データ読み込み"""
        try:
            db_file = os.path.join(self.db_path, "conversations.json")
            if os.path.exists(db_file):
                with open(db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_history = data.get("conversations", [])
        except Exception:
            self.conversation_history = []
    
    def _save_data(self):
        """データ保存"""
        try:
            db_file = os.path.join(self.db_path, "conversations.json")
            data = {
                "conversations": self.conversation_history,
                "last_updated": datetime.now().isoformat()
            }
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"❌ データ保存エラー: {str(e)}")
    
    def _build_vector_index(self):
        """ベクトルインデックス構築"""
        try:
            if not self.conversation_history:
                return
            
            # 全会話から埋め込みを生成
            texts = []
            for conv in self.conversation_history:
                texts.append(conv.get("user_input", ""))
                texts.append(conv.get("ai_response", ""))
            
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
    
    def add_conversation(self, user_input, ai_response):
        """会話を追加"""
        conversation = {
            "id": hashlib.md5(f"{user_input}{ai_response}{datetime.now().isoformat()}".encode()).hexdigest(),
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response
        }
        
        self.conversation_history.append(conversation)
        self._save_data()
        self._build_vector_index()
    
    def search_similar_conversations(self, query, k=Config.MAX_RAG_RESULTS):
        """類似会話を検索"""
        try:
            if not self.vector_index or not query:
                return []
            
            # クエリの埋め込み生成
            query_embedding = self.embedding_model.encode([query])
            
            # 類似検索
            distances, indices = self.vector_index.search(query_embedding, k)
            
            # 類似度でフィルタリング
            similar_conversations = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if dist < (1 - Config.SIMILARITY_THRESHOLD):  # コサイン類似度
                    if idx < len(self.conversation_history):
                        similar_conversations.append({
                            "conversation": self.conversation_history[idx],
                            "similarity": 1 - dist
                        })
            
            return similar_conversations[:k]
            
        except Exception as e:
            st.error(f"❌ 類似検索エラー: {str(e)}")
            return []
    
    def get_context_for_query(self, query):
        """クエリに対するコンテキストを取得"""
        similar_convs = self.search_similar_conversations(query)
        
        if not similar_convs:
            return ""
        
        # 類似会話からコンテキストを構築
        context_parts = []
        for conv in similar_convs:
            context_parts.append(f"過去の類似質問: {conv['conversation']['user_input']}")
            context_parts.append(f"過去の回答: {conv['conversation']['ai_response']}")
        
        return "\n".join(context_parts)

class ResourceMonitor:
    """リソース監視システム"""
    
    def __init__(self):
        self.monitoring = True
        self.alerts = []
        
    def get_system_status(self):
        """システム状態を取得"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_free_gb": disk.free / (1024**3),
                "timestamp": datetime.now().isoformat(),
                "status": "healthy"
            }
            
            # しきい値を超えている場合は警告
            if cpu_percent > Config.CPU_THRESHOLD:
                status["status"] = "warning"
                status["cpu_warning"] = f"CPU使用率が高いです: {cpu_percent:.1f}%"
            
            if memory.percent > Config.MEMORY_THRESHOLD:
                status["status"] = "warning"
                status["memory_warning"] = f"メモリ使用率が高いです: {memory.percent:.1f}%"
            
            if disk.free / (1024**3) < Config.DISK_THRESHOLD:
                status["status"] = "warning"
                status["disk_warning"] = f"空き容量が少ないです: {disk.free / (1024**3):.1f}GB"
            
            return status
            
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def should_add_wait_message(self, response):
        """待機メッセージを追加すべきか判定"""
        status = self.get_system_status()
        
        if status.get("status") == "warning":
            high_load_keywords = ["重い", "時間がかかる", "待って", "処理中"]
            return any(keyword in response for keyword in high_load_keywords)
        
        return False
    
    def get_wait_message(self):
        """待機メッセージを取得"""
        return "少々お待ちください。現在システム負荷が高いです。"

class ScheduledTaskManager:
    """スケジュールタスク管理"""
    
    def __init__(self):
        self.scheduler = schedule
        self.running = False
        self.task_results = {}
        
    def initialize(self):
        """スケジューラー初期化"""
        try:
            # 定期タスクを登録
            for time_str, task_name in Config.SCHEDULED_TASKS:
                if task_name == "daily_system_check":
                    self.scheduler.every().day.at(time_str).do(self.daily_system_check)
                elif task_name == "daily_summary":
                    self.scheduler.every().day.at(time_str).do(self.daily_summary)
                elif task_name == "evening_cleanup":
                    self.scheduler.every().day.at(time_str).do(self.evening_cleanup)
                elif task_name == "night_backup":
                    self.scheduler.every().day.at(time_str).do(self.night_backup)
            
            # バックグラウンドでスケジューラーを起動
            self._start_scheduler_thread()
            
            return True
        except Exception as e:
            st.error(f"❌ スケジューラー初期化エラー: {str(e)}")
            return False
    
    def _start_scheduler_thread(self):
        """スケジューラースレッド起動"""
        def run_scheduler():
            self.running = True
            while self.running:
                self.scheduler.run_pending()
                time.sleep(60)  # 1分ごとにチェック
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
    
    def daily_system_check(self):
        """日次システムチェック"""
        try:
            monitor = ResourceMonitor()
            status = monitor.get_system_status()
            
            self.task_results["daily_system_check"] = {
                "timestamp": datetime.now().isoformat(),
                "status": status["status"],
                "details": status
            }
            
        except Exception as e:
            self.task_results["daily_system_check"] = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def daily_summary(self):
        """日次サマリー"""
        try:
            # RAGシステムから統計を取得
            summary = f"日次サマリー - {datetime.now().strftime('%Y-%m-%d')}"
            
            self.task_results["daily_summary"] = {
                "timestamp": datetime.now().isoformat(),
                "summary": summary
            }
            
        except Exception as e:
            self.task_results["daily_summary"] = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def evening_cleanup(self):
    """夕方クリーンアップ"""
        try:
            # 一時ファイルのクリーンアップ
            temp_dir = tempfile.gettempdir()
            cleaned_files = 0
            
            for file in os.listdir(temp_dir):
                if file.startswith("temp_"):
                    try:
                        os.remove(os.path.join(temp_dir, file))
                        cleaned_files += 1
                    except:
                        pass
            
            self.task_results["evening_cleanup"] = {
                "timestamp": datetime.now().isoformat(),
                "cleaned_files": cleaned_files
            }
            
        except Exception as e:
            self.task_results["evening_cleanup"] = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def night_backup(self):
        """夜間バックアップ"""
        try:
            # 設定ファイルのバックアップ
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "config": {
                    "main_model": Config.MAIN_MODEL,
                    "vision_model": Config.VISION_MODEL,
                    "rag_enabled": True,
                    "monitoring_enabled": True
                },
                "task_results": self.task_results
            }
            
            backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = os.path.join("./backups", backup_file)
            
            os.makedirs("./backups", exist_ok=True)
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            self.task_results["night_backup"] = {
                "timestamp": datetime.now().isoformat(),
                "backup_file": backup_path
            }
            
        except Exception as e:
            self.task_results["night_backup"] = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def get_task_status(self):
        """タスク状況を取得"""
        return {
            "scheduler_running": self.running,
            "next_tasks": self.scheduler.next_run(),
            "task_results": self.task_results
        }

class VRMModel:
    """VRMモデル管理クラス"""
    
    def __init__(self):
        self.models_path = Config.VRM_MODELS_PATH
        self.available_models = []
        self.current_model = None
        self.current_expression = "neutral"
        self.current_animation = "idle"
        
        os.makedirs(self.models_path, exist_ok=True)
        self._create_sample_vrm()
        self.get_available_models()
        
    def _create_sample_vrm(self):
        """サンプルVRMファイルを作成"""
        sample_vrm_path = os.path.join(self.models_path, "default_avatar.vrm")
        
        if not os.path.exists(sample_vrm_path):
            vrm_content = """# VRM Model File
model_version: "1.0"
model_name: "AI Assistant Avatar"
model_author: "AI System"

expressions:
  neutral: "通常"
  happy: "喜び"
  sad: "悲しみ"
  angry: "怒り"
  surprised: "驚き"
  thinking: "思考中"

animations:
  idle: "待機"
  talking: "話している"
  thinking: "思考中"
  waving: "手を振っている"
"""
            
            with open(sample_vrm_path, 'w', encoding='utf-8') as f:
                f.write(vrm_content)
    
    def get_available_models(self):
        """利用可能なVRMモデルを取得"""
        models = []
        if os.path.exists(self.models_path):
            for file in os.listdir(self.models_path):
                if file.endswith('.vrm'):
                    models.append(file)
        
        self.available_models = models
        return models
    
    def set_expression(self, expression):
        """表情を設定"""
        valid_expressions = ["neutral", "happy", "sad", "angry", "surprised", "thinking"]
        if expression in valid_expressions:
            self.current_expression = expression
            return True
        return False
    
    def set_animation(self, animation):
        """アニメーションを設定"""
        valid_animations = Config.VRM_ANIMATIONS
        if animation in valid_animations:
            self.current_animation = animation
            return True
        return False
    
    def get_vrm_info(self):
        """VRM情報を取得"""
        return {
            "available_models": len(self.available_models),
            "current_model": self.current_model,
            "current_expression": self.current_expression,
            "current_animation": self.current_animation,
            "models_path": self.models_path
        }

class VRMRenderer:
    """VRMレンダラー（シミュレーション）"""
    
    def __init__(self):
        self.vrm_model = VRMModel()
        self.is_rendering = False
        
    def initialize(self):
        """VRMレンダラー初期化"""
        self.vrm_model.get_available_models()
        return True
    
    def render_avatar(self, expression="neutral", animation="idle"):
        """アバターをレンダリング（シミュレーション）"""
        try:
            self.vrm_model.set_expression(expression)
            self.vrm_model.set_animation(animation)
            
            current_time = datetime.now().strftime('%H:%M:%S')
            
            expression_emoji = {
                "neutral": "😐", "happy": "😊", "sad": "😢",
                "angry": "😠", "surprised": "😲", "thinking": "🤔"
            }
            
            emoji = expression_emoji.get(expression, "😐")
            
            return {
                "status": "success",
                "timestamp": current_time,
                "expression": expression,
                "animation": animation,
                "emoji": emoji,
                "render_data": {
                    "avatar_state": "active",
                    "performance": "60 FPS",
                    "quality": "high"
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_avatar_display(self):
        """アバター表示を取得"""
        expression_emoji = {
            "neutral": "😐", "happy": "😊", "sad": "😢",
            "angry": "😠", "surprised": "😲", "thinking": "🤔"
        }
        
        emoji = expression_emoji.get(self.vrm_model.current_expression, "😐")
        
        return f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin: 10px 0;">
            <div style="font-size: 64px; margin-bottom: 10px;">{emoji}</div>
            <div style="color: white; font-weight: bold;">
                <div>Expression: {self.vrm_model.current_expression}</div>
                <div>Animation: {self.vrm_model.current_animation}</div>
                <div>Time: {datetime.now().strftime('%H:%M:%S')}</div>
            </div>
        </div>
        """

class FinalOptimizedAISystem:
    """最適化AIシステム"""
    
    def __init__(self):
        self.ollama_client = None
        self.whisper_model = None
        self.tts_engine = None
        self.rag_system = RAGSystem()
        self.resource_monitor = ResourceMonitor()
        self.task_manager = ScheduledTaskManager()
        self.vrm_renderer = VRMRenderer()
        self.current_personality = "friend"
        
    def initialize(self):
        """システム初期化"""
        try:
            # Ollama初期化
            self.ollama_client = ollama.Client()
            
            # 音声処理初期化
            self.whisper_model = faster_whisper.WhisperModel("base")
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', str(Config.VOICE_RATE))
            self.tts_engine.setProperty('volume', str(Config.VOICE_VOLUME))
            
            # 各サブシステム初期化
            self.rag_system.initialize()
            self.task_manager.initialize()
            self.vrm_renderer.initialize()
            
            return True
            
        except Exception as e:
            return False
    
    def generate_response(self, prompt, images=None, context="", fast_mode=False):
        """最適化された応答生成"""
        try:
            # RAGからコンテキストを取得
            rag_context = self.rag_system.get_context_for_query(prompt)
            full_context = f"{context}\n{rag_context}" if rag_context else context
            
            # リソース監視チェック
            if self.resource_monitor.should_add_wait_message(prompt):
                wait_message = self.resource_monitor.get_wait_message()
                self.vrm_renderer.render_avatar("thinking", "thinking")
                return f"{wait_message}\n\n思考中です..."
            
            # VRM表情更新（思考中）
            self.vrm_renderer.render_avatar("thinking", "thinking")
            
            # Ollamaで応答生成
            response = self.ollama_client.generate(
                model=Config.MAIN_MODEL,
                prompt=f"{full_context}\n\nユーザーの質問: {prompt}",
                options={
                    "temperature": 0.7,
                    "max_tokens": Config.MAX_TOKENS_FAST if fast_mode else Config.MAX_TOKENS_FULL
                }
            )
            
            ai_response = response['response']
            
            # RAGに会話を追加
            self.rag_system.add_conversation(prompt, ai_response)
            
            # 応答に応じて表情を変更
            if any(word in ai_response for word in ["ありがとう", "嬉しい", "楽しい", "成功"]):
                self.vrm_renderer.render_avatar("happy", "talking")
            elif any(word in ai_response for word in ["すみません", "ごめん", "失敗", "問題"]):
                self.vrm_renderer.render_avatar("sad", "talking")
            else:
                self.vrm_renderer.render_avatar("neutral", "talking")
            
            return ai_response
            
        except Exception as e:
            self.vrm_renderer.render_avatar("sad", "idle")
            return f"❌ 応答生成エラー: {str(e)}"
    
    def text_to_speech(self, text):
        """音声合成"""
        try:
            self.vrm_renderer.render_avatar("happy", "talking")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.vrm_renderer.render_avatar("neutral", "idle")
            return True
        except Exception as e:
            st.error(f"❌ 音声合成エラー: {str(e)}")
            return False
    
    def get_system_status(self):
        """システム状態を取得"""
        return {
            "resource_status": self.resource_monitor.get_system_status(),
            "task_status": self.task_manager.get_task_status(),
            "vrm_status": self.vrm_renderer.vrm_model.get_vrm_info(),
            "rag_status": {
                "conversations_count": len(self.rag_system.conversation_history),
                "last_updated": datetime.now().isoformat()
            }
        }

def render_dashboard(ai_system):
    """ダッシュボード表示"""
    st.header("📊 システムダッシュボード")
    
    status = ai_system.get_system_status()
    
    # リソース状態
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖥️ リソース監視")
        resource_status = status["resource_status"]
        
        if "error" not in resource_status:
            st.metric("CPU使用率", f"{resource_status['cpu_percent']:.1f}%")
            st.metric("メモリ使用率", f"{resource_status['memory_percent']:.1f}%")
            st.metric("空き容量", f"{resource_status['disk_free_gb']:.1f}GB")
            
            # 警告表示
            if resource_status.get("status") == "warning":
                st.warning("⚠️ システムリソースに注意が必要です")
                if "cpu_warning" in resource_status:
                    st.error(resource_status["cpu_warning"])
                if "memory_warning" in resource_status:
                    st.error(resource_status["memory_warning"])
                if "disk_warning" in resource_status:
                    st.error(resource_status["disk_warning"])
        else:
            st.success("✅ システムリソースは正常です")
    
    with col2:
        st.subheader("🤖 AIシステム状態")
        
        # RAG状態
        rag_status = status["rag_status"]
        st.metric("会話履歴", rag_status["conversations_count"])
        st.write(f"最終更新: {rag_status['last_updated']}")
        
        # タスク状態
        task_status = status["task_status"]
        st.write(f"スケジューラー: {'実行中' if task_status['scheduler_running'] else '停止中'}")
        
        if task_status["task_results"]:
            st.write("**最近のタスク結果**:")
            for task_name, result in task_status["task_results"].items():
                st.write(f"- {task_name}: {result.get('timestamp', 'N/A')}")

def render_main_interface(ai_system):
    """メインインターフェース"""
    st.header("💬 最適化AIアシスタント")
    
    # 会話履歴
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
    
    # VRM表示と入力
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 入力エリア
        user_input = st.text_input(
            "💬 メッセージを入力",
            placeholder="最適化AIとの対話を開始...",
            key="user_input"
        )
        
        # ボタン群
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            send_button = st.button("💬 送信", type="primary")
        
        with col2:
            fast_mode = st.checkbox("⚡ 高速モード", help="短い応答を優先")
        
        with col3:
            auto_speech = st.checkbox("🔊 音声読み上げ", value=True)
        
        # 送信処理
        if send_button and user_input:
            # ユーザーメッセージを保存
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # AI応答生成
            with st.spinner("🤖 最適化AIで応答生成中..."):
                context = ""
                if len(st.session_state.messages) > 1:
                    recent_messages = st.session_state.messages[-3:]
                    context = "最近の会話: " + " | ".join([msg["content"] for msg in recent_messages])
                
                ai_response = ai_system.generate_response(
                    user_input, 
                    context=context, 
                    fast_mode=fast_mode
                )
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            # 自動音声読み上げ
            if auto_speech:
                ai_system.text_to_speech(ai_response)
            
            st.rerun()
    
    with col2:
        # VRM表示
        st.subheader("👤 VRMアバター")
        vrm_display = ai_system.vrm_renderer.get_avatar_display()
        st.markdown(vrm_display, unsafe_allow_html=True)

def render_settings(ai_system):
    """設定画面"""
    st.header("⚙️ システム設定")
    
    # モデル情報
    st.subheader("🤖 モデル情報")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("メインモデル", Config.MAIN_MODEL)
        st.write("**用途**: 高速なテキスト生成・雑談")
        st.write("**特徴**: 3bモデルで軽量・高速")
    
    with col2:
        st.metric("ビジョンモデル", Config.VISION_MODEL)
        st.write("**用途**: 画像認識・画面分析")
        st.write("**特徴**: 11bモデルで高精度")
    
    # RAG設定
    st.subheader("🧠 RAG設定")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**データベースパス**: {Config.RAG_DB_PATH}")
        st.write(f"**会話履歴**: {len(ai_system.rag_system.conversation_history)}件")
        st.write(f"**類似度閾値**: {Config.SIMILARITY_THRESHOLD}")
    
    with col2:
        st.write("**有効化された機能**:")
        st.write("- ✅ 過去の会話検索")
        st.write("- ✅ コンテキスト拡張")
        st.write("- ✅ 類似度フィルタリング")
    
    # スケジュール設定
    st.subheader("⏰ スケジュール設定")
    st.write("**定期タスク**:")
    for time_str, task_name in Config.SCHEDULED_TASKS:
        st.write(f"- {time_str}: {task_name}")
    
    task_status = ai_system.get_system_status()["task_status"]
    if task_status["task_results"]:
        st.write("**実行結果**:")
        for task_name, result in task_status["task_results"].items():
            st.write(f"- {task_name}: {result.get('timestamp', 'N/A')}")

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="🚀 Final Optimized AI System",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 AI Agent System - Final Optimized Version")
    st.markdown("### 🎯 llama3.2 + VRM + RAG + 監視 + スケジュール")
    
    # システム初期化
    if 'ai_system' not in st.session_state:
        with st.spinner("🚀 最適化AIシステム初期化中..."):
            ai_system = FinalOptimizedAISystem()
            if ai_system.initialize():
                st.session_state.ai_system = ai_system
                st.success("✅ 最適化AIシステム初期化完了")
            else:
                st.error("❌ AIシステム初期化失敗")
                st.stop()
    
    ai_system = st.session_state.ai_system
    
    # サイドバー
    with st.sidebar:
        render_settings(ai_system)
    
    # メインタブ
    tab1, tab2 = st.tabs(["💬 AIアシスタント", "📊 システムダッシュボード"])
    
    with tab1:
        render_main_interface(ai_system)
    
    with tab2:
        render_dashboard(ai_system)
    
    # フッター情報
    st.markdown("---")
    st.markdown(f"**🚀 最適化AI**: {Config.MAIN_MODEL} + {Config.VISION_MODEL}")
    st.markdown(f"**最終更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**🎯 目標**: 速く・正確に・何でも見える・感情表現・過去の学習・自動管理")

if __name__ == "__main__":
    main()
