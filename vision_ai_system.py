#!/usr/bin/env python3
"""
AI Agent System - ビジョンAI統合システム
llama3.2-visionモデルと画面認識を統合した高度なAIシステム
"""

import streamlit as st
import ollama
import pyautogui
import tempfile
import os
import time
from datetime import datetime
from PIL import Image
import io
import base64
import json

class VisionAISystem:
    """ビジョンAI統合システム"""
    
    def __init__(self):
        self.ollama_client = None
        self.vision_model = "llama3.2-vision"
        self.text_model = "llama3.1:8b"
        self.current_mode = "text"  # text, vision, hybrid
        
    def initialize(self):
        """システム初期化"""
        try:
            self.ollama_client = ollama.Client()
            return True
        except Exception as e:
            st.error(f"❌ ビジョンAIシステム初期化エラー: {str(e)}")
            return False
    
    def capture_screen(self, save_temp=True):
        """画面キャプチャ取得"""
        try:
            screenshot = pyautogui.screenshot()
            
            if save_temp:
                # 一時ファイルとして保存
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_path = f"temp_screenshot_{timestamp}.png"
                screenshot.save(temp_path)
                return temp_path, screenshot
            else:
                return None, screenshot
                
        except Exception as e:
            st.error(f"❌ 画面キャプチャエラー: {str(e)}")
            return None, None
    
    def image_to_base64(self, image_path):
        """画像をbase64に変換"""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            st.error(f"❌ 画像変換エラー: {str(e)}")
            return None
    
    def analyze_screen_with_vision(self, prompt="この画面について詳細に説明してください"):
        """ビジョンモデルで画面分析"""
        try:
            # 画面キャプチャ取得
            temp_path, screenshot = self.capture_screen()
            
            if temp_path is None:
                return "画面キャプチャの取得に失敗しました"
            
            # ビジョンモデルで分析
            with st.spinner("🔍 ビジョンAIで画面分析中..."):
                response = self.ollama_client.generate(
                    model=self.vision_model,
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
    
    def analyze_image_file(self, image_file, prompt="この画像について詳細に説明してください"):
        """アップロードされた画像ファイルを分析"""
        try:
            with st.spinner("🔍 ビジョンAIで画像分析中..."):
                response = self.ollama_client.generate(
                    model=self.vision_model,
                    prompt=prompt,
                    images=[image_file]
                )
            
            return response['response']
            
        except Exception as e:
            return f"❌ 画像分析エラー: {str(e)}"
    
    def hybrid_analysis(self, prompt, image_path=None):
        """ハイブリッド分析（テキスト+画像）"""
        try:
            # 画像がない場合は画面キャプチャ
            if image_path is None:
                image_path, _ = self.capture_screen()
            
            if image_path is None:
                return "画面キャプチャの取得に失敗しました"
            
            with st.spinner("🧠 ハイブリッドAI分析中..."):
                response = self.ollama_client.generate(
                    model=self.vision_model,
                    prompt=f"以下の画像とテキスト情報を統合して回答してください:\n\nテキスト: {prompt}\n\n画像:",
                    images=[image_path]
                )
            
            # 一時ファイル削除
            try:
                if os.path.exists(image_path) and "temp_screenshot" in image_path:
                    os.unlink(image_path)
            except:
                pass
            
            return response['response']
            
        except Exception as e:
            return f"❌ ハイブリッド分析エラー: {str(e)}"
    
    def extract_text_from_screen(self):
        """画面からテキスト抽出（OCR機能）"""
        try:
            temp_path, _ = self.capture_screen()
            
            if temp_path is None:
                return "画面キャプチャの取得に失敗しました"
            
            ocr_prompt = """この画像からすべてのテキスト情報を抽出してください。
            読めるテキストを正確に、フォーマットを保って出力してください。
            ボタン、ラベル、メニュー項目、エラーメッセージなど、すべてのテキストを含めてください。"""
            
            with st.spinner("📝 画面からテキスト抽出中..."):
                response = self.ollama_client.generate(
                    model=self.vision_model,
                    prompt=ocr_prompt,
                    images=[temp_path]
                )
            
            # 一時ファイル削除
            try:
                os.unlink(temp_path)
            except:
                pass
            
            return response['response']
            
        except Exception as e:
            return f"❌ テキスト抽出エラー: {str(e)}"
    
    def analyze_ui_elements(self):
        """UI要素の分析"""
        try:
            temp_path, _ = self.capture_screen()
            
            if temp_path is None:
                return "画面キャプチャの取得に失敗しました"
            
            ui_prompt = """この画面のUI要素を詳細に分析してください：
            1. すべてのボタンとそのラベル
            2. メニュー項目と階層構造
            3. 入力フィールドとプレースホルダーテキスト
            4. エラーメッセージや警告
            5. ナビゲーション要素
            6. 全体的なレイアウト構造
            
            可能な限り詳細に、構造化して報告してください。"""
            
            with st.spinner("🎨 UI要素分析中..."):
                response = self.ollama_client.generate(
                    model=self.vision_model,
                    prompt=ui_prompt,
                    images=[temp_path]
                )
            
            # 一時ファイル削除
            try:
                os.unlink(temp_path)
            except:
                pass
            
            return response['response']
            
        except Exception as e:
            return f"❌ UI分析エラー: {str(e)}"

def render_vision_interface():
    """ビジョンAIインターフェース"""
    st.header("👁️ ビジョンAIシステム")
    
    # モード選択
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📸 画面分析", type="primary"):
            vision_system.current_mode = "screen_analysis"
    
    with col2:
        if st.button("📝 テキスト抽出", type="primary"):
            vision_system.current_mode = "text_extraction"
    
    with col3:
        if st.button("🎨 UI要素分析", type="primary"):
            vision_system.current_mode = "ui_analysis"
    
    st.markdown("---")
    
    # カスタムプロンプト入力
    custom_prompt = st.text_area(
        "🔍 カスタム分析プロンプト",
        placeholder="画面についてどのような分析をしますか？",
        height=100,
        key="vision_prompt"
    )
    
    # 実行ボタン
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 画面を分析", type="primary", key="analyze_screen"):
            if custom_prompt:
                result = vision_system.analyze_screen_with_vision(custom_prompt)
            else:
                result = vision_system.analyze_screen_with_vision()
            
            st.subheader("📊 分析結果")
            st.write(result)
    
    with col2:
        if st.button("📝 テキストを抽出", type="primary", key="extract_text"):
            result = vision_system.extract_text_from_screen()
            st.subheader("📝 抽出結果")
            st.write(result)
    
    # UI要素分析
    if st.button("🎨 UI要素を分析", type="primary", key="analyze_ui"):
        result = vision_system.analyze_ui_elements()
        st.subheader("🎨 UI要素分析結果")
        st.write(result)
    
    # 画像ファイルアップロード分析
    st.markdown("---")
    st.subheader("📁 画像ファイル分析")
    
    uploaded_file = st.file_uploader(
        "画像ファイルを選択",
        type=['png', 'jpg', 'jpeg', 'bmp', 'gif'],
        key="vision_image_file"
    )
    
    if uploaded_file:
        # 画像プレビュー
        image = Image.open(uploaded_file)
        st.image(image, caption="アップロードされた画像", use_column_width=True)
        
        # 分析プロンプト
        image_prompt = st.text_area(
            "🔍 画像分析プロンプト",
            placeholder="この画像についてどのような分析をしますか？",
            height=100,
            key="image_prompt",
            value="この画像について詳細に説明してください"
        )
        
        if st.button("🔍 画像を分析", type="primary", key="analyze_image"):
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            result = vision_system.analyze_image_file(tmp_file_path, image_prompt)
            st.subheader("📊 画像分析結果")
            st.write(result)
            
            # 一時ファイル削除
            try:
                os.unlink(tmp_file_path)
            except:
                pass

def render_hybrid_interface():
    """ハイブリッドインターフェース"""
    st.header("🧠 ハイブリッドAI分析")
    
    # 画面キャプチャとテキストの統合分析
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 画面キャプチャ")
        if st.button("📸 画面をキャプチャ", key="capture_for_hybrid"):
            temp_path, screenshot = vision_system.capture_screen(save_temp=False)
            if screenshot:
                st.session_state.hybrid_image = screenshot
                st.success("✅ 画面キャプチャ完了")
                st.image(screenshot, caption="キャプチャした画面", use_column_width=True)
    
    with col2:
        st.subheader("💬 テキスト入力")
        hybrid_prompt = st.text_area(
            "💬 分析テキスト",
            placeholder="画面についてどのような質問や指示がありますか？",
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
            
            result = vision_system.hybrid_analysis(hybrid_prompt, tmp_file_path)
            st.subheader("🧠 ハイブリッド分析結果")
            st.write(result)
            
            # 一時ファイル削除
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        else:
            st.warning("⚠️ 画面キャプチャとテキストの両方が必要です")

def render_quick_actions():
    """クイックアクション"""
    st.header("⚡ クイックアクション")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📸 画面を説明", key="quick_describe"):
            result = vision_system.analyze_screen_with_vision("この画面を簡潔に説明してください")
            st.info("📊 画面説明:")
            st.write(result)
    
    with col2:
        if st.button("❌ エラーを検出", key="quick_error"):
            error_prompt = """この画面にエラーメッセージ、警告、問題点がないか確認してください。
            赤い文字、エラーアイコン、警告メッセージ、異常な表示などに注目してください。"""
            result = vision_system.analyze_screen_with_vision(error_prompt)
            st.info("🚨 エラー検出結果:")
            st.write(result)
    
    with col3:
        if st.button("💡 操作手順を説明", key="quick_instructions"):
            instruction_prompt = """この画面の操作方法や手順をステップバイステップで説明してください。
            ボタンのクリック順序、入力フィールドの使い方、ナビゲーション方法などを詳細に教えてください。"""
            result = vision_system.analyze_screen_with_vision(instruction_prompt)
            st.info("📋 操作手順:")
            st.write(result)

def main():
    """メイン処理"""
    st.set_page_config(
        page_title="👁️ Vision AI System",
        page_icon="👁️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("👁️ AI Agent Vision System")
    st.markdown("### 🚀 llama3.2-vision + 画面認識の統合")
    
    # グローバル変数初期化
    if 'vision_system' not in st.session_state:
        st.session_state.vision_system = VisionAISystem()
        if st.session_state.vision_system.initialize():
            st.success("✅ ビジョンAIシステム初期化完了")
        else:
            st.error("❌ ビジョンAIシステム初期化失敗")
            st.stop()
    
    vision_system = st.session_state.vision_system
    
    # サイドバー情報
    with st.sidebar:
        st.header("👁️ ビジョンAI設定")
        
        st.write(f"**ビジョンモデル**: {vision_system.vision_model}")
        st.write(f"**テキストモデル**: {vision_system.text_model}")
        
        # モデル情報
        try:
            models = vision_system.ollama_client.list()
            vision_models = [m['name'] for m in models if 'vision' in m['name'].lower()]
            st.write("**利用可能なビジョンモデル**:")
            for model in vision_models:
                st.write(f"- {model}")
        except:
            st.write("❌ モデル情報取得エラー")
        
        st.markdown("---")
        st.subheader("📊 利用統計")
        
        # 簡単な統計表示（実際の実装ではDBに保存）
        st.metric("分析実行回数", "0")
        st.metric("テキスト抽出回数", "0")
        st.metric("UI分析回数", "0")
    
    # メインタブ
    tab1, tab2, tab3 = st.tabs(["👁️ ビジョンAI", "🧠 ハイブリッド分析", "⚡ クイックアクション"])
    
    with tab1:
        render_vision_interface()
    
    with tab2:
        render_hybrid_interface()
    
    with tab3:
        render_quick_actions()
    
    # フッター情報
    st.markdown("---")
    st.markdown(f"**最終更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**🚀 llama3.2-visionモデルで高度な画像認識を実現**")

if __name__ == "__main__":
    main()
