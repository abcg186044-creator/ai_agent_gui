#!/usr/bin/env python3
"""
AI Agent System - llama3.2 完全移行版
最新のllama3.2シリーズを活用した最適化AIシステム
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
    import base64
except ImportError as e:
    st.error(f"❌ 必須ライブラリのインポートエラー: {str(e)}")
    st.stop()

# 最新llama3.2設定
class Config:
    # モデル設定
    MAIN_MODEL = "llama3.2"           # メイン推論・雑談用（3b: 高速かつ高知能）
    VISION_MODEL = "llama3.2-vision"   # 画像・画面解析用（11b: 画面監視機能）
    EMBEDDING_MODEL = "nomic-embed-text:latest"
    
    # Ollama設定
    OLLAMA_HOST = "localhost"
    OLLAMA_PORT = 11434
    
    # 音声設定
    VOICE_RATE = 200
    VOICE_VOLUME = 0.9
    
    # 高速応答設定
    STREAMING_ENABLED = True
    FAST_RESPONSE_TIMEOUT = 2.0  # 秒
    MAX_TOKENS_FAST = 512
    MAX_TOKENS_FULL = 4096

class ModelRouter:
    """インテリジェントモデル・ルーター"""
    
    def __init__(self):
        self.main_model = Config.MAIN_MODEL
        self.vision_model = Config.VISION_MODEL
        self.embedding_model = Config.EMBEDDING_MODEL
        
    def route_request(self, prompt, images=None, context="", fast_mode=False):
        """リクエストを最適なモデルに振り分ける"""
        
        # 画像が含まれる場合はビジョンモデル
        if images and len(images) > 0:
            return self.vision_model, self._prepare_vision_prompt(prompt, context)
        
        # 短い応答が必要な場合は高速モード
        if fast_mode or self._is_fast_response_needed(prompt):
            return self.main_model, self._prepare_fast_prompt(prompt, context)
        
        # 通常のテキスト処理
        return self.main_model, self._prepare_full_prompt(prompt, context)
    
    def _is_fast_response_needed(self, prompt):
        """高速応答が必要か判定"""
        fast_keywords = ["こんにちは", "おはよう", "ありがとう", "すみません", "はい", "いいえ", "うん", "そう", "なるほど"]
        prompt_lower = prompt.lower()
        return any(keyword in prompt_lower for keyword in fast_keywords)
    
    def _prepare_fast_prompt(self, prompt, context):
        """高速応答用プロンプト準備"""
        return f"""{context}

短く簡潔に答えてください。最大50文字以内で：
{prompt}"""
    
    def _prepare_full_prompt(self, prompt, context):
        """完全応答用プロンプト準備"""
        return f"""{context}

詳細に丁寧に答えてください：
{prompt}"""
    
    def _prepare_vision_prompt(self, prompt, context):
        """ビジョン用プロンプト準備"""
        return f"""{context}

