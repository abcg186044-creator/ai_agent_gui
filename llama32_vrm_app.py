#!/usr/bin/env python3
"""
AI Agent System - llama3.2 + VRM 完全統合版
最新のllama3.2シリーズとVRMアバターを統合した最適化AIシステム
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
    
    # VRM設定
    VRM_MODELS_PATH = "./vrm_models"
    DEFAULT_VRM = "default_avatar.vrm"
    VRM_ANIMATIONS = ["idle", "talking", "thinking", "happy", "sad"]
    
    # 高速応答設定
    STREAMING_ENABLED = True
    FAST_RESPONSE_TIMEOUT = 2.0
    MAX_TOKENS_FAST = 512
    MAX_TOKENS_FULL = 4096

class VRMModel:
    """VRMモデル管理クラス"""
    
    def __init__(self):
        self.models_path = Config.VRM_MODELS_PATH
        self.available_models = []
        self.current_model = None
        self.current_expression = "neutral"
        self.current_animation = "idle"
        
        # VRMモデルディレクトリ作成
        os.makedirs(self.models_path, exist_ok=True)
        
        # サンプルVRMファイル作成
        self._create_sample_vrm()
        
    def _create_sample_vrm(self):
        """サンプルVRMファイルを作成"""
        sample_vrm_path = os.path.join(self.models_path, "default_avatar.vrm")
        
        if not os.path.exists(sample_vrm_path):
            # VRMファイルの基本構造（サンプル）
            vrm_content = """# VRM Model File
# This is a sample VRM model file
# In a real implementation, this would be a binary 3D model file

model_version: "1.0"
model_name: "Default Avatar"
model_author: "AI System"
model_contact: "https://github.com/ai-system"

# Avatar metadata
avatar:
  name: "AI Assistant"
  version: "1.0"
  
# Expressions
expressions:
  neutral: "通常"
  happy: "喜び"
  sad: "悲しみ"
  angry: "怒り"
  surprised: "驚き"
  thinking: "思考中"
  
# Animations
animations:
  idle: "待機"
  talking: "話している"
  thinking: "思考中"
  waving: "手を振っている"
  
# Model references
# In real implementation, these would reference actual 3D model files
model_files:
  mesh: "avatar.mesh"
  texture: "avatar.png"
  skeleton: "avatar.skeleton"
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
            # 表情とアニメーションを設定
            self.vrm_model.set_expression(expression)
            self.vrm_model.set_animation(animation)
            
            # レンダリング結果を生成（シミュレーション）
            render_result = self._simulate_rendering()
            
            return render_result
            
        except Exception as e:
            return {"error": str(e)}
    
    def _simulate_rendering(self):
        """レンダリングをシミュレート"""
        # 実際の実装では3Dレンダリングライブラリ（Three.jsなど）を使用
        # ここではシミュレーション結果を返す
        
        current_time = datetime.now().strftime('%H:%M:%S')
        
        return {
            "status": "success",
            "timestamp": current_time,
            "expression": self.vrm_model.current_expression,
            "animation": self.vrm_model.current_animation,
            "model_info": self.vrm_model.get_vrm_info(),
            "render_data": {
                "avatar_state": "active",
                "performance": "60 FPS",
                "quality": "high"
            }
        }
    
    def get_avatar_image(self):
        """アバター画像を取得（プレースホルダー）"""
        # 実際の実装ではレンダリングされた画像を返す
        # ここではプレースホルダー画像を生成
        
        # 表情に応じた絵文字
        expression_emoji = {
            "neutral": "😐",
            "happy": "😊",
            "sad": "😢",
            "angry": "😠",
            "surprised": "😲",
            "thinking": "🤔"
        }
        
        emoji = expression_emoji.get(self.vrm_model.current_expression, "😐")
        
        # 簡単なテキスト表現（実際には画像を生成）
        return f"""
        <div style="text-align: center; padding: 20px; font-size: 48px;">
            {emoji}
        </div>
        <div style="text-align: center; padding: 10px;">
            <strong>Expression:</strong> {self.vrm_model.current_expression}<br>
            <strong>Animation:</strong> {self.vrm_model.current_animation}<br>
            <strong>Time:</strong> {datetime.now().strftime('%H:%M:%S')}
        </div>
        """

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
                        "stream": False
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

