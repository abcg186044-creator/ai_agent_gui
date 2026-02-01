#!/usr/bin/env python3
"""
AI Agent System - ビジョン機能強化版アプリケーション
llama3.2-visionを統合した完全なAIアシスタントシステム
"""

import streamlit as st
import sys
import os
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path

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

# 設定
class Config:
    VISION_MODEL = "llama3.2-vision"
    TEXT_MODEL = "llama3.2"  # 基本llama3.2モデルを使用
    OLLAMA_HOST = "localhost"
    OLLAMA_PORT = 11434
    VOICE_RATE = 200
    VOICE_VOLUME = 0.9

class EnhancedAISystem:
    """強化AIシステム"""
    
    def __init__(self):
        self.ollama_client = None
        self.whisper_model = None
        self.tts_engine = None
        self.knowledge_db = None
        self.memory_data = None
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
            
            # 知識ベース初期化
            self.knowledge_db = chromadb.PersistentClient(path="./knowledge_base")
            
            # メモリDB初期化
            self.memory_data = self._load_memory_db()
            
            return True
        except Exception as e:
            st.error(f"❌ システム初期化エラー: {str(e)}")
            return False
    
    def _load_memory_db(self):
        """メモリDB読み込み"""
        try:
            if os.path.exists("./memory_db.json"):
                with open("./memory_db.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "conversations": [],
                    "user_profile": {
                        "name": None,
                        "os": None,
                        "tech_stack": [],
                        "preferences": [],
                        "projects": [],
                        "last_updated": None
                    },
                    "learning_data": {
                        "common_questions": [],
                        "preferred_responses": [],
                        "technical_level": "beginner"
                    }
                }
        except Exception:
            return {"conversations": [], "user_profile": {}, "learning_data": {}}
    
    def capture_and_analyze_screen(self, prompt="この画面について詳細に分析してください"):
        """画面キャプチャとビジョン分析"""
        try:
            with st.spinner("📸 画面キャプチャ中..."):
                screenshot = pyautogui.screenshot()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_path = f"temp_vision_{timestamp}.png"
                screenshot.save(temp_path)
            
            with st.spinner("👁️ ビジョンAI分析中..."):
                response = self.ollama_client.generate(
                    model=Config.VISION_MODEL,
                    prompt=prompt,
                    images=[temp_path]
                )
            
            # 一時ファイル削除
            try:
                os.unlink(temp_path)
            except:
                pass
            
            return response['response']
            
        except Exception as e:
            return f"❌ 画面分析エラー: {str(e)}"
    
    def analyze_uploaded_image(self, image_file, prompt):
        """アップロード画像の分析"""
        try:
            with st.spinner("👁️ 画像分析中..."):
                response = self.ollama_client.generate(
                    model=Config.VISION_MODEL,
                    prompt=prompt,
                    images=[image_file]
                )
            return response['response']
        except Exception as e:
            return f"❌ 画像分析エラー: {str(e)}"
    
    def extract_text_from_screen(self):
        """画面からテキスト抽出（OCR）"""
        try:
            ocr_prompt = """この画像からすべてのテキスト情報を抽出してください。
            読めるテキストを正確に、フォーマットを保って出力してください。
            ボタン、ラベル、メニュー項目、エラーメッセージなど、すべてのテキストを含めてください。"""
            
            return self.capture_and_analyze_screen(ocr_prompt)
        except Exception as e:
            return f"❌ テキスト抽出エラー: {str(e)}"
    
    def hybrid_analysis(self, text_prompt, image_path=None):
        """ハイブリッド分析（テキスト+画像）"""
        try:
            if image_path is None:
                with st.spinner("📸 画面キャプチャ中..."):
                    screenshot = pyautogui.screenshot()
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    image_path = f"temp_hybrid_{timestamp}.png"
                    screenshot.save(image_path)
            
            hybrid_prompt = f"以下の画像とテキスト情報を統合して回答してください:\n\nテキスト: {text_prompt}\n\n画像:"
            
            with st.spinner("🧠 ハイブリッドAI分析中..."):
                response = self.ollama_client.generate(
                    model=Config.VISION_MODEL,
                    prompt=hybrid_prompt,
                    images=[image_path]
                )
            
            # 一時ファイル削除
            try:
                if image_path and "temp_" in image_path:
                    os.unlink(image_path)
            except:
                pass
            
            return response['response']
            
        except Exception as e:
            return f"❌ ハイブリッド分析エラー: {str(e)}"
    
    def generate_text_response(self, prompt, context=""):
        """テキストのみの応答生成"""
        try:
            personality_prompts = {
                "friend": f"あなたは親友エンジニアとして、フレンドリーに{context}を考慮しながら答えてください。{prompt}",
                "copy": f"あなたはユーザーの分身として、{context}を背景に{prompt}に答えてください。",
                "expert": f"あなたは専門家として、提供された資料に基づき{context}を考慮しながら正確な回答を提供してください。{prompt}"
            }
            
            adjusted_prompt = personality_prompts.get(self.current_personality, prompt)
            
            response = self.ollama_client.generate(
                model=Config.TEXT_MODEL,
                prompt=adjusted_prompt,
                options={
                    "temperature": 0.7,
                    "max_tokens": 4096
                }
            )
            
            return response['response']
        except Exception as e:
            return f"❌ 応答生成エラー: {str(e)}"
    
    def text_to_speech(self, text):
        """音声合成"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            st.error(f"❌ 音声合成エラー: {str(e)}")
            return False

def render_main_interface():
    """メインインターフェース"""
    st.header("💬 AIアシスタント")
    
    # 会話履歴表示
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
    
    # 入力エリア
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        user_input = st.text_input(
            "メッセージを入力",
            placeholder="AIとの対話を開始...",
            key="user_input"
        )
    
    with col2:
        if st.button("📸 画面分析", help="現在の画面をAIで分析"):
            with st.spinner("画面分析中..."):
                result = ai_system.capture_and_analyze_screen()
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"📸 **画面分析結果**:\n\n{result}"
                })
                st.rerun()
    
    with col3:
        if st.button("📝 テキスト抽出", help="画面からテキストを抽出"):
            with st.spinner("テキスト抽出中..."):
                result = ai_system.extract_text_from_screen()
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"📝 **テキスト抽出結果**:\n\n{result}"
                })
                st.rerun()
    
    # 送信ボタン
    if st.button("💬 送信", type="primary"):
        if user_input:
            # ユーザーメッセージを保存
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # AI応答生成
            with st.spinner("AI応答生成中..."):
                context = ""
                if len(st.session_state.messages) > 1:
                    recent_messages = st.session_state.messages[-3:]
                    context = "最近の会話: " + " | ".join([msg["content"] for msg in recent_messages])
                
                ai_response = ai_system.generate_text_response(user_input, context)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            # 自動音声読み上げ
            if st.checkbox("🔊 音声読み上げ", value=True):
                ai_system.text_to_speech(ai_response)
            
            st.rerun()

def render_vision_interface():
    """ビジョンインターフェース"""
    st.header("👁️ ビジョンAI")
    
    # 画像ファイルアップロード
    uploaded_file = st.file_uploader(
        "📁 画像ファイルを選択",
        type=['png', 'jpg', 'jpeg', 'bmp', 'gif'],
        key="vision_image_file"
    )
    
    if uploaded_file:
        # 画像プレビュー
        image = Image.open(uploaded_file)
        st.image(image, caption="アップロードされた画像", use_column_width=True)
        
        # 分析プロンプト
        analysis_type = st.selectbox(
            "🔍 分析タイプ",
            ["詳細説明", "テキスト抽出", "UI要素分析", "エラー検出", "操作手順説明"],
            key="analysis_type"
        )
        
        prompts = {
            "詳細説明": "この画像について詳細に説明してください",
            "テキスト抽出": "この画像からすべてのテキストを抽出してください",
            "UI要素分析": "この画面のUI要素（ボタン、メニュー、入力フィールドなど）を分析してください",
            "エラー検出": "この画像にエラーメッセージや警告、問題点がないか確認してください",
            "操作手順説明": "この画面の操作方法をステップバイステップで説明してください"
        }
        
        custom_prompt = st.text_area(
            "🔍 カスタムプロンプト（オプション）",
            placeholder="上記の分析タイプ以外の独自のプロンプトを入力",
            height=100,
            key="custom_prompt"
        )
        
        # 分析実行
        final_prompt = custom_prompt if custom_prompt else prompts[analysis_type]
        
        if st.button("👁️ 画像を分析", type="primary"):
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            result = ai_system.analyze_uploaded_image(tmp_file_path, final_prompt)
            
            st.subheader("📊 画像分析結果")
            st.write(result)
            
            # 一時ファイル削除
            try:
                os.unlink(tmp_file_path)
            except:
                pass

def render_hybrid_interface():
    """ハイブリッドインターフェース"""
    st.header("🧠 ハイブリッド分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 画面キャプチャ")
        if st.button("📸 画面をキャプチャ", key="capture_hybrid"):
            with st.spinner("画面キャプチャ中..."):
                screenshot = pyautogui.screenshot()
                st.session_state.hybrid_image = screenshot
                st.success("✅ 画面キャプチャ完了")
                st.image(screenshot, caption="キャプチャした画面", use_column_width=True)
    
    with col2:
        st.subheader("💬 分析テキスト")
        hybrid_prompt = st.text_area(
            "💬 画面についての質問や指示",
            placeholder="キャプチャした画面についてどのような分析をしますか？",
            height=150,
            key="hybrid_prompt"
        )
    
    # ハイブリッド分析実行
    if st.button("🧠 ハイブリッド分析", type="primary", key="hybrid_analysis"):
        if 'hybrid_image' in st.session_state and hybrid_prompt:
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                screenshot = st.session_state.hybrid_image
                screenshot.save(tmp_file.name)
                tmp_file_path = tmp_file.name
            
            result = ai_system.hybrid_analysis(hybrid_prompt, tmp_file_path)
            
            st.subheader("🧠 ハイブリッド分析結果")
            st.write(result)
            
            # 一時ファイル削除
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        else:
            st.warning("⚠️ 画面キャプチャとテキストの両方が必要です")

def render_settings():
    """設定画面"""
    st.header("⚙️ 設定")
    
    # 人格選択
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
    
    # システム情報
    st.subheader("📊 システム情報")
    
    # CPUとメモリ使用量
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("CPU使用率", f"{cpu_percent}%")
    with col2:
        st.metric("メモリ使用率", f"{memory.percent}%")
    
    # モデル情報
    st.write(f"**ビジョンモデル**: {Config.VISION_MODEL}")
    st.write(f"**テキストモデル**: {Config.TEXT_MODEL}")
    
    try:
        models = ai_system.ollama_client.list()
        model_names = [model.get('name', 'Unknown') for model in models]
        st.write(f"**利用可能モデル**: {', '.join(model_names)}")
    except:
        st.write("❌ モデル情報取得エラー")

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="🤖 AI Agent Vision Enhanced",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 AI Agent System - Vision Enhanced")
    st.markdown("### 🚀 llama3.2-vision + 画面認識の完全統合")
    
    # システム初期化
    if 'ai_system' not in st.session_state:
        st.session_state.ai_system = EnhancedAISystem()
        if st.session_state.ai_system.initialize():
            st.success("✅ 強化AIシステム初期化完了")
        else:
            st.error("❌ 強化AIシステム初期化失敗")
            st.stop()
    
    global ai_system
    ai_system = st.session_state.ai_system
    
    # サイドバー
    with st.sidebar:
        render_settings()
    
    # メインタブ
    tab1, tab2, tab3 = st.tabs(["💬 AIアシスタント", "👁️ ビジョンAI", "🧠 ハイブリッド分析"])
    
    with tab1:
        render_main_interface()
    
    with tab2:
        render_vision_interface()
    
    with tab3:
        render_hybrid_interface()
    
    # フッター情報
    st.markdown("---")
    st.markdown(f"**最終更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**🚀 llama3.2-visionで高度な視覚的AI対話を実現**")

if __name__ == "__main__":
    main()