画像とテキスト情報を統合して答えてください：
{prompt}"""

class StreamingResponse:
    """ストリーミング応答処理"""
    
    def __init__(self, model, prompt, images=None):
        self.model = model
        self.prompt = prompt
        self.images = images
        self.response_queue = queue.Queue()
        self.is_complete = False
        
    def generate_streaming(self):
        """ストリーミング生成"""
        try:
            if self.images:
                # ビジョンモデルの場合
                response = ollama.generate(
                    model=self.model,
                    prompt=self.prompt,
                    images=self.images,
                    options={
                        "temperature": 0.7,
                        "max_tokens": Config.MAX_TOKENS_FULL,
                        "stream": False  # ビジョンモデルはストリーミング未対応
                    }
                )
                self.response_queue.put(response['response'])
            else:
                # テキストモデルの場合
                response = ollama.generate(
                    model=self.model,
                    prompt=self.prompt,
                    options={
                        "temperature": 0.7,
                        "max_tokens": Config.MAX_TOKENS_FAST if self._is_fast_prompt() else Config.MAX_TOKENS_FULL,
                        "stream": False
                    }
                )
                self.response_queue.put(response['response'])
                
            self.is_complete = True
            
        except Exception as e:
            self.response_queue.put(f"❌ 応答生成エラー: {str(e)}")
            self.is_complete = True
    
    def _is_fast_prompt(self):
        """高速プロンプトか判定"""
        fast_keywords = ["こんにちは", "おはよう", "ありがとう", "すみません", "はい", "いいえ"]
        return any(keyword in self.prompt for keyword in fast_keywords)
    
    def get_response(self):
        """応答を取得"""
        try:
            return self.response_queue.get(timeout=30)
        except queue.Empty:
            return "応答タイムアウト"

class StartupSelfCheck:
    """起動時セルフチェック"""
    
    def __init__(self):
        self.checks = []
        
    def run_all_checks(self):
        """すべてのチェックを実行"""
        results = {
            "models": self.check_models(),
            "dependencies": self.check_dependencies(),
            "system": self.check_system_resources(),
            "external_tools": self.check_external_tools()
        }
        
        self.checks = results
        return results
    
    def check_models(self):
        """モデルチェック"""
        try:
            client = ollama.Client()
            models = client.list()
            model_names = [m.get('name', '') for m in models]
            
            checks = {
                "main_model": Config.MAIN_MODEL in model_names,
                "vision_model": Config.VISION_MODEL in model_names,
                "embedding_model": Config.EMBEDDING_MODEL in model_names,
                "available_models": model_names
            }
            
            return checks
            
        except Exception as e:
            return {"error": str(e)}
    
    def check_dependencies(self):
        """依存関係チェック"""
        dependencies = {
            "ollama": self._check_import("ollama"),
            "streamlit": self._check_import("streamlit"),
            "pyautogui": self._check_import("pyautogui"),
            "faster_whisper": self._check_import("faster_whisper"),
            "pyttsx3": self._check_import("pyttsx3"),
            "pillow": self._check_import("PIL"),
            "pandas": self._check_import("pandas"),
            "chromadb": self._check_import("chromadb")
        }
        return dependencies
    
    def _check_import(self, module_name):
        """インポートチェック"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def check_system_resources(self):
        """システムリソースチェック"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_free_gb": disk.free / (1024**3),
                "status": "healthy" if cpu_percent < 80 and memory.percent < 80 else "warning"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_external_tools(self):
        """外部ツールチェック"""
        tools = {
            "ollama_service": self._check_ollama_service(),
            "php": self._check_php()
        }
        return tools
    
    def _check_ollama_service(self):
        """Ollamaサービスチェック"""
        try:
            client = ollama.Client()
            models = client.list()
            return len(models) > 0
        except:
            return False
    
    def _check_php(self):
        """PHPチェック"""
        try:
            import subprocess
            result = subprocess.run(
                ["C:\\Program Files\\PHP\\current\\php.exe", "--version"], 
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False

class OptimizedAISystem:
    """llama3.2最適化AIシステム"""
    
    def __init__(self):
        self.ollama_client = None
        self.whisper_model = None
        self.tts_engine = None
        self.model_router = ModelRouter()
        self.startup_check = StartupSelfCheck()
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
            
            # 起動時チェック実行
            check_results = self.startup_check.run_all_checks()
            
            return True, check_results
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def generate_response(self, prompt, images=None, context="", fast_mode=False):
        """最適化された応答生成"""
        try:
            # モデル振り分け
            model, formatted_prompt = self.model_router.route_request(
                prompt, images, context, fast_mode
            )
            
            # ストリーミング応答
            if Config.STREAMING_ENABLED and not images:
                streaming = StreamingResponse(model, formatted_prompt, images)
                
                # バックグラウンドで実行
                thread = threading.Thread(target=streaming.generate_streaming)
                thread.start()
                
                # 応答取得
                response = streaming.get_response()
                thread.join(timeout=30)
                
                return response
            else:
                # 通常応答
                if images:
                    response = self.ollama_client.generate(
                        model=model,
                        prompt=formatted_prompt,
                        images=images,
                        options={
                            "temperature": 0.7,
                            "max_tokens": Config.MAX_TOKENS_FULL
                        }
                    )
                else:
                    response = self.ollama_client.generate(
                        model=model,
                        prompt=formatted_prompt,
                        options={
                            "temperature": 0.7,
                            "max_tokens": Config.MAX_TOKENS_FAST if fast_mode else Config.MAX_TOKENS_FULL
                        }
                    )
                
                return response['response']
                
        except Exception as e:
            return f"❌ 応答生成エラー: {str(e)}"
    
    def analyze_screen_with_vision(self, prompt="この画面について詳細に分析してください"):
        """ビジョンモデルで画面分析"""
        try:
            # 画面キャプチャ
            screenshot = pyautogui.screenshot()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_path = f"vision_analysis_{timestamp}.png"
            screenshot.save(temp_path)
            
            # llama3.2-visionで分析
            response = self.ollama_client.generate(
                model=Config.VISION_MODEL,
                prompt=prompt,
                images=[temp_path],
                options={
                    "temperature": 0.7,
                    "max_tokens": Config.MAX_TOKENS_FULL
                }
            )
            
            # 一時ファイル削除
            try:
                os.unlink(temp_path)
            except:
                pass
            
            return response['response']
            
        except Exception as e:
            return f"❌ 画面分析エラー: {str(e)}"
    
    def extract_text_from_screen(self):
        """llama3.2-visionでOCR"""
        try:
            ocr_prompt = """この画像からすべてのテキスト情報を抽出してください。
            読めるテキストを正確に、フォーマットを保って出力してください。
            ボタン、ラベル、メニュー項目、エラーメッセージなど、すべてのテキストを含めてください。"""
            
            return self.analyze_screen_with_vision(ocr_prompt)
            
        except Exception as e:
            return f"❌ テキスト抽出エラー: {str(e)}"
    
    def text_to_speech(self, text):
        """音声合成"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            st.error(f"❌ 音声合成エラー: {str(e)}")
            return False