class OptimizedAISystem:
    """llama3.2 + VRM 最適化AIシステム"""
    
    def __init__(self):
        self.ollama_client = None
        self.whisper_model = None
        self.tts_engine = None
        self.model_router = ModelRouter()
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
            
            # VRMレンダラー初期化
            self.vrm_renderer.initialize()
            
            return True
            
        except Exception as e:
            return False
    
    def generate_response(self, prompt, images=None, context="", fast_mode=False):
        """最適化された応答生成"""
        try:
            # モデル振り分け
            model, formatted_prompt = self.model_router.route_request(
                prompt, images, context, fast_mode
            )
            
            # VRM表情更新（思考中）
            self.vrm_renderer.render_avatar("thinking", "thinking")
            
            # 応答生成
            if Config.STREAMING_ENABLED and not images:
                streaming = StreamingResponse(model, formatted_prompt, images)
                
                # バックグラウンドで実行
                thread = threading.Thread(target=streaming.generate_streaming)
                thread.start()
                
                # 応答取得
                response = streaming.get_response()
                thread.join(timeout=30)
                
                # VRM表情更新（話し中）
                self.vrm_renderer.render_avatar("happy", "talking")
                
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
                
                # VRM表情更新（喜び）
                self.vrm_renderer.render_avatar("happy", "talking")
                
                return response['response']
                
        except Exception as e:
            # VRM表情更新（悲しみ）
            self.vrm_renderer.render_avatar("sad", "idle")
            return f"❌ 応答生成エラー: {str(e)}"
    
    def analyze_screen_with_vision(self, prompt="この画面について詳細に分析してください"):
        """ビジョンモデルで画面分析"""
        try:
            # VRM表情更新（思考中）
            self.vrm_renderer.render_avatar("thinking", "thinking")
            
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
            
            # VRM表情更新（驚き）
            self.vrm_renderer.render_avatar("surprised", "idle")
            
            # 一時ファイル削除
            try:
                os.unlink(temp_path)
            except:
                pass
            
            return response['response']
            
        except Exception as e:
            # VRM表情更新（悲しみ）
            self.vrm_renderer.render_avatar("sad", "idle")
            return f"❌ 画面分析エラー: {str(e)}"
    
    def text_to_speech(self, text):
        """音声合成"""
        try:
            # VRM表情更新（話し中）
            self.vrm_renderer.render_avatar("happy", "talking")
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            # VRM表情更新（通常）
            self.vrm_renderer.render_avatar("neutral", "idle")
            
            return True
        except Exception as e:
            st.error(f"❌ 音声合成エラー: {str(e)}")
            return False
    
    def get_vrm_display(self):
        """VRM表示データを取得"""
        return self.vrm_renderer.get_avatar_image()

def render_vrm_interface(ai_system):
    """VRMインターフェース"""
    st.header("👤 VRMアバター")
    
    # VRM情報表示
    vrm_info = ai_system.vrm_renderer.vrm_model.get_vrm_info()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("利用可能モデル", vrm_info["available_models"])
    
    with col2:
        st.metric("現在の表情", vrm_info["current_expression"])
    
    with col3:
        st.metric("現在のアニメ", vrm_info["current_animation"])
    
    # VRM表示
    st.subheader("👤 アバター表示")
    vrm_display = ai_system.get_vrm_display()
    st.markdown(vrm_display, unsafe_allow_html=True)
    
    # 表情コントロール
    st.subheader("😊 表情コントロール")
    
    expressions = ["neutral", "happy", "sad", "angry", "surprised", "thinking"]
    expression_labels = {
        "neutral": "😐 通常",
        "happy": "😊 喜び",
        "sad": "😢 悲しみ",
        "angry": "😠 怒り",
        "surprised": "😲 驚き",
        "thinking": "🤔 思考中"
    }
    
    cols = st.columns(3)
    for i, (expr, label) in enumerate(expression_labels.items()):
        with cols[i % 3]:
            if st.button(f"{label}", key=f"expr_{expr}"):
                ai_system.vrm_renderer.render_avatar(expr, "idle")
                st.success(f"表情を「{label}」に変更しました")
                st.rerun()
    
    # アニメーションコントロール
    st.subheader("🎬 アニメーション")
    
    animations = Config.VRM_ANIMATIONS
    animation_labels = {
        "idle": "😴 待機",
        "talking": "💬 話している",
        "thinking": "🤔 思考中",
        "happy": "😊 喜んでいる"
    }
    
    cols = st.columns(2)
    for i, (anim, label) in enumerate(animation_labels.items()):
        with cols[i % 2]:
            if st.button(f"{label}", key=f"anim_{anim}"):
                ai_system.vrm_renderer.render_avatar("neutral", anim)
                st.success(f"アニメーションを「{label}」に変更しました")
                st.rerun()