def render_startup_check(check_results):
    """起動時チェック結果表示"""
    st.header("🔍 起動時セルフチェック")
    
    # モデルチェック
    if "models" in check_results:
        st.subheader("🤖 モデルチェック")
        models = check_results["models"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "メインモデル", 
                "✅ OK" if models.get("main_model") else "❌ 失敗",
                help=Config.MAIN_MODEL
            )
        with col2:
            st.metric(
                "ビジョンモデル", 
                "✅ OK" if models.get("vision_model") else "❌ 失敗",
                help=Config.VISION_MODEL
            )
        
        if "available_models" in models:
            st.write("**利用可能なモデル**:")
            for model in models["available_models"]:
                st.write(f"- {model}")
    
    # 依存関係チェック
    if "dependencies" in check_results:
        st.subheader("📦 依存関係チェック")
        deps = check_results["dependencies"]
        
        for dep_name, status in deps.items():
            status_icon = "✅" if status else "❌"
            st.write(f"{status_icon} {dep_name}")
    
    # システムリソースチェック
    if "system" in check_results:
        st.subheader("📊 システムリソース")
        sys_info = check_results["system"]
        
        if "error" not in sys_info:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("CPU使用率", f"{sys_info['cpu_percent']:.1f}%")
            with col2:
                st.metric("メモリ使用率", f"{sys_info['memory_percent']:.1f}%")
            with col3:
                st.metric("空き容量", f"{sys_info['disk_free_gb']:.1f}GB")
            
            status_color = "🟢" if sys_info["status"] == "healthy" else "🟡"
            st.write(f"**システム状態**: {status_color} {sys_info['status']}")

def render_main_interface(ai_system):
    """メインインターフェース"""
    st.header("💬 llama3.2 AIアシスタント")
    
    # 会話履歴
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
    
    # 入力エリア
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        user_input = st.text_input(
            "💬 メッセージを入力",
            placeholder="llama3.2との対話を開始...",
            key="user_input"
        )
    
    with col2:
        if st.button("👁️ 画面分析", help="llama3.2-visionで画面分析"):
            with st.spinner("👁️ llama3.2-visionで画面分析中..."):
                result = ai_system.analyze_screen_with_vision()
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"👁️ **画面分析結果**:\n\n{result}"
                })
                st.rerun()
    
    with col3:
        if st.button("📝 テキスト抽出", help="llama3.2-visionでOCR"):
            with st.spinner("📝 llama3.2-visionでテキスト抽出中..."):
                result = ai_system.extract_text_from_screen()
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"📝 **テキスト抽出結果**:\n\n{result}"
                })
                st.rerun()
    
    with col4:
        fast_mode = st.checkbox("⚡ 高速モード", help="短い応答を優先")
    
    # 送信ボタン
    if st.button("💬 送信", type="primary"):
        if user_input:
            # ユーザーメッセージを保存
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # AI応答生成
            with st.spinner("🤖 llama3.2で応答生成中..."):
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
            if st.checkbox("🔊 音声読み上げ", value=True):
                ai_system.text_to_speech(ai_response)
            
            st.rerun()

def render_settings(ai_system):
    """設定画面"""
    st.header("⚙️ llama3.2 設定")
    
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
    
    # 人格選択
    st.subheader("🎭 人格設定")
    personalities = {
        "friend": "👥 親友エンジニア",
        "copy": "🪞 分身", 
        "expert": "🧑‍🏫 エキスパート"
    }
    
    selected_personality = st.selectbox(
        "人格選択",
        list(personalities.keys()),
        format_func=lambda x: personalities[x],
        index=list(personalities.keys()).index(ai_system.current_personality)
    )
    
    if selected_personality != ai_system.current_personality:
        ai_system.current_personality = selected_personality
        st.success(f"人格を「{personalities[selected_personality]}」に変更しました")
    
    # 高速応答設定
    st.subheader("⚡ 高速応答設定")
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox(
            "ストリーミング応答",
            value=Config.STREAMING_ENABLED,
            help="リアルタイムでの応答表示"
        )
    
    with col2:
        st.number_input(
            "高速応答タイムアウト（秒）",
            value=Config.FAST_RESPONSE_TIMEOUT,
            min_value=1.0,
            max_value=10.0,
            step=0.5
        )

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="🚀 llama3.2 AI System",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 AI Agent System - llama3.2 完全移行版")
    st.markdown("### 🎯 最新llama3.2シリーズで「速く」「正確に」「何でも見える」最強のAIエージェント")
    
    # システム初期化
    if 'ai_system' not in st.session_state:
        with st.spinner("🚀 llama3.2 AIシステム初期化中..."):
            ai_system = OptimizedAISystem()
            success, check_results = ai_system.initialize()
            
            if success:
                st.session_state.ai_system = ai_system
                st.success("✅ llama3.2 AIシステム初期化完了")
            else:
                st.error("❌ AIシステム初期化失敗")
                if "error" in check_results:
                    st.error(f"エラー: {check_results['error']}")
                st.stop()
    
    ai_system = st.session_state.ai_system
    
    # サイドバー
    with st.sidebar:
        # 起動時チェック結果
        if 'startup_check' not in st.session_state:
            st.session_state.startup_check = ai_system.startup_check.checks
        
        render_startup_check(st.session_state.startup_check)
        
        # 設定
        render_settings(ai_system)
    
    # メインタブ
    tab1, tab2 = st.tabs(["💬 AIアシスタント", "👁️ ビジョン機能"])
    
    with tab1:
        render_main_interface(ai_system)
    
    with tab2:
        st.header("👁️ llama3.2-vision ビジョン機能")
        st.markdown("### 🎨 高度な画像認識・画面分析")
        
        # 画像アップロード分析
        uploaded_file = st.file_uploader(
            "📁 画像ファイルを選択",
            type=['png', 'jpg', 'jpeg', 'bmp', 'gif'],
            key="vision_image_file"
        )
        
        if uploaded_file:
            # 画像プレビュー
            image = Image.open(uploaded_file)
            st.image(image, caption="アップロードされた画像", use_column_width=True)
            
            # 分析タイプ選択
            analysis_type = st.selectbox(
                "🔍 分析タイプ",
                ["詳細説明", "テキスト抽出", "UI要素分析", "エラー検出", "オブジェクト認識"],
                key="analysis_type"
            )
            
            prompts = {
                "詳細説明": "この画像について詳細に説明してください",
                "テキスト抽出": "この画像からすべてのテキストを抽出してください",
                "UI要素分析": "この画面のUI要素（ボタン、メニュー、入力フィールドなど）を分析してください",
                "エラー検出": "この画像にエラーメッセージや警告、問題点がないか確認してください",
                "オブジェクト認識": "この画像に含まれるオブジェクトをすべてリストアップしてください"
            }
            
            if st.button("👁️ llama3.2-visionで分析", type="primary"):
                # 一時ファイルに保存
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # llama3.2-visionで分析
                with st.spinner("👁️ llama3.2-visionで分析中..."):
                    response = ai_system.ollama_client.generate(
                        model=Config.VISION_MODEL,
                        prompt=prompts[analysis_type],
                        images=[tmp_file_path],
                        options={
                            "temperature": 0.7,
                            "max_tokens": Config.MAX_TOKENS_FULL
                        }
                    )
                
                st.subheader("📊 llama3.2-vision 分析結果")
                st.write(response['response'])
                
                # 一時ファイル削除
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
    
    # フッター情報
    st.markdown("---")
    st.markdown(f"**🚀 llama3.2シリーズ**: {Config.MAIN_MODEL} + {Config.VISION_MODEL}")
    st.markdown(f"**最終更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**🎯 目標**: 速く・正確に・何でも見える最強のAIエージェント")

if __name__ == "__main__":
    main()