def render_main_interface(ai_system):
    """メインインターフェース"""
    st.header("💬 llama3.2 + VRM AIアシスタント")
    
    # 会話履歴
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
    
    # VRM表示をサイドに配置
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 入力エリア
        user_input = st.text_input(
            "💬 メッセージを入力",
            placeholder="llama3.2 + VRMとの対話を開始...",
            key="user_input"
        )
        
        # ボタン群
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            send_button = st.button("💬 送信", type="primary")
        
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
            fast_mode = st.checkbox("⚡ 高速モード", help="短い応答を優先")
        
        with col4:
            auto_speech = st.checkbox("🔊 音声読み上げ", value=True, help="応答を音声で読み上げ")
        
        # 送信処理
        if send_button and user_input:
            # ユーザーメッセージを保存
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # AI応答生成
            with st.spinner("🤖 llama3.2 + VRMで応答生成中..."):
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
        st.subheader("👤 アバター")
        vrm_display = ai_system.get_vrm_display()
        st.markdown(vrm_display, unsafe_allow_html=True)

def render_settings(ai_system):
    """設定画面"""
    st.header("⚙️ llama3.2 + VRM 設定")
    
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
    
    # VRM設定
    st.subheader("👤 VRM設定")
    vrm_info = ai_system.vrm_renderer.vrm_model.get_vrm_info()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**VRMモデルパス**: {vrm_info['models_path']}")
        st.write(f"**利用可能モデル数**: {vrm_info['available_models']}")
        
        # VRMモデルアップロード
        uploaded_vrm = st.file_uploader(
            "📁 VRMモデルをアップロード",
            type=['vrm'],
            key="vrm_upload"
        )
        
        if uploaded_vrm:
            # VRMファイルを保存
            save_path = os.path.join(vrm_info['models_path'], uploaded_vrm.name)
            with open(save_path, 'wb') as f:
                f.write(uploaded_vrm.getvalue())
            st.success(f"VRMモデルを「{uploaded_vrm.name}」として保存しました")
    
    with col2:
        # VRMステータス
        st.write("**現在のステータス**:")
        st.write(f"- 表情: {vrm_info['current_expression']}")
        st.write(f"- アニメーション: {vrm_info['current_animation']}")
        
        # 表情プレビュー
        if st.button("🔄 表情をリセット", key="reset_expression"):
            ai_system.vrm_renderer.render_avatar("neutral", "idle")
            st.success("表情をリセットしました")
            st.rerun()

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="👤 llama3.2 + VRM AI System",
        page_icon="👤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("👤 AI Agent System - llama3.2 + VRM 完全統合版")
    st.markdown("### 🚀 llama3.2 + VRMで次世代のAI体験")
    
    # システム初期化
    if 'ai_system' not in st.session_state:
        with st.spinner("🚀 llama3.2 + VRM AIシステム初期化中..."):
            ai_system = OptimizedAISystem()
            if ai_system.initialize():
                st.session_state.ai_system = ai_system
                st.success("✅ llama3.2 + VRM AIシステム初期化完了")
            else:
                st.error("❌ AIシステム初期化失敗")
                st.stop()
    
    ai_system = st.session_state.ai_system
    
    # サイドバー
    with st.sidebar:
        render_settings(ai_system)
    
    # メインタブ
    tab1, tab2, tab3 = st.tabs(["💬 AIアシスタント", "👤 VRMアバター", "👁️ ビジョン機能"])
    
    with tab1:
        render_main_interface(ai_system)
    
    with tab2:
        render_vrm_interface(ai_system)
    
    with tab3:
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
    st.markdown(f"**🚀 llama3.2 + VRM**: {Config.MAIN_MODEL} + {Config.VISION_MODEL}")
    st.markdown(f"**最終更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**🎯 目標**: 速く・正確に・何でも見える・感情表現も可能な最強のAIエージェント")

if __name__ == "__main__":
    main()
